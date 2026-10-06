# LibraryBuilder

An isolated, Git-backed reusable design library for Divi 5.

It deliberately does **not** replace `Modules/` or the existing site tooling. The builder dynamically loads the trusted `tools/divi_modules.py` parser for lossless export parsing, top-level section extraction, labels, and Divi block validation.

## First vertical slice

```bash
# Ingest an authorized Divi JSON export
python3 LibraryBuilder/cli.py ingest /path/to/layout.json --source-name "DiviWP Landing Pack"

# Search the generated catalog
python3 LibraryBuilder/cli.py search "hero"

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

The original section markup is canonical. Ingestion calculates SHA-256 before storing it, so exact duplicate sections are skipped. Metadata records source provenance, category, features, and validation state.

## Tonight's workflow

1. Export/download an **authorized** Divi 5 layout JSON.
2. Run `ingest`.
3. Inspect/search the resulting catalog.
4. Run `validate`.
5. Clone one component into a scratch location.
6. Once that round-trip is verified, add composition into a page workspace and use the existing compiler/deployment flow.

Do not scrape or bypass access controls for commercial marketplace layouts. Use layouts you own, are licensed to use, or that are explicitly redistributable.
