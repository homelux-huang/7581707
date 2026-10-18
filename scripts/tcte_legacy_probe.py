import re, requests,base64
from bs4 import BeautifulSoup
for y in range(91,100):
 u=f'https://web1.tcte.edu.tw/EXAM/{y:03d}_4y/'
 try:
  r=requests.get(u,timeout=25)
  html=r.content.decode(r.apparent_encoding or 'utf8',errors='replace')
  m=re.search(r'09.{0,25}商|商業類',html)
  print('YEAR',y,r.status_code,len(html),'MATCH',m.group(0) if m else None,flush=True)
  if m:
   print('RAW',repr(html[m.start():m.start()+1800]),flush=True)
  ss=BeautifulSoup(html,'html.parser')
  if y>=95:
   matches=[]
   for z in ss.find_all('input',onclick=True):
    mm=re.search(r'obj=([A-Za-z0-9+/=]+)',z['onclick'])
    if mm:
     try:
      fn=base64.b64decode(mm.group(1)).decode('utf8')
      if '-4y-' in fn and ('-09-' in fn or '-14-' in fn or '-00-' in fn):matches.append(fn)
     except:pass
   print('PDF_CODES',y,[fn for fn in matches if re.search(r'-(?:09|14)-(?:1|2)[-.]',fn)][:16],flush=True)
  for x in ss.find_all('input',onclick=True)[:6]:
   print('INPUT',repr(x.get('onclick','')),flush=True)
  for x in ss.find_all('a',href=True)[:6]:
   print('A',repr(x.get_text(' ',strip=True)),repr(x['href']),flush=True)
 except Exception as e: print('ERROR',y,type(e).__name__,str(e)[:180],flush=True)
