# BD Star Divi 5 Modules

This folder breaks the current BD Star Transport Divi 5 exports into page-level module/section files.

## Structure

- `home/`, `about/`, `services/`, `contact/`, `header/`, `footer/`
  - `manifest.json` — ordered assembly manifest for that export.
  - `template.json` — original raw Divi export wrapper with only the payload replaced by a placeholder.
  - `sections/*.divi` — raw top-level Divi 5 section blocks.
- `_compiled/` — generated exports from the module files.

## Commands

From `/home/dioscarr/Work/divi-working-set`:

```bash
/home/dioscarr/.hermes/hermes-agent/venv/bin/python tools/divi_modules.py split --page all
/home/dioscarr/.hermes/hermes-agent/venv/bin/python tools/divi_modules.py compile --page all --out-dir /home/dioscarr/Work/divi-working-set/Modules/_compiled
/home/dioscarr/.hermes/hermes-agent/venv/bin/python tools/divi_modules.py validate --page all
```

Compile one page:

```bash
/home/dioscarr/.hermes/hermes-agent/venv/bin/python tools/divi_modules.py compile --page home
```

## Divi 5 safety rules

- Edit `.divi` files as raw Gutenberg/Divi 5 block markup.
- Preserve Divi 5 nested settings under `module.advanced` / `module.decoration` / module-specific keys.
- Do **not** convert to older flat `attrs` format.
- Do **not** hand-roll escaping. The compile script JSON-escapes the payload safely.
- Keep CRLF/newlines intact; the script reads/writes with `newline=''`.
- Validate and compare before importing compiled exports into WordPress.

## Home video modal backdrop settings

The home hero's video modal is a native `divi/code` module. A layout JSON
export can set only fields that Divi has registered for that module; it cannot
register a new Visual Builder panel or custom fields. The former embedded
`Video Modal / Backdrop` JSON was inert page markup, not a Divi control, and
has been removed.

The module is deliberately labelled **BD Video Modal — Backdrop (Code)** so it
is discoverable in the Visual Builder Layers panel. To edit it, open the Home
page in Visual Builder, open **Layers**, select that module, click its gear,
then go to **Content → Code**. At the beginning of its `<style>` block, edit
only these CSS custom-property values:

```bash
python tools/configure_video_modal_backdrop.py validate
```

```css
#bdstar-video{
  --bd-video-backdrop-color: rgba(12,16,31,.80);
  --bd-video-backdrop-blur: 12px;
}
```

Use any valid CSS color (`rgba(...)`, hex, or named color) and a CSS length
(for example, `4px`, `12px`, or `20px`). Do not edit the dialog markup or
scripts. A real select/color/slider control would require an installed,
registered Divi extension/custom module (PHP plus its Builder definition);
there is no extension source in this export-only working set.

## Contact message form: inline card + floating nav drawer

There are two instances of the same contact form, and they are independent.

**The inline card** on the Contact page is boxed by a hook on the **Column** that wraps the
form, not on the Contact Form module. That is deliberate: the Column survives replacing the
built-in Divi form with a Gravity Forms module, so the box and the `#bd-contact-form`
anchor keep working after the plugin is installed. It is never hidden by the nav button.

**The floating drawer** is a second instance that slides in from the right edge when the nav
envelope icon is pressed, on every page. It is plain form markup in the header Code module,
because a Divi module cannot be rendered inside the header and the header is the only global
slot. On a phone it becomes a bottom sheet.

- Hook: `Modules/contact/sections/03-contact-body.divi`, the Column inside the row labelled
  `Contact Form`. It carries `id="bd-contact-form"`, `class="bd-contact-form-card"` and the
  admin label `Contact Form Card`.
- Card surface, drawer, shared field styling, the Gravity Forms skin, the nav button and its
  script all live in the header Code module (admin label `BD Theme Toggle`) inside
  `Modules/header/manifest.json`. The nav button sits between the dark-mode button and the
  WhatsApp icon and only appears on scroll, exactly like `.bd-scroll-whatsapp`.
- Each block this tool owns is fenced by sentinels (`bd:form-card`, `bd:form-drawer`,
  `bd:form-drawer-script`) so an edit always propagates instead of being skipped.

### The floating form does not submit yet

A header Code module has no Divi form handler behind it, and Gravity Forms is not installed,
so the drawer cannot post anywhere. Rather than drop a filled-in form silently, submitting it
swaps the form for a short panel that hands the message to WhatsApp and says plainly that
Gravity Forms is not wired up. **When Gravity Forms is installed**, delete the drawer's
`submit` listener and the `.bd-form-drawer-done` block, then drop a `[gravityform id="…"]`
shortcode in their place. The `.gform_*` skin already covers `#bd-form-drawer`, so it will
match the inline card with no further CSS.

### Scoping rule that must not be broken

Field and Gravity Forms rules are generated per scope (`{s()}`, `{cs()}`, `{ds()}`, `{sd()}`
in the tool) rather than written as one scope plus a descendant. A selector list of
`#main-content .bd-contact-form-card,#bd-form-drawer .bd-field-error[hidden]` puts
`display:none` on the **first branch alone**, which hides the entire inline form. `validate`
fails on any `display:none` rule that targets a bare scope, so this cannot regress quietly.

Re-apply or check the whole change with:

```bash
python tools/add_contact_form_card.py apply
python tools/add_contact_form_card.py validate
```

`validate` also fails on an unsubstituted placeholder (`__WA__`, `{s(`), a duplicate
sentinel, a doubled `{{` brace (one of those silently kills a whole media query), the collapse
behaviour returning, or a `.gform_*` rule that names only one surface.

Verified 2026-10-03 in headless Chromium against the compiled export, not on the live site:
55 checks covering the inline card staying visible in both light and dark for both the native
Divi form and Gravity Forms markup; drawer geometry and slide-in; scrim fade; page scroll
lock; all four close paths; focus moved in, focus restored, and Tab and Shift+Tab trapped for
the whole drawer; per-field validation including a bad email; the WhatsApp hand-off link;
phone bottom sheet; the card padding and radius at the 980px and 767px breakpoints; and the drawer working on a page with no inline form at all.

## Current verified split counts

- `home`: 10 sections
- `about`: 4 sections
- `services`: 8 sections
- `contact`: 4 sections
- `header`: 1 section
- `footer`: 2 sections

The initial split/compile was verified on 2026-10-02: compiled payloads matched the originals exactly for all six exports.
