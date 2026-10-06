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

def module_types(markup):
    return sorted(set(re.findall(r"<!--\s*wp:divi/([\w-]+)", markup)))


def features(markup):
    low=markup.lower()
    modules=set(module_types(markup))
    return {
      "has_image": "image" in modules or '"image"' in low,
      "has_button": "button" in modules or '"button"' in low,
      "has_form": "form" in low,
      "has_video": "video" in low,
      "has_slider": "slider" in modules or "slide" in modules,
      "has_code": "code" in modules,
      "has_responsive_settings": '"phone"' in low or '"tablet"' in low,
    }


def signals(label, markup, category):
    low=(label+" "+markup).lower()
    visual=[]
    content=[]
    if any(term in low for term in ("#0d0e24", "#090b14", "#141630", "navy", "dark")):
        visual.append("dark")
    if "gradient" in low or "linear-gradient" in low:
        visual.append("gradient")
    if "border-radius" in low or '"radius"' in low:
        visual.append("rounded")
    if any(term in low for term in ("hero", "banner")) or category == "hero":
        content.append("hero")
    if any(term in low for term in ("mobile", '"phone"', '"tablet"')):
        content.append("responsive")
    if any(term in low for term in ("headline", "heading", "title")):
        content.append("headline")
    if "cta" in low or "call to action" in low:
        content.append("cta")
    return {"visual": sorted(set(visual)), "content": sorted(set(content))}


def search_tokens(label, category, modules, features_data, signals_data):
    values=[label, category, " ".join(modules), " ".join(signals_data["visual"]),
            " ".join(signals_data["content"])]
    values.extend(name.removeprefix("has_").replace("_", " ")
                  for name, enabled in features_data.items() if enabled)
    return sorted(set(re.findall(r"[a-z0-9]+", " ".join(values).lower())))


SYNONYMS={
    "banner": {"hero"}, "headline": {"hero", "headline"},
    "action": {"cta", "button"}, "call": {"cta"},
    "phone": {"mobile", "responsive"}, "tablet": {"responsive"},
    "photo": {"image", "gallery"}, "picture": {"image", "gallery"},
    "carousel": {"slider"}, "reviews": {"testimonial"},
    "navy": {"dark"}, "blue": {"dark"},
}


def searchable_metadata(label, category, markup, metadata_features):
    modules=module_types(markup)
    metadata_signals=signals(label, markup, category)
    return {
      "modules": modules,
      "signals": metadata_signals,
      "search_terms": search_tokens(label, category, modules, metadata_features, metadata_signals),
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
        metadata_features=features(markup)
        search_data=searchable_metadata(label, category, markup, metadata_features)
        component_id=f"{d.slugify(source_name or path.stem)}-{pos:02d}-{d.slugify(label)}-{digest[:8]}"
        folder=COMPONENTS/category/component_id
        folder.mkdir(parents=True, exist_ok=False)
        (folder/"component.divi").write_text(markup, encoding="utf-8", newline="")
        metadata={
            "schema":"divi-library-component-v2","id":component_id,"kind":"section",
            "category":category,"label":label,"sha256":digest,
            "source":{"name":source_name or path.stem,"file":path.name,"section":pos},
            "tags":sorted(set([category]+search_data["signals"]["content"])),
            "features":metadata_features, "modules":search_data["modules"],
            "signals":search_data["signals"], "search_terms":search_data["search_terms"],
          "validation":{"divi_block_balance":True}
        }
        (folder/"metadata.json").write_text(json.dumps(metadata,indent=2)+"\n",encoding="utf-8")
        index["components"].append(metadata); hashes.add(digest); added.append(component_id)
    save_index(index)
    print(json.dumps({"source":path.name,"sections":len(sections),"added":added,"duplicates":skipped},indent=2))

def search_index(index, query):
    raw_tokens=re.findall(r"[a-z0-9_:-]+", query.lower())
    filters=[]
    terms=[]
    for token in raw_tokens:
        if ":" in token:
            key, value=token.split(":", 1)
            if key in {"category", "has", "feature", "module", "signal"} and value:
                filters.append((key, value.replace("-", "_")))
                continue
        terms.append(token)
    expanded=[]
    for term in terms:
        expanded.append(term)
        expanded.extend(SYNONYMS.get(term, ()))
    expanded=set(expanded)
    matches=[]
    for item in index.get("components", []):
        if any(key == "category" and item.get("category") != value for key, value in filters):
            continue
        if any(key == "module" and value not in item.get("modules", []) for key, value in filters):
            continue
        if any(key == "signal" and value not in item.get("signals", {}).get("visual", []) + item.get("signals", {}).get("content", []) for key, value in filters):
            continue
        if any(key in {"has", "feature"} and not item.get("features", {}).get("has_"+value, False) for key, value in filters):
            continue
        hay=set(item.get("search_terms", []))
        if not expanded:
            score=0; matched=[]
        else:
            matched=sorted(term for term in expanded if term in hay)
            if not matched:
                continue
            score=sum(3 if term in terms else 1 for term in matched)
        result=dict(item)
        result["score"]=score
        result["matched_terms"]=matched
        matches.append(result)
    return sorted(matches, key=lambda item: (-item["score"], item["id"]))


def search(query):
    print(json.dumps(search_index(load_index(), query),indent=2))

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
