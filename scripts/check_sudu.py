from pathlib import Path
import re,subprocess,sys,json
s=Path('sudu/index.html').read_text(encoding='utf-8')
scripts=re.findall(r'<script(?:\s+[^>]*)?>([\s\S]*?)</script>',s)
js=[x for x in scripts if 'function clinic(){' in x]
assert len(js)==1,'application script must exist exactly once'
Path('/tmp/sudu_app.js').write_text(js[0],encoding='utf-8')
subprocess.run(['node','--check','/tmp/sudu_app.js'],check=True)
for required in ['data-clinic-answer','data-clinic-reset','concept-key','keyHtml','第一次答錯']:
 assert required in s,required
payload=re.search(r'<script id="bootstrap" type="application/json">([\s\S]*?)</script>',s)
assert payload,'bootstrap json missing'
j=json.loads(payload.group(1))
assert len(j['practice'])==64, len(j['practice'])
print('OK syntax and 64 practice questions, review and highlight controls')
