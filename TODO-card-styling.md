# BD Star Divi 5 – Card styling & dark mode TODOs

Found 2026-10-02 from screenshots of the live Cloudways homepage (light + dark).
Files: `bdstar-{home,about,contact,services,header,footer}-v5.json` in this folder.
Status key: DONE = fixed in the JSON in this folder (needs re-import + visual check), NOT AN ISSUE = turned out to be a screenshot artifact.

## Background (read first)

- Per-block card styling lives in JSON: `module.decoration.border` with `radius` INSIDE it (Divi 5 ignores a separate `borderRadius` key), plus `boxShadow`.
- The header export (`bdstar-header-v5.json`, search "BD card + media system") also has CSS for `.et_pb_column.et_pb_with_border/with_background` and `.et_pb_blurb.et_pb_with_border`. Evidence from dark-mode render: blurbs get these classes and the dark panel; columns do NOT (a column with a hard-coded JSON `background:#ffffff` stays white in dark mode). So do not give columns a JSON background.
- Dark theme = `html[data-bd-theme="dark"]`, localStorage key `bdstar-theme`.
- Editing rules: keep block comments byte-exact (two spaces before JSON, preserve `/-->` on self-closing blocks, escape `<`, `>`, `&` as `<` `>` `&`). After any scripted edit verify opens == closes + self-closing. Never re-run `fix_card_styles.py` (strips `/-->`).
- Screenshot caveat: sections with slide/fade animations (images, hero) render blank in a static capture until scrolled into view.

## TODOs

### 1. Ten Years counters styled as cards — DONE
Removed border/boxShadow from the four `1_4` columns in home. Label text still touches the edges only if a border is added again; no padding change needed without a box.

### 2. Text-only box styled as card ("5-STAR RATED, LICENSED & INSURED") — DONE
Removed border/shadow from that `column-inner` (the one wrapping two text modules).

### 3. Dark mode: Premium Services panel not full height — DONE (verify)
The card surface, 1px border, 12px radius, and shadow now live on the same blurb module, which receives the dark-mode background. The redundant column border is removed, and the blurb uses native `height:100%` inside the equal-height row. Verify after re-import in dark mode; the live page has not been updated or visually verified.

### 4. Fleet images: white frames in dark mode — DONE
Removed the image-level `boxShadow` (preset7, spread 10px, #f7f7f7) from the four fleet images.

### 5. Fleet & Journeys empty boxes — NOT AN ISSUE (likely)
All six image URLs return 200 and the image blocks have `src`. The blank tiles were images with slide-in animation not yet triggered in a static screenshot. If they stay blank on a real scrolled view, check the animation settings on those four image modules.

### 6. 5-Star section layout glitches — DONE
- White band above the left column: section had a preset7 `boxShadow` vertical 100px #ffffff; removed.
- Ghost/double cards: the two `column-inner` wrappers had their own card styling around blurbs that are already cards; removed from the wrappers.
- Placeholder "Branding" renamed to "Licensed & Insured"; both card titles set to 18px so heights match. If heights still differ, set the same `min-height` on both blurbs.
- Latest export refresh: set a responsive gutter between the two cards, made their 16px border radius and light shadow explicit with Divi's `boxShadow` preset, and reduced/framed the right-side image.
- Refreshed "Why Families Choose" with a restrained light section surface, a wider capped content row, and a contained, centered, framed image. Copy is unchanged.

### 7. Premium Services titles missing / list alignment — DONE
- Titles: the three legacy blurbs stored the title as a plain string (`"value":"Airport Transfers"`), Divi 5 needs `{"text":"Airport Transfers"}`. Converted.
- Lists: added `#main-content .et_pb_blurb_description ul{text-align:left;}` to the header CSS block.

### 8. Icons render as stray letters ("k", "b") — NOT AN ISSUE (likely)
Seen only on a local `file://` copy where the Divi icon font did not load. The live render shows the icons correctly. Re-check on the live site only.

### 9. Verify after re-import — TODO
- Re-import home (Replace Existing Content), screenshot light and dark:
  `chromium --headless=new --no-sandbox --virtual-time-budget=8000 --screenshot=out.png --window-size=1440,7000 URL`
  (Playwright's bundled browser crashes here; for dark, use a local copy of the page with `localStorage.setItem("bdstar-theme","dark")` injected.)
- Check Premium Services cards, the two Five-Star cards, the right-side image frame, and the refreshed Why Families section in desktop/mobile and light/dark modes.
- Pass criteria: real cards have visible rounded borders and shadows; dark panels fill card height with no border/background seam; images stay within their content columns.
- Not yet checked: about, contact, services pages (cards there were styled by `round_cards.py`; counters/text-only boxes there were not audited).
