#!/usr/bin/env python3
"""TCTE official-question PDF extractor. Preserves uncertainty; never invents an answer.
Run from repository root. Writes sudu/data/years/<year>.json, only from official sources.
"""
import argparse, base64, bisect, datetime, hashlib, json, os, re, sys, time
from pathlib import Path
from urllib.parse import urljoin, urlparse, parse_qs
import requests
from bs4 import BeautifulSoup
import fitz

ROOT=Path(__file__).resolve().parent.parent
OUT=ROOT/"sudu"/"data"/"years"
DOMAIN={"web1.tcte.edu.tw"}
HEADERS={"User-Agent":"Mozilla/5.0 (compatible; TCTE-exam-education/1.0; +https://www.tcte.edu.tw/)"}
S=requests.Session()
S.headers.update(HEADERS)
QSTART=re.compile(r"(?m)^[ \t]*(\d{1,3})[.．、][ \t]*(?=\S)")
OPT=re.compile(r"\(\s*([A-D])\s*\)")
YEAR_PATTERN=re.compile(r"(\d{2,3})-4y-(.+?)(?:-standard)?\.pdf$",re.I)
GROUP_CODES={"09-1":"專業科目（一）","09-2":"專業科目（二）","00-C":"國文","00-E":"英文","00-MB":"數學 B"}
OPTION_NAMES={"09-1","09-2","00-C","00-E","00-MB"}
BOOK_NEEDS_REVIEW=re.compile(r"如[圖表]|表[（(]|圖[（(]|參[閱考]下[圖表]|依下[列圖表]|附[圖表]|附表|下圖|下表|依據.*圖|下列.*[圖表]|以下資料|矩陣|會計項目資訊如表")
VERSION=3

def stamp():return datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")
def guarded_get(url,timeout=35):
    x=urlparse(url)
    if x.scheme!="https" or x.hostname not in DOMAIN:raise ValueError("Untrusted official source: "+url)
    for i in range(3):
        try:
            r=S.get(url,timeout=timeout)
            r.raise_for_status()
            if len(r.content)>35_000_000:raise ValueError("PDF >35MB")
            return r
        except (requests.Timeout,requests.ConnectionError) as e:
            if i==2:raise
            time.sleep(2+i*2)
    raise RuntimeError(url)

def year_url(year):
    # Legacy years use 3-digit 090_4y, not 90_4y.
    if year<100:return f"https://web1.tcte.edu.tw/EXAM/{year:03d}_4y/"
    return f"https://web1.tcte.edu.tw/EXAM/{year}_4y/"

def decoded_input_links(html,url):
    """Official year page stores PDF filenames in base64 downloader.php?obj=."""
    matches={}
    for tag in BeautifulSoup(html,"html.parser").select("input[onclick]"):
        onclick=tag.get("onclick","")
        m=re.search(r"downloader\.php\?obj=([A-Za-z0-9+/=]+)",onclick)
        if not m:continue
        try:fn=base64.b64decode(m.group(1)).decode("utf-8")
        except Exception:continue
        if not fn.lower().endswith(".pdf"):continue
        if "-confirm" in fn.lower() or "-feature" in fn.lower() or "-guide" in fn.lower() or "-grade" in fn.lower():continue
        if any(s in fn.lower() for s in ["-answer","-standard","-ans"]):kind="answer"
        else:kind="exam"
        # Match official 09 and all common subjects; older years may have another math code.
        m2=re.search(r"(?:^|-4y-)(09-[12]|00-[A-Za-z0-9]+)(?:-standard|-answer|-ans)?\.pdf$",fn,re.I)
        if not m2:continue
        paper=m2.group(1).upper()
        if paper not in OPTION_NAMES and not paper.startswith("00-M"):continue
        key=(paper,kind)
        if key in matches:continue
        full=urljoin(url,"downloader.php?obj="+m.group(1))
        matches[key]={"filename":fn,"url":full,"kind":kind,"paper":paper}
    return list(matches.values())

def legacy_links(html,url):
    """Legacy 090-099 use links instead of downloader inputs. Do not label as modern 09."""
    soup=BeautifulSoup(html,"html.parser")
    links=[]
    for a in soup.find_all("a",href=True):
        href=urljoin(url,a["href"])
        if urlparse(href).hostname not in DOMAIN or not href.lower().split("?")[0].endswith(".pdf"):continue
        txt=(a.get_text(" ",strip=True)+" "+a.parent.get_text(" ",strip=True)).replace(" ","")
        paper=None
        if "商業類專一" in txt or "商業類專業科目(一)" in txt:paper="BIZ-1"
        if "商業類專二" in txt or "商業類專業科目(二)" in txt:paper="BIZ-2"
        if "共同科國文" in txt:paper="00-C"
        if "共同科英文" in txt:paper="00-E"
        if "共同科數學" in txt:paper="00-M-OLD"
        if paper:
            links.append({"filename":href.split("/")[-1],"url":href,"kind":"exam","paper":paper})
    return list({(x["paper"],x["url"]):x for x in links}.values())

def pdf_text(pdf_bytes):
    doc=fitz.open(stream=pdf_bytes,filetype="pdf")
    out=[]
    ocr_pages=[]
    for ix,page in enumerate(doc):
        text=page.get_text(sort=True)
        meaningful=re.sub(r"\s+","",text)
        if len(meaningful)<30 and os.getenv("TCTE_ENABLE_OCR","1")=="1":
            try:
                from PIL import Image
                import pytesseract,io
                image=Image.open(io.BytesIO(page.get_pixmap(matrix=fitz.Matrix(2.3,2.3),alpha=False).tobytes("png")))
                text=pytesseract.image_to_string(image,lang="chi_tra+eng")
                ocr_pages.append(ix+1)
            except Exception as exc:print(f"OCR_FAILURE page {ix+1}: {str(exc)[:120]}")
        out.append(text)
    return out,ocr_pages

def clean(segment):
    segment=re.sub(r"(?m)^\s*(?:\d{2,3}\s*年四技|商業與管理群\s*專業科目|公告試題僅供參考|共\s*\d+\s*頁|第\s*\d+\s*頁)\s*$","",segment)
    segment=segment.replace("\u02c9","").replace("\x00","")
    return segment.strip()

def parse_question_options(raw):
    m=list(OPT.finditer(raw))
    sequence=None
    for i,x in enumerate(m):
        if x.group(1)!="A":continue
        seq=[x]
        for c in "BCD":
            last=seq[-1]
            nxt=next((a for a in m if a.start()>last.start() and a.group(1)==c),None)
            if nxt is None:break
            seq.append(nxt)
        if len(seq)==4:
            sequence=seq
            break
    if not sequence:return clean(raw),[],["missing_A_to_D_options"]
    pos=sequence[0].start()
    stem=clean(raw[:pos])
    opts=[clean(raw[a.end():sequence[i+1].start()] if i<3 else raw[a.end():]) for i,a in enumerate(sequence)]
    warnings=[]
    if len(stem)<9:warnings.append("short_question")
    if any(len(x)<1 for x in opts):warnings.append("blank_option")
    if max([len(x) for x in opts]+[0])>850:warnings.append("long_option_or_broken_layout")
    if BOOK_NEEDS_REVIEW.search(stem):warnings.append("figure_or_table_recheck_pdf")
    if "\ufffd" in raw:warnings.append("replacement_character")
    return stem,opts,warnings

def extract_questions(pages,year,paper,src,ocr_pages):
    offsets=[];full=""; 
    for i,text in enumerate(pages):
        offsets.append(len(full))
        full+=text+"\n\n"
    markers=list(QSTART.finditer(full))
    # Skip cover-page lists and normalize against ascending number sequence.
    found={}
    for i,m in enumerate(markers):
        number=int(m.group(1))
        if number<1 or number>100:continue
        if number in found:continue
        end=markers[i+1].start() if i+1<len(markers) else len(full)
        raw=full[m.end():end]
        pg=bisect.bisect_right(offsets,m.start())
        if len(raw)>7000 or len(raw)<12:continue
        stem,options,warnings=parse_question_options(raw)
        if not stem:continue
        if len(options)!=4:warnings.append("missing_complete_options")
        if pg in ocr_pages:warnings.append("ocr_not_manually_verified")
        if not options and number>2 and number not in found:continue
        qid=f"{year}-{paper}-{number:02d}"
        # Never pretend a machine read is a confirmed textbook reference.
        found[number]={
            "id":qid,"year":year,"paper":paper,"number":number,
            "subject":GROUP_CODES.get(paper,paper),
            "kind":"官方歷屆題（自動擷取、待審核）",
            "question":stem,"options":options,
            "answer":None,"answerVerified":False,
            "explanation":"","principle":"","steps":"","wrongOptions":[],
            "extension":"","practice":None,"textbook":None,"teachingVerified":False,
            "source":src,"official":True,"page":pg,
            "issues":warnings,"ocrUsed":pg in ocr_pages,
            "questionVerified":False
        }
    return [found[n] for n in sorted(found)]

def parse_answers(pages):
    text="\n".join(pages)
    # TCTE answer PDF is tabular (multiple number-letter pairs per visual row).
    cleaned=re.sub(r"\s*公告\s*"," ",text)
    result,conflicts={},set()
    for m in re.finditer(r"(?<!\d)(\d{1,3})[ \t]+([A-D])(?=\s|$)",cleaned):
        n=int(m.group(1));a=m.group(2)
        if n<1 or n>100:continue
        if n in result and result[n]!=a:conflicts.add(n)
        else:result[n]=a
    for n in conflicts:result.pop(n,None)
    return result,sorted(conflicts)

def expected_count_from_cover(pages):
    cover=" ".join(pages[:2])
    nums=re.findall(r"(?:共|總計)\s*(\d{1,3})\s*題",cover)
    return int(nums[0]) if nums else None

def process_one(year,link,answer_link):
    code=link["paper"];issues=[]
    entry={"paper":code,"subject":GROUP_CODES.get(code,code),"questionPdf":link["url"],
           "answerPdf":answer_link["url"] if answer_link else None,"status":"needs_review",
           "questions":[],"discoveredCount":0,"answerCount":0,"expectedCount":None,"issues":issues}
    try:
        raw=guarded_get(link["url"],60).content
        if raw[:4]!=b"%PDF":raise ValueError("Official question response not PDF")
        pages,ocr=pdf_text(raw)
        q=extract_questions(pages,year,code,link["url"],ocr)
        entry["expectedCount"]=expected_count_from_cover(pages)
        entry["questions"]=q
        entry["discoveredCount"]=len(q)
        if not q:issues.append("no_readable_questions")
        if ocr:issues.append("ocr_pages_"+",".join(map(str,ocr)))
        if answer_link:
            ar=guarded_get(answer_link["url"],60).content
            if ar[:4]!=b"%PDF":raise ValueError("Official answer response not PDF")
            ap,ao=pdf_text(ar)
            answers,conflicts=parse_answers(ap)
            entry["answerCount"]=len(answers)
            if conflicts:issues.append("answer_conflicts_"+str(conflicts[:15]))
            for item in q:
                ans=answers.get(item["number"])
                if ans is not None:
                    item["answer"]="ABCD".index(ans)
                    # Official answer verified as match to the standard-answer PDF by number.
                    item["answerVerified"]=True
            if len(answers)<len(q):issues.append("incomplete_answer_pdf_extraction")
        else:issues.append("official_answer_pdf_not_identified")
        if entry["expectedCount"] is not None and len(q)!=entry["expectedCount"]:
            issues.append(f"expected_{entry['expectedCount']}_found_{len(q)}")
        if q:
            numbers=[x["number"] for x in q]
            if numbers!=list(range(1,max(numbers)+1)):issues.append("missing_nonconsecutive_questions")
        entry["status"]="parsed_pending_teaching" if q else "needs_review"
    except Exception as exc:
        entry["status"]="download_or_parse_failed"
        issues.append(type(exc).__name__+": "+str(exc)[:260])
    # Strictly complete means no missing questions AND all answer confirmations AND approved teaching.
    entry["complete"]=bool(entry["expectedCount"] and len(entry["questions"])==entry["expectedCount"]
          and all(q["answerVerified"] and q["questionVerified"] and q["teachingVerified"] for q in entry["questions"]))
    return entry

def process_year(y):
    entry={"year":y,"courseType":"09商管群" if y>=100 else "舊制商業類（不可直接當作09商管群）",
           "sourceIndex":year_url(y),"generatedAt":stamp(),"pipelineVersion":VERSION,"papers":[],"errors":[]}
    try:
        base=year_url(y)
        response=guarded_get(base)
        # 90–99 old sites have direct links and often HTML answer keys, which require different parser.
        if y<100:
            links=legacy_links(response.text,base)
            if not links:
                entry["errors"].append("舊制官網來源格式不同，需人工確認年份與商業類考卷的連結；未偽造09考卷。")
            entry["discoveredPdfLinks"]=len(links)
        else:
            links=decoded_input_links(response.text,base)
            entry["discoveredPdfLinks"]=len(links)
        exams=[p for p in links if p["kind"]=="exam"]
        answers={p["paper"]:p for p in links if p["kind"]=="answer"}
        # Restrict to 09 professional and common subjects for this platform.
        exams=[e for e in exams if e["paper"] in OPTION_NAMES or (y<100 and e["paper"] in {"BIZ-1","BIZ-2","00-M-OLD"})]
        # Old math versions are distinct. Do not silently choose one among several.
        for x in exams:
            entry["papers"].append(process_one(y,x,answers.get(x["paper"])))
        if not exams:entry["errors"].append("未找到對應試題 PDF；官方來源版型或代碼需再擴充。")
    except Exception as exc:
        entry["errors"].append(type(exc).__name__+": "+str(exc)[:280])
    entry["papersFound"]=len(entry["papers"])
    entry["questionsFound"]=sum(len(p["questions"]) for p in entry["papers"])
    entry["officialAnswersMatched"]=sum(sum(bool(q["answerVerified"]) for q in p["questions"]) for p in entry["papers"])
    entry["teachingReviewed"]=sum(sum(bool(q["teachingVerified"]) for q in p["questions"]) for p in entry["papers"])
    entry["fullyCompletedPapers"]=sum(p.get("complete",False) for p in entry["papers"])
    return entry

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--years",nargs="+",type=int,required=True)
    args=parser.parse_args()
    OUT.mkdir(parents=True,exist_ok=True)
    for y in args.years:
        if not 90<=y<=115:raise ValueError("Year outside 90–115")
        dest=OUT/(str(y)+".json")
        obj=process_year(y)
        # Keep the previous better extraction if the official website fails temporarily.
        if dest.exists():
            try:
                old=json.loads(dest.read_text(encoding="utf-8"))
                if old.get("questionsFound",0)>obj["questionsFound"]:
                    print("KEEP_PREVIOUS_BETTER",y,old["questionsFound"],obj["questionsFound"],flush=True)
                    continue
            except Exception:pass
        dest.write_text(json.dumps(obj,ensure_ascii=False,separators=(",",":")),encoding="utf-8")
        print("YEAR_RESULT",json.dumps({k:obj[k] for k in ["year","papersFound","questionsFound","officialAnswersMatched","fullyCompletedPapers","errors"]},ensure_ascii=False),flush=True)
        for p in obj["papers"]:
            print("PAPER_RESULT",y,p["paper"],p["discoveredCount"],p["answerCount"],p["expectedCount"],p["issues"][:4],flush=True)

if __name__=="__main__":main()
