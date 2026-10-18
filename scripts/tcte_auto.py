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
VERSION=4

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
    source_year=int(re.search(r"/(\d{2,3})_4y/",url).group(1))
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
        # Actual historical commerce group: 90-91 code 14, 92-97 code 13, 98+ code 09 (official yearly indexes).
        m2=re.search(r"(?:^|-4y-)(09-[12]|13-[12]|14-[12]|00-[A-Za-z0-9]+)(?:-standard|-answer|-ans)?\.pdf$",fn,re.I)
        if not m2:continue
        paper=m2.group(1).upper()
        if re.fullmatch(r"(09|13|14)-[12]",paper):
            code,part=paper.split("-")
            expected="14" if source_year<=91 else ("13" if source_year<=97 else "09")
            if code!=expected:continue
            if source_year<98:paper="BIZ-"+part
        if paper not in OPTION_NAMES and paper not in {"BIZ-1","BIZ-2"} and not paper.startswith("00-M"):continue
        key=(paper,kind)
        if key in matches:continue
        full=urljoin(url,"downloader.php?obj="+m.group(1))
        matches[key]={"filename":fn,"url":full,"kind":kind,"paper":paper}
    return list(matches.values())

def legacy_links(html,url):
    """Legacy 090-094 linked PDF directly; derive codes from official href, not neighboring group cells."""
    soup=BeautifulSoup(html,"html.parser")
    linked={}
    source_year=int(re.search(r"/(\d{3})_4y",url).group(1))
    for item in soup.find_all("a",href=True):
        href=urljoin(url,item["href"])
        if urlparse(href).hostname not in DOMAIN:continue
        base_name=urlparse(href).path.split("/")[-1].lower()
        m=re.search(r"(?:\d{2,3}-4y-)(09|13|14)-([12])(?:-(standard|solve|finalsolve))?\.pdf$",base_name)
        paper=None;kind="exam"
        if m:
            code,part,suffix=m.groups()
            expected="14" if source_year<=91 else ("13" if source_year<=97 else "09")
            if code==expected:paper=("BIZ-" if source_year<98 else "09-")+part
            if suffix:kind="answer"
        else:
            m=re.search(r"(?:\d{2,3}-4y-)(00-[cem][a-z]?)(?:-(standard|solve|finalsolve))?\.pdf$",base_name)
            if m:
                code,suffix=m.groups()
                if code=="00-c":paper="00-C"
                elif code=="00-e":paper="00-E"
                elif code in ("00-mb","00-m-b"):paper="00-MB"
                elif code=="00-m":paper="00-M-OLD"
                if suffix:kind="answer"
        # The 90 exam uses plain 14_1.pdf and contextual '商業類專一' text.
        if not paper and source_year==90 and base_name.endswith(".pdf"):
            label=re.sub(r"\s+","",item.parent.get_text(" ",strip=True))
            if "商業類專一" in label or "商業類專業科目一" in label:paper="BIZ-1"
            elif "商業類專二" in label or "商業類專業科目二" in label:paper="BIZ-2"
            elif "共同科國文" in label:paper="00-C"
            elif "共同科英文" in label:paper="00-E"
            elif "共同科數學" in label:paper="00-M-OLD"
        if paper:
            record={"filename":base_name,"url":href,"kind":kind,"paper":paper}
            k=(paper,kind)
            if k not in linked or "finalsolve" in base_name or "standard" in base_name:
                linked[k]=record
    return list(linked.values())

def pdf_text(pdf_bytes):
    """Read only an existing PDF text layer. Scanned pages are rendered as images, never OCR."""
    with fitz.open(stream=pdf_bytes, filetype="pdf") as doc:
        return [page.get_text(sort=True) for page in doc], []

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

def subject_from_source(year,paper,number,prefix):
    if paper=="09-2" and year==114:
        return "會計學" if number<=24 else "經濟學"
    if paper=="BIZ-1" and year==90:
        return "會計學" if number<=25 else "經濟學"
    # Use explicit subject-section headings only; never infer per-question chapters.
    h=re.findall(r"(?m)^[ \t]*(?:[壹貳參肆一二三四][、.．]\s*)?(會計學|經濟學|商業概論|數位科技概論|數位科技應用)\s*[:：]?\s*$",prefix)
    if h and paper in {"09-1","09-2","BIZ-1","BIZ-2"}:return h[-1]
    return GROUP_CODES.get(paper,paper)

def extract_questions(pages,year,paper,src,ocr_pages):
    offsets=[];full=""; 
    for i,text in enumerate(pages):
        offsets.append(len(full))
        # Modern PDFs have a cover page with numbered instructions; skip it.
        if i == 0 and "考試開始鈴" in text and "試題本" in text:
            full += "\n\n"
        else:
            full += text + "\n\n"
    markers=list(QSTART.finditer(full))
    if year==114 and paper=="09-2":
        print("DEBUG_HEAD",repr(full[:1100]),flush=True)
        print("DEBUG_MARKERS",len(markers),[(m.group(1),m.start()) for m in markers[:18]],flush=True)
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
        if year==114 and paper=="09-2" and i<5: print("DEBUG_CANDIDATE",number,"pg",pg,"len",len(raw),"first",repr(raw[:250]),flush=True)
        stem,options,warnings=parse_question_options(raw)
        if not stem:continue
        # Numbered cover instructions used to consume IDs 1-3 before the real
        # questions. Keep searching for the real number; never publish this text.
        if re.match(r"^(?:請先核對考試科目|本試題共|本試題均為|本試卷共|本試卷均為|請用.?2B|請依題號順序|本試題不可使用)", stem):continue
        if len(options)!=4:warnings.append("missing_complete_options")
        if pg in ocr_pages:warnings.append("ocr_not_manually_verified")
        if not options and number>2 and number not in found:continue
        qid=f"{year}-{paper}-{number:02d}"
        # Never pretend a machine read is a confirmed textbook reference.
        found[number]={
            "id":qid,"year":year,"paper":paper,"number":number,
            "subject":subject_from_source(year,paper,number,full[:m.start()]),
            "kind":"官方歷屆題（自動擷取、待審核）",
            "question":stem,"options":options,
            "answer":None,"answerMatched":False,"answerVerified":False,
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
        entry["questionPdfSha256"]=hashlib.sha256(raw).hexdigest()
        pages,ocr=pdf_text(raw)
        q=extract_questions(pages,year,code,link["url"],ocr)
        entry["expectedCount"]=expected_count_from_cover(pages)
        entry["discoveredCount"]=len(q)
        # Create explicitly flagged navigation slots for missing OCR questions.
        # These are NOT counted as successfully extracted question texts.
        expected=entry["expectedCount"]
        if expected and 1<=expected<=100:
            found={item["number"] for item in q}
            for no in range(1,expected+1):
                if no in found:continue
                q.append({"id":f"{year}-{code}-{no:02d}","year":year,"paper":code,"number":no,
                  "subject":GROUP_CODES.get(code,code),"kind":"官方原卷 OCR 未辨識題",
                  "question":"本題原卷文字、圖表或公式尚未成功擷取，請點選原始 PDF 對照，不能把此提示當作正式題幹。",
                  "options":[],"answer":None,"answerMatched":False,"answerVerified":False,"questionVerified":False,
                  "explanation":"","steps":"","extension":"","practice":None,"textbook":None,"teachingVerified":False,
                  "source":link["url"],"official":True,"page":None,"issues":["OCR_missing_question"]})
            q.sort(key=lambda item:item["number"])
        entry["questions"]=q
        if entry["expectedCount"] and entry["discoveredCount"]!=entry["expectedCount"]:
            issues.append(f"OCR_extracted_{entry['discoveredCount']}_of_{entry['expectedCount']}")
        if not q:issues.append("no_readable_questions")
        if ocr:issues.append("ocr_pages_"+",".join(map(str,ocr)))
        if answer_link:
            ar=guarded_get(answer_link["url"],60).content
            if ar[:4]!=b"%PDF":raise ValueError("Official answer response not PDF")
            entry["answerPdfSha256"]=hashlib.sha256(ar).hexdigest()
            ap,ao=pdf_text(ar)
            answers,conflicts=parse_answers(ap)
            entry["answerCount"]=len(answers)
            if conflicts:issues.append("answer_conflicts_"+str(conflicts[:15]))
            for item in q:
                ans=answers.get(item["number"])
                if ans is not None:
                    item["officialAnswerCandidate"]=ans
                    item["answerSource"]=answer_link["url"]
                    if len(item["options"])==4 and all(item["options"]) and "OCR_missing_question" not in item.get("issues",[]):
                        item["answer"]="ABCD".index(ans)
                        item["answerMatched"]=True
                        item["answerVerified"]=False
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
    for item in entry["questions"]:
        item["sourceVersion"]={"questionPdfSha256":entry.get("questionPdfSha256"),
                               "answerPdfSha256":entry.get("answerPdfSha256")}
    # Strictly complete means no missing questions AND all answer confirmations AND approved teaching.
    entry["complete"]=bool(entry["expectedCount"] and len(entry["questions"])==entry["expectedCount"]
          and all(q["answerVerified"] and q["questionVerified"] and q["teachingVerified"] for q in entry["questions"]))
    return entry

def legacy_answer_table(url):
    """Extract old multi-subject HTML standard-answer table by its published column headers."""
    try:
        page=guarded_get(urljoin(url,"answer.htm")).text
    except Exception:
        return {}
    soup=BeautifulSoup(page,"html.parser")
    found={}
    targets={"BIZ-1":["商業類（一）","商業類(一)","商業類一"],
             "BIZ-2":["商業類（二）","商業類(二)","商業類二"],
             "00-C":["國文"],"00-E":["英文"],"00-M-OLD":["數學商業類"]}
    for table in soup.find_all("table"):
        rows=table.find_all("tr")
        for head_i,head in enumerate(rows):
            cols=head.find_all(["td","th"],recursive=False)
            headers=[re.sub(r"\s+","",cell.get_text(" ",strip=True)) for cell in cols]
            if len(headers)<20 or not any("商業類" in x for x in headers):continue
            mapping={}
            for code,names in targets.items():
                possible=[i for i,title in enumerate(headers) if title in names]
                if len(possible)==1:mapping[code]=possible[0]
            if not mapping:continue
            for row in rows[head_i+1:]:
                cells=row.find_all(["td","th"],recursive=False)
                if len(cells)<len(headers)-2:continue
                cells=[re.sub(r"\s+","",cell.get_text(" ",strip=True)) for cell in cells]
                if not cells or not re.fullmatch(r"\d{1,3}",cells[0]):continue
                no=int(cells[0])
                for code,idx in mapping.items():
                    if idx>=len(cells):continue
                    val=cells[idx].upper()
                    accepted=re.findall(r"[ABCD]",val)
                    if 1<=no<=100 and accepted and len(accepted)<=4 and re.fullmatch(r"[ABCD](?:OR[ABCD])*",val,re.I):
                        found.setdefault(code,{})[no]=list(dict.fromkeys(accepted))
            if found:return found
    return found

def legacy_91_answer_pdf(year_url):
    """Read 91 official one-page *multi-subject* final-answer PDF, by explicit 14商業類 rows."""
    target=urljoin(year_url,"91-4y-answer-new.pdf")
    out={}
    try:
        binary=guarded_get(target,45).content
        if not binary.startswith(b"%PDF"):return out
        document=fitz.open(stream=binary,filetype="pdf")
        lines=document[0].get_text(sort=True).splitlines()
        for line in lines:
            line=line.strip()
            match=re.search(r"14商業類\s*\(\s*專\s*([一二])\s*\)\s*(.*)$",line)
            if not match:continue
            paper="BIZ-1" if match.group(1)=="一" else "BIZ-2"
            vals=re.findall(r"送分|[ABCD](?:或[ABCD])?",match.group(2))
            if len(vals)<40:continue
            accepted={}
            for number,token in enumerate(vals[:50],start=1):
                accepted[number]=list(dict.fromkeys(re.findall(r"[ABCD]",token))) if token!="送分" else list("ABCD")
            out[paper]=accepted
    except Exception as exc:
        print("LEGACY91_ANSWER_ERROR",type(exc).__name__,str(exc)[:140],flush=True)
    return out

def process_year(y):
    entry={"year":y,"courseType":"09商管群" if y>=98 else "舊制商業類（不可直接當作09商管群）",
           "sourceIndex":year_url(y),"generatedAt":stamp(),"pipelineVersion":VERSION,"papers":[],"errors":[]}
    try:
        base=year_url(y)
        response=guarded_get(base)
        # 90–99 old sites have direct links and often HTML answer keys, which require different parser.
        links=decoded_input_links(response.text,base)
        if not links:
            links=legacy_links(response.text,base)
        if y<98:
            entry["courseType"]="舊制商業類（90-91考科代碼14，92-97代碼13；98起09商管群）"
        entry["discoveredPdfLinks"]=len(links)
        exams=[p for p in links if p["kind"]=="exam"]
        answers={p["paper"]:p for p in links if p["kind"]=="answer"}
        # Restrict to 09 professional and common subjects for this platform.
        exams=[e for e in exams if e["paper"] in OPTION_NAMES or (y<98 and e["paper"] in {"BIZ-1","BIZ-2","00-M-OLD"})]
        # Old math versions are distinct. Do not silently choose one among several.
        legacy_keys=legacy_91_answer_pdf(base) if y==91 else (legacy_answer_table(base) if y==90 and any(x["paper"].startswith("BIZ-") for x in exams) else {})
        for x in exams:
            paper=process_one(y,x,answers.get(x["paper"]))
            official=legacy_keys.get(x["paper"],{})
            if official:
                for question in paper["questions"]:
                    opts=official.get(question["number"])
                    if opts and len(question["options"])==4 and all(question["options"]) and "OCR_missing_question" not in question.get("issues",[]):
                        question["acceptedAnswers"]=["ABCD".index(c) for c in opts]
                        question["answer"]=question["acceptedAnswers"][0]
                        question["answerMatched"]=True
                        question["answerVerified"]=False
                        question["answerSource"]=urljoin(base,"91-4y-answer-new.pdf") if y==91 else urljoin(base,"answer.htm")
                paper["answerCount"]=len(official)
                paper["answerHtml"]=urljoin(base,"answer.htm")
                paper["issues"]=[x for x in paper["issues"] if x!="official_answer_pdf_not_identified"]
            entry["papers"].append(paper)
        if not exams:entry["errors"].append("未找到對應試題 PDF；官方來源版型或代碼需再擴充。")
    except Exception as exc:
        entry["errors"].append(type(exc).__name__+": "+str(exc)[:280])
    entry["papersFound"]=len(entry["papers"])
    entry["questionsFound"]=sum(p.get("discoveredCount",0) for p in entry["papers"])
    entry["officialAnswersMatched"]=sum(sum(bool(q.get("answerMatched") or q.get("answerVerified")) for q in p["questions"]) for p in entry["papers"])
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
