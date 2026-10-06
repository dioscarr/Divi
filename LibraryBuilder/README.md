# LibraryBuilder

An isolated, Git-backed reusable design library for Divi 5.

It deliberately does **not** replace `Modules/` or the existing site tooling. The builder dynamically loads the trusted `tools/divi_modules.py` parser for lossless export parsing, top-level section extraction, labels, and Divi block validation.

## First vertical slice

```bash
# Ingest an authorized Divi JSON export
python3 LibraryBuilder/cli.py ingest /path/to/layout.json --source-name "DiviWP Landing Pack"

# Search the generated catalog with natural-language terms
python3 LibraryBuilder/cli.py search "dark mobile hero with CTA"

# Search with structured filters when you know the constraint
python3 LibraryBuilder/cli.py search "category:hero feature:image responsive"

# Validate every stored component against its hash and Divi block balance
python3 LibraryBuilder/cli.py validate

# Clone a selected component without modifying it
python3 LibraryBuilder/cli.py clone COMPONENT_ID --to /tmp/hero.divi
```

## Storage

```text
LibraryBuilder/
  cli.py
  library/
    index.json
    components/
      hero/
        <stable-component-id>/
          component.divi
          metadata.json
```

The original section markup is canonical. Ingestion calculates SHA-256 before storing it, so exact duplicate sections are skipped. Metadata records source provenance, category, module types, responsive/content/visual signals, searchable terms, features, and validation state. The schema is versioned as `divi-library-component-v2`.

Search expands common design language into library terms: `banner` maps to hero, `phone` to responsive/mobile, `action` to CTA/button, `photo` to image/gallery, and `carousel` to slider. Results are ranked by matched terms and include `score` and `matched_terms` for explainability.

## Tonight's workflow

1. Export/download an **authorized** Divi 5 layout JSON.
2. Run `ingest`.
3. Inspect/search the resulting catalog.
4. Run `validate`.
5. Clone one component into a scratch location.
6. Once that round-trip is verified, add composition into a page workspace and use the existing compiler/deployment flow.

Do not scrape or bypass access controls for commercial marketplace layouts. Use layouts you own, are licensed to use, or that are explicitly redistributable.
