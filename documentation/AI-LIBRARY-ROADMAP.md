# Divi AI Library & Clone Roadmap

## Goal

Extend the existing lossless Divi 5 split/compile workflow into an agent-friendly design library that can ingest approved Divi layouts, extract reusable components, find them semantically, clone/adapt them, compose new pages, validate the result, and then hand the finished page to the existing deployment workflow.

The current `Modules/<page>/sections/*.divi` files remain the editable source of truth for site pages. The library is a reusable design corpus, not a replacement for the current page structure.

## Existing foundation to preserve

- Raw Divi 5 Gutenberg/block markup is preserved rather than normalized into a custom JSON schema.
- `tools/divi_modules.py` owns split, compile, block-balance validation, wrapper preservation, and safe JSON escaping.
- Page manifests preserve ordered assembly.
- Compiled output remains generated output.
- Existing page-specific transformation tools can continue to operate.
- Deployment remains a separate final step and must keep site-specific safety guardrails.

## Target architecture

```text
Approved layout source
        |
        v
   Import / ingest
        |
        v
 Lossless Divi extraction
        |
        +----> full page
        +----> section
        +----> row (later)
        +----> module (later)
        |
        v
 Metadata + visual evidence
        |
        v
 Reusable component library
        |
        v
 Search / select / clone / adapt
        |
        v
 Page workspace (Modules/<page>)
        |
        v
 compile -> validate -> preview/diff -> deploy
```

## Proposed repository structure

```text
documentation/
  AI-LIBRARY-ROADMAP.md
  COMPONENT-SCHEMA.md
  INGESTION.md
  AGENT-WORKFLOW.md

Library/
  components/
    hero/
    features/
    cards/
    testimonials/
    gallery/
    pricing/
    cta/
    contact/
    navigation/
    footer/
    other/
  sources/
  index.json

tools/
  divi_modules.py
  divi_library.py        # ingest/index/search/clone
  divi_compose.py        # page composition operations (later)
```

Do not move the existing `Modules/` tree during the first implementation.

## Component model

Each reusable component should keep the original `.divi` markup untouched and store metadata beside it.

Example:

```text
Library/components/hero/modern-split-hero/
  component.divi
  metadata.json
  preview.png            # optional initially
```

Suggested metadata:

```json
{
  "schema": "divi-library-component-v1",
  "id": "modern-split-hero",
  "kind": "section",
  "category": "hero",
  "source": {
    "type": "approved-layout",
    "name": "source-layout-name"
  },
  "tags": ["modern", "split", "image", "cta"],
  "theme": ["light"],
  "industries": [],
  "features": {
    "has_image": true,
    "has_cta": true,
    "has_form": false
  },
  "validation": {
    "divi_block_balance": true
  }
}
```

Metadata describes a component; it must never become the canonical representation of the Divi markup.

## Phase 1 — Library foundation

Build `tools/divi_library.py` with a small deterministic command surface:

```bash
python tools/divi_library.py ingest ...
python tools/divi_library.py index
python tools/divi_library.py list --category hero
python tools/divi_library.py search "dark hero with image and CTA"
python tools/divi_library.py clone <component-id> --to ...
python tools/divi_library.py validate
```

Initial scope should be top-level sections because the current splitter already understands that boundary reliably.

### Acceptance criteria

- Ingesting a Divi export does not mutate its extracted section markup.
- Every component receives a stable ID and source provenance.
- Duplicate exact components can be detected by content hash.
- Library validation reuses the existing Divi block-balance logic.
- A library component can be copied into a page workspace and compiled by the existing compiler.

## Phase 2 — Classification and search

Add automatic metadata generation without allowing AI classification to alter component markup.

Useful classifications:

- hero
- feature/benefit grid
- card grid
- logo/social proof
- stats
- gallery
- testimonials
- pricing
- FAQ
- CTA
- contact/form
- navigation
- footer

Search should begin deterministic: category, tags, source, features, and text. Semantic/vector search can be added after the corpus is large enough to justify it.

## Phase 3 — Clone and compose operations

Expose agent-friendly operations instead of asking an agent to rewrite large raw files blindly:

- `clone_section`
- `insert_section`
- `remove_section`
- `move_section`
- `replace_section`
- `replace_text`
- `replace_image`
- `set_link`
- `compile_page`
- `validate_page`

The operation layer should make small, inspectable changes and preserve the existing raw Divi structure whenever possible.

## Phase 4 — Visual catalog

Generate a preview for each component and attach it to the library entry.

Then support requests such as:

> Find a modern dark hero with one image, two calls to action, and enough room for a short headline.

The agent should return candidate component IDs first, then clone the selected component into the working page.

Later, image embeddings can support visual similarity: "find sections that look like this."

## Phase 5 — Site adaptation

A cloned component should be adapted to the destination site's design system rather than copied literally.

Separate:

1. structure/layout
2. content
3. design tokens/style
4. site-specific behavior

This enables prompts such as:

> Use this hero's composition, but apply the current site's typography, colors, button style, spacing, and content.

The source component remains unchanged; adaptation happens in the destination page workspace.

## Phase 6 — Autonomous visual iteration

Only after deterministic clone/compose/validation is stable:

1. compose page
2. compile
3. render preview
4. capture screenshot
5. compare against intent/reference
6. make bounded changes
7. compile and validate again
8. stop at acceptance threshold or request review
9. deploy only through the established deployment guardrails

## Ingestion policy

Prefer layouts obtained through authorized/approved channels. Keep provenance for every imported component.

Do not make website scraping the core ingestion strategy. For Elegant Themes/Divi layouts, use an authorized Divi environment or exported layout files as the input to the local extractor.

## Important implementation rule

Do **not** begin by building a sophisticated database.

The Git repository can be the first component store:

- `.divi` = canonical component
- `metadata.json` = searchable description
- `index.json` = generated catalog
- Git history = provenance/change history

A database or vector store becomes useful later when the library size/search requirements justify it.

## First implementation milestone

The first useful vertical slice is:

1. Add `Library/`.
2. Add `divi_library.py ingest`.
3. Feed it one authorized Divi layout export.
4. Extract its top-level sections using the existing parsing logic.
5. Create component folders + metadata.
6. Build `index.json`.
7. Clone one imported section into a test page workspace.
8. Compile with the existing compiler.
9. Validate exact Divi block balance.
10. Preview manually before any deployment.

If that works end-to-end, expand ingestion volume before adding rows/modules, embeddings, or autonomous visual iteration.
