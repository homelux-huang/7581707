import requests,fitz,re,base64
for y in (91,92,93,94,95,98,99):
 u=f"https://web1.tcte.edu.tw/EXAM/{y:03d}_4y/"
 links={91:["91-4y-answer-new.pdf","91-4y-14-1.pdf"],92:["92-4y-09-1-solve.pdf","92-4y-09-2-solve.pdf"],93:["93-4y-09-1-finalsolve.pdf","93-4y-09-2-finalsolve.pdf"],94:["94-4y-09-1-standard.pdf","94-4y-09-2-standard.pdf"],95:["95-4y-14-1.pdf"],98:["98-4y-14-1.pdf"],99:["99-4y-14-1.pdf"]}
 for fn in links[y]:
  try:
   target=u+('downloader.php?obj='+base64.b64encode(fn.encode()).decode() if y>=95 else fn)
   r=requests.get(target,timeout=35)
   print("FILE",y,fn,r.status_code,len(r.content),r.headers.get('content-type'),flush=True)
   if r.content.startswith(b"%PDF"):
    doc=fitz.open(stream=r.content,filetype="pdf")
    print("DOC",y,fn,"pages",len(doc),"TEXT",repr("\n".join(p.get_text(sort=True) for p in list(doc)[:2])[:3500]),flush=True)
  except Exception as e:print("ERR",y,fn,type(e).__name__,str(e)[:100],flush=True)
