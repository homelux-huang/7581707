"""Role A read-only 115 MB21 source/SQLite shape inspector. Never creates QA approval."""
import json,sqlite3,hashlib
from pathlib import Path
p=Path("sudu/data/processed/115")
o=json.loads((p/"questions.json").read_text())
q=next(x for x in o["questions"] if x.get("questionId")=="115-00-MB-21")
print("BANK",len(o["questions"]),list(o),flush=True)
print("Q21",json.dumps(q,ensure_ascii=False,sort_keys=True),flush=True)
i=json.loads((p/"inventory.json").read_text())
print("INVENTORY_SQL",json.dumps(i.get("sqlite"),ensure_ascii=False),flush=True)
print("DB_SHA",hashlib.sha256((p/"question-bank.sqlite3").read_bytes()).hexdigest(),flush=True)
with sqlite3.connect("file:"+str(p/"question-bank.sqlite3")+"?mode=ro",uri=True) as c:
 print("DB_TABLES",c.execute("SELECT name,sql FROM sqlite_master WHERE type='table'").fetchall(),flush=True)
 for n in ("questions",):
  print("DB_COLUMNS",c.execute("PRAGMA table_info("+n+")").fetchall(),flush=True)
  print("DB_N",c.execute("SELECT COUNT(*) FROM "+n).fetchone(),flush=True)
  print("DB_21",c.execute("SELECT * FROM "+n+" WHERE question_id=?",("115-00-MB-21",)).fetchone(),flush=True)
