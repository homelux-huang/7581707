"""Validate real app assets and corpus schema without a hard-coded fixture count."""
from pathlib import Path
import re,subprocess,json
root=Path(__file__).resolve().parents[1]
html=(root/'sudu/index.html').read_text(encoding='utf-8')
match=re.search(r'<script id="bootstrap" type="application/json">([\s\S]*?)</script>',html)
assert match,'bootstrap JSON missing'
payload=json.loads(match.group(1));practice=payload['practice']
assert practice and len({q['id'] for q in practice})==len(practice),'practice IDs must be unique'
for q in practice:
 assert isinstance(q['options'],list) and len(q['options'])==4 and all(isinstance(x,str) and x.strip() for x in q['options']),q['id']
 assert isinstance(q['answer'],int) and 0<=q['answer']<4,q['id']
app=(root/'sudu/app.js').read_text()
for required in ['data-clinic-answer','data-clinic-reset','concept-key','keyHtml','reviewHistory','attempts','correct===null']:
 assert required in app,required
for script in sorted((root/'sudu').glob('*.js')):subprocess.run(['node','--check',str(script)],check=True)
all_ids=set();json_count=0
for file in sorted((root/'sudu/data').rglob('*.json')):
 data=json.loads(file.read_text(),parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)));json_count+=1
 if file.parent.name!='years':continue
 assert str(data['year'])==file.stem,file
 for paper in data['papers']:
  numbers=set()
  for q in paper.get('questions',[]):
   assert q['id'] not in all_ids,('duplicate ID',q['id']);all_ids.add(q['id'])
   assert isinstance(q['number'],int) and q['number']>0 and q['number'] not in numbers,('duplicate/invalid paper number',file,paper['paper'],q['number']);numbers.add(q['number'])
   assert str(q['year'])==file.stem and q['paper']==paper['paper'],q['id']
for ref in re.findall(r'(?:src|href)="\./([^"?#]+)',html):assert (root/'sudu'/ref).is_file(),ref
assert 'data-tab="archive"' not in html and 'data-tab="source"' not in html
print(f'PASS: JavaScript syntax, {json_count} JSON files, {len(practice)} practice IDs, {len(all_ids)} official record IDs, unique per-paper numbers and app assets')
