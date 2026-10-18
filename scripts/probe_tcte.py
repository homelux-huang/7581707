import requests
from bs4 import BeautifulSoup
for year in (114,113,101,90):
    url=f'https://web1.tcte.edu.tw/EXAM/{year}_4y/'
    try:
        r=requests.get(url,timeout=25,headers={'User-Agent':'Mozilla/5.0'})
        print('PAGE',year,r.status_code,len(r.content),r.url,flush=True)
        soup=BeautifulSoup(r.content,'html.parser')
        for tr in soup.select('tr'):
            s=' '.join(tr.stripped_strings)
            if any(x in s for x in ('09商業','09 商業','商業類','國文科','數學(B)')):
                print('ROW',repr(s[:150]),flush=True)
                print('HTML',str(tr)[:1800],flush=True)
        for sc in soup.find_all('script'):
            st=sc.get_text()[:10000]
            if 'download' in st.lower() or 'fopen' in st.lower():
                print('SCRIPT',repr(st[:700]),flush=True)
    except Exception as exc: print('ERROR',year,type(exc).__name__,str(exc)[:200],flush=True)
