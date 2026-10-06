#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STORE = Path(__file__).resolve().parent / "library"
COMPONENTS = STORE / "components"
INDEX = STORE / "index.json"

def engine():
    path = ROOT / "tools" / "divi_modules.py"
    spec = importlib.util.spec_from_file_location("existing_divi_modules", path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module

def classify(label, markup):
    text=(label+" "+markup[:4000]).lower()
    rules=[("hero",["hero","banner"]),("testimonial",["testimonial","review"]),
           ("pricing",["pricing","price"]),("faq",["faq","accordion"]),
           ("contact",["contact","form"]),("cta",["call to action","cta"]),
           ("features",["feature","benefit","service"]),("gallery",["gallery","portfolio"])]
    for category, words in rules:
        if any(w in text for w in words): return category
    return "other"

def features(markup):
    low=markup.lower()
    return {
      "has_image": "divi/image" in low or '"image"' in low,
      "has_button": "divi/button" in low or '"button"' in low,
      "has_form": "form" in low,
      "has_video": "video" in low,
    }

def load_index():
    if not INDEX.exists(): return {"schema":"divi-library-index-v1","components":[]}
    return json.loads(INDEX.read_text(encoding="utf-8"))

def save_index(index):
    STORE.mkdir(parents=True, exist_ok=True)
    index["components"]=sorted(index["components"], key=lambda x:x["id"])
    INDEX.write_text(json.dumps(index, indent=2)+"\n", encoding="utf-8")

def ingest(path, source_name=None):
    d=engine(); path=Path(path).resolve()
    _, payload, _, _ = d.load_export(path)
    errors=d.scan_divi_balance(payload)
    if errors: raise SystemExit("Source failed Divi validation:\n" + "\n".join(errors))
    sections=d.top_level_sections(payload)
    index=load_index(); hashes={x["sha256"] for x in index["components"]}
    added=[]; skipped=[]
    for pos,(start,end,attrs) in enumerate(sections,1):
        markup=payload[start:end]
        digest=hashlib.sha256(markup.encode("utf-8")).hexdigest()
        if digest in hashes:
            skipped.append(digest[:12]); continue
        label=d.extract_label(attrs, pos)
        category=classify(label, markup)
        component_id=f"{d.slugify(source_name or path.stem)}-{pos:02d}-{d.slugify(label)}-{digest[:8]}"
        folder=COMPONENTS/category/component_id
        folder.mkdir(parents=True, exist_ok=False)
        (folder/"component.divi").write_text(markup, encoding="utf-8", newline="")
        metadata={
          "schema":"divi-library-component-v1","id":component_id,"kind":"section",
          "category":category,"label":label,"sha256":digest,
          "source":{"name":source_name or path.stem,"file":path.name,"section":pos},
          "tags":[category],"features":features(markup),
          "validation":{"divi_block_balance":True}
        }
        (folder/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
        index["components"].append(metadata); hashes.add(digest); added.append(component_id)
    save_index(index)
    print(json.dumps({"source":path.name,"sections":len(sections),"added":added,"duplicates":skipped},indent=2))

def search(query):
    tokens=query.lower().split()
    matches=[]
    for item in load_index()["components"]:
        hay=json.dumps(item).lower()
        if all(t in hay for t in tokens): matches.append(item)
    print(json.dumps(matches,indent=2))

def validate():
    d=engine(); failures=[]
    for item in load_index()["components"]:
        p=COMPONENTS/item["category"]/item["id"]/"component.divi"
        if not p.exists(): failures.append(f"{item['id']}: missing component.divi"); continue
        markup=p.read_text(encoding="utf-8")
        digest=hashlib.sha256(markup.encode("utf-8")).hexdigest()
        errors=d.scan_divi_balance(markup)
        if digest != item["sha256"]: failures.append(f"{item['id']}: hash mismatch")
        failures.extend(f"{item['id']}: {e}" for e in errors)
    if failures: raise SystemExit("\n".join(failures))
    print(f"OK: {len(load_index()['components'])} components validated")

def clone(component_id, destination):
    found=next((x for x in load_index()["components"] if x["id"]==component_id),None)
    if not found: raise SystemExit(f"Unknown component: {component_id}")
    src=COMPONENTS/found["category"]/component_id/"component.divi"
    dst=Path(destination).resolve(); dst.parent.mkdir(parents=True,exist_ok=True)
    shutil.copyfile(src,dst); print(dst)

def main():
    p=argparse.ArgumentParser(description="Divi reusable design library builder")
    s=p.add_subparsers(dest="cmd",required=True)
    i=s.add_parser("ingest"); i.add_argument("export"); i.add_argument("--source-name")
    q=s.add_parser("search"); q.add_argument("query")
    c=s.add_parser("clone"); c.add_argument("component_id"); c.add_argument("--to",required=True)
    s.add_parser("validate")
    a=p.parse_args()
    {"ingest":lambda:ingest(a.export,a.source_name),"search":lambda:search(a.query),
     "clone":lambda:clone(a.component_id,a.to),"validate":validate}[a.cmd]()

if __name__=="__main__": main()
