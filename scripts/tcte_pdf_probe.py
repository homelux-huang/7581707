import base64,re,requests,fitz
from urllib.parse import urljoin
from bs4 import BeautifulSoup
session=requests.Session(); session.headers['User-Agent']="Mozilla/5.0 7581707-educational-index/1.0"
for y in [115,114,113,110,100,99,95,90]:
  url=f'https://web1.tcte.edu.tw/EXAM/{y}_4y/'
  try:
    r=session.get(url,timeout=35)
    print("\nYEAR",y,r.status_code,len(r.content),r.url,flush=True)
    html=r.content.decode(r.apparent_encoding or 'utf8',errors='replace')
    m=re.search(r'09.{0,30}(?:商|管理)',html)
    if not m: m=re.search(r'商業類',html)
    if m:
      block=html[m.start():m.start()+4500]
      entries=re.findall(r'<input[^>]*onclick=["\x27]([^"\x27]*?downloader[^"\x27]*?)["\x27][^>]*>',block,re.I)
      print("BLOCK_TEXT",BeautifulSoup(block[:700],'html.parser').get_text(" ",strip=True),flush=True)
      print("INPUTS",entries[:5],flush=True)
    else: print("NOT_FOUND_09_OR_BUSINESS",html[:150],flush=True)
    # Try one exact known 114 format if page matches published 09 links
    if y==114:
      for name in ['114-4y-09-2.pdf','114-4y-09-2-standard.pdf']:
        target=url+'downloader.php?obj='+base64.b64encode(name.encode()).decode()
        rr=session.get(target,timeout=45)
        print("PDF",name,rr.status_code,len(rr.content),rr.url,rr.headers.get('content-type'),flush=True)
        if rr.content[:4]==b'%PDF':
          doc=fitz.open(stream=rr.content,filetype='pdf')
          print("PAGES",len(doc),"FIRST_PAGE_TEXT",repr(doc[0].get_text(sort=True)[:4500]),flush=True)
          if len(doc)>2: print("PAGE2",repr(doc[2].get_text(sort=True)[:1100]),flush=True)
  except Exception as e:print("ERROR",y,type(e).__name__,str(e)[:200],flush=True)
