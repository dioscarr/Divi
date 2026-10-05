#!/usr/bin/env python3
"""Box the Contact page message form and add the floating nav form drawer.

Two files are patched:

- ``Modules/contact/sections/03-contact-body.divi`` gets a hook on the Column that wraps
  the form (``id="bd-contact-form"`` / ``class="bd-contact-form-card"`` plus the admin
  label "Contact Form Card" so it is findable in the Layers panel). The inline form is
  never hidden by this tool; the nav drawer is a second, floating instance.
- ``Modules/header/manifest.json`` gets the card surface, the Gravity Forms skin, the nav
  toggle button, the drawer markup and the drawer script inside the existing header Code
  module, whose admin label is "BD Theme Toggle".

The card surface deliberately lives on the Column, not on the Contact Form module, so the
box and the ``#bd-contact-form`` anchor keep working when the built-in Divi form is
replaced by a Gravity Forms module once that plugin is installed. The drawer cannot host a
Divi module at all, so it ships as plain form markup that the same skin styles, and the
``.gform_*`` rules are generated for both surfaces from one scope list.

Escaping: the Code module's HTML/CSS/JS is a string inside a block's JSON. It is decoded
with :func:`json.loads` and re-encoded with ``json.dumps``, never hand-escaped.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

BASE = Path("/home/dioscarr/Work/divi-working-set")
CONTACT_SECTION = BASE / "Modules/contact/sections/03-contact-body.divi"
HEADER_MANIFEST = BASE / "Modules/header/manifest.json"

CARD_ID = "bd-contact-form"
CARD_CLASS = "bd-contact-form-card"
CARD_LABEL = "Contact Form Card"
ROW_LABEL = "Contact Form"
HEADER_CODE_LABEL = "BD Theme Toggle"
DRAWER_ID = "bd-form-drawer"
WHATSAPP = "https://wa.me/18299866861"

COLUMN_OPEN_RE = re.compile(r"(<!--\s*wp:divi/column\s+)(\{.*?\})(\s+)(-->|-->)", re.S)
CODE_BLOCK_RE = re.compile(r"(<!-- wp:divi/code\s+)(\{.*?\})(\s+/-->)", re.S)

# The surface owns the box in both places, so one rule set styles the inline card and the
# drawer. Selectors are never written as "{scope} .child": that expands to a comma list
# whose first branch is the bare scope, so a declaration like `display:none` silently lands
# on the whole inline card. Each descendant is expanded per scope instead.
CARD_SCOPE = "#main-content .bd-contact-form-card"
DRAWER_SCOPE = "#" + DRAWER_ID
DARK = 'html[data-bd-theme="dark"] '


def expand_scopes(css: str) -> str:
    """Expand {s(desc)}, {cs(desc)}, {ds(desc)} and {sd(desc)} into real selector lists."""

    def one(prefix_scope: str, desc: str) -> str:
        return prefix_scope + (" " + desc if desc else "")

    def sub(match: re.Match[str]) -> str:
        kind, desc = match.group(1), match.group(2).strip()
        if kind == "s":
            return one(CARD_SCOPE, desc) + "," + one(DRAWER_SCOPE, desc)
        if kind == "cs":
            return one(CARD_SCOPE, desc)
        if kind == "ds":
            return one(DRAWER_SCOPE, desc)
        if kind == "sd":
            return one(DARK + CARD_SCOPE, desc) + "," + one(DARK + DRAWER_SCOPE, desc)
        raise SystemExit(f"unknown scope placeholder {{{kind}(...)}}")

    return re.sub(r"\{(s|cs|ds|sd)\(([^)]*)\)\}", sub, css)


def read_text_exact(path: Path) -> str:
    with path.open("r", encoding="utf-8", newline="") as handle:
        return handle.read()


def write_text_exact(path: Path, text: str) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        handle.write(text)


def label_of(attrs: dict) -> str | None:
    return (
        attrs.get("module", {})
        .get("meta", {})
        .get("adminLabel", {})
        .get("desktop", {})
        .get("value")
    )


MARKUP_ANCHOR = '  <a class="bd-scroll-whatsapp" href="' + WHATSAPP + '"'

# ---------------------------------------------------------------------------
# nav toggle button
# ---------------------------------------------------------------------------

TOGGLE_BUTTON = (
    '  <button class="bd-form-toggle" type="button"'
    f' aria-controls="{DRAWER_ID}" aria-expanded="false"'
    ' aria-label="Open the message form" title="Open the message form">'
    '<span class="bd-form-toggle-icon" aria-hidden="true">✉</span></button>\n'
)

# The 2026-10-03 collapse variant is replaced in place by `apply`.
OLD_TOGGLE_BUTTON = (
    '  <button class="bd-form-toggle" type="button"'
    f' aria-controls="{CARD_ID}" aria-expanded="true"'
    ' aria-label="Hide the message form" title="Hide the message form">'
    '<span class="bd-form-toggle-icon" aria-hidden="true">✉</span></button>\n'
)

# ---------------------------------------------------------------------------
# floating drawer markup
# ---------------------------------------------------------------------------

DRAWER_MARKUP = """
<div class="bd-form-scrim" id="bd-form-scrim" aria-hidden="true"></div>
<aside class="bd-form-drawer" id="bd-form-drawer" role="dialog" aria-modal="true" aria-hidden="true" aria-labelledby="bd-form-drawer-title">
  <div class="bd-form-drawer-head">
    <div class="bd-form-drawer-headings">
      <h2 class="bd-form-drawer-title" id="bd-form-drawer-title">Send us a message</h2>
      <p class="bd-form-drawer-sub">Tell us what you need and we reply within one business day.</p>
    </div>
    <button class="bd-form-drawer-close" type="button" aria-label="Close the message form">×</button>
  </div>
  <div class="bd-form-drawer-body">
    <form class="bd-form-drawer-form" id="bd-form-drawer-form" novalidate>
      <p class="bd-field">
        <label class="bd-field-label" for="bd-fd-name">Full name</label>
        <input class="bd-field-input" id="bd-fd-name" name="name" type="text" autocomplete="name" required>
        <span class="bd-field-error" hidden>Please tell us your name.</span>
      </p>
      <p class="bd-field">
        <label class="bd-field-label" for="bd-fd-phone">Phone or WhatsApp</label>
        <input class="bd-field-input" id="bd-fd-phone" name="phone" type="tel" autocomplete="tel" required>
        <span class="bd-field-error" hidden>Please add a number we can reach you on.</span>
      </p>
      <p class="bd-field">
        <label class="bd-field-label" for="bd-fd-email">Email</label>
        <input class="bd-field-input" id="bd-fd-email" name="email" type="email" autocomplete="email" required>
        <span class="bd-field-error" hidden>Please check this email address.</span>
      </p>
      <p class="bd-field">
        <label class="bd-field-label" for="bd-fd-message">Your message</label>
        <textarea class="bd-field-input bd-field-textarea" id="bd-fd-message" name="message" rows="4" required></textarea>
        <span class="bd-field-error" hidden>Please add a short message.</span>
      </p>
      <button class="bd-form-drawer-submit" type="submit">Send Message</button>
      <p class="bd-form-drawer-alt">Prefer WhatsApp? <a href="__WA__" target="_blank" rel="noopener">Message us there</a>.</p>
    </form>
    <div class="bd-form-drawer-done" id="bd-form-drawer-done" hidden>
      <h3 class="bd-form-drawer-done-title">Ready to send</h3>
      <p class="bd-form-drawer-done-text">This floating form is not connected to Gravity Forms yet, so nothing was submitted. Send the same message on WhatsApp and we will pick it up from there.</p>
      <a class="bd-form-drawer-done-wa" id="bd-form-drawer-wa" href="__WA__" target="_blank" rel="noopener">Send on WhatsApp</a>
      <button class="bd-form-drawer-again" type="button">Back to the form</button>
    </div>
  </div>
</aside>
""".replace("__WA__", WHATSAPP)

# ---------------------------------------------------------------------------
# CSS
# ---------------------------------------------------------------------------

CARD_CSS = expand_scopes("""
/* ===== Contact message form: inline card + floating nav drawer =====
   The inline surface is on the Column that wraps the form, not on the form module, so the
   box and the #bd-contact-form anchor survive replacing the built-in Divi form with a
   Gravity Forms module. The drawer is a second, floating instance of the same form; it is
   additive and never hides the inline one. */
:root{
  --bd-form-card-surface:#ffffff;
  --bd-form-card-border:#e4e6ef;
  --bd-form-card-shadow:0 24px 54px -26px rgba(20,22,48,.34);
}
html[data-bd-theme="dark"]{
  --bd-form-card-surface:#141630;
  --bd-form-card-border:rgba(255,255,255,.16);
}

/* --- inline card --- */
{cs()}{
  scroll-margin-top:150px;
  background-color:var(--bd-form-card-surface);
  border:1px solid var(--bd-form-card-border);
  border-radius:18px;
  padding:40px 36px;
  box-shadow:var(--bd-form-card-shadow);
  transition:transform .3s ease,box-shadow .3s ease,border-color .3s ease;
}
{cs(:hover)}{
  transform:translateY(-3px);
  border-color:rgba(222,126,10,.42);
  box-shadow:0 32px 64px -28px rgba(20,22,48,.44);
}
html[data-bd-theme="dark"] {cs()}{
  background:#141630!important;
  background-color:#141630!important;
  background-image:none!important;
  border-color:rgba(255,255,255,.16)!important;
  box-shadow:0 24px 54px -22px rgba(0,0,0,.88)!important;
}
@media(max-width:980px){cs()}{padding:32px 26px;}
@media(max-width:767px){cs()}{padding:24px 18px;border-radius:14px;}
/* Inside the navy card the built-in Divi form labels must stay readable too. */
html[data-bd-theme="dark"] {cs( label)}{color:#d7d9e2!important;}
html[data-bd-theme="dark"] {cs( input::placeholder)},
html[data-bd-theme="dark"] {cs( textarea::placeholder)}{color:#b7bac7!important;}

/* --- drawer shell --- */
{ds()}{
  position:fixed;top:0;right:0;z-index:9991;
  display:flex;flex-direction:column;
  width:min(430px,100vw);max-width:100vw;
  height:100vh;height:100dvh;max-height:100vh;max-height:100dvh;
  background-color:var(--bd-form-card-surface);
  border-left:1px solid var(--bd-form-card-border);
  box-shadow:-28px 0 70px -30px rgba(20,22,48,.45);
  color:#353740;
  transform:translate3d(100%,0,0);visibility:hidden;
  transition:transform .38s cubic-bezier(.16,1,.3,1),visibility 0s linear .38s;
}
html.bd-form-open {ds()}{
  transform:translate3d(0,0,0);visibility:visible;
  transition:transform .38s cubic-bezier(.16,1,.3,1),visibility 0s linear 0s;
}
.bd-form-scrim{
  position:fixed;inset:0;z-index:9990;
  background:rgba(12,16,31,.62);
  backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);
  opacity:0;visibility:hidden;
  transition:opacity .3s ease,visibility 0s linear .3s;
}
html.bd-form-open .bd-form-scrim{
  opacity:1;visibility:visible;
  transition:opacity .3s ease,visibility 0s linear 0s;
}
html.bd-form-open,html.bd-form-open body{overflow:hidden;}

/* --- drawer chrome --- */
.bd-form-drawer-head{
  display:flex;align-items:flex-start;gap:14px;
  padding:26px 24px 18px;border-bottom:1px solid var(--bd-form-card-border);
}
.bd-form-drawer-headings{flex:1 1 auto;min-width:0;}
.bd-form-drawer-title{
  margin:0;font-family:Montserrat,sans-serif;font-weight:700;
  font-size:22px;line-height:1.25em;color:#141630;
}
.bd-form-drawer-sub{
  margin:7px 0 0;font-family:Montserrat,sans-serif;
  font-size:13px;line-height:1.5em;color:#747d88;
}
.bd-form-drawer-close{
  flex:0 0 auto;display:grid;place-items:center;width:40px;height:40px;padding:0;
  border:1px solid var(--bd-form-card-border);border-radius:50%;cursor:pointer;
  background:transparent;color:#141630;font:300 27px/1 Arial,sans-serif;
  transition:background-color .2s ease,border-color .2s ease,color .2s ease;
}
.bd-form-drawer-close:hover{border-color:#de7e0a;color:#de7e0a;}
.bd-form-drawer-close:focus-visible{outline:3px solid #f0952e;outline-offset:3px;}
.bd-form-drawer-body{flex:1 1 auto;min-height:0;overflow-y:auto;padding:24px;}
/* Phone: a bottom sheet, so the thumb reaches the submit button. */
@media(max-width:767px){
  {ds()}{
    top:auto;bottom:0;left:0;right:0;
    width:100%;height:auto;max-height:88vh;max-height:88dvh;
    border-left:0;border-top:1px solid var(--bd-form-card-border);
    border-radius:18px 18px 0 0;
    transform:translate3d(0,100%,0);
  }
  html.bd-form-open {ds()}{transform:translate3d(0,0,0);}
  .bd-form-drawer-head{padding:20px 18px 14px;}
  .bd-form-drawer-body{padding:18px;}
  .bd-form-drawer-title{font-size:19px;}
}

/* --- nav toggle: same circle size and scroll reveal as the WhatsApp icon --- */
.bd-form-toggle{display:none;align-items:center;justify-content:center;flex:0 0 auto;align-self:center;width:38px;height:38px;margin:0;padding:0;border:0;border-radius:50%;background:#de7e0a;color:#fff;cursor:pointer;box-shadow:0 8px 18px rgba(222,126,10,.30);font:700 18px/1 Arial,sans-serif;transition:transform .2s ease,box-shadow .2s ease,background-color .2s ease,color .2s ease;}
.bd-form-toggle:hover{transform:translateY(-1px);box-shadow:0 10px 22px rgba(222,126,10,.42);}
.bd-form-toggle:focus-visible{outline:3px solid #f0952e;outline-offset:3px;}
html.bd-hdr-scrolled .bd-form-toggle{display:inline-flex;}
html.bd-form-open .bd-form-toggle{background:#fcd21d;color:#141630;box-shadow:0 8px 18px rgba(252,210,29,.34);}

/* --- shared field styling: the inline card, the drawer, and Gravity Forms --- */
{s(.bd-field)}{margin:0 0 18px;}
{s(.bd-field-label)}{
  display:block;margin:0 0 7px;
  font-family:Montserrat,sans-serif;font-weight:700;font-size:12px;letter-spacing:.08em;
  text-transform:uppercase;color:#747d88;
}
{s(.bd-field-input)}{
  display:block;width:100%;margin:0;padding:13px 15px;
  border:1px solid #dfe1ea;border-radius:10px;
  background-color:#ffffff;color:#353740;
  font-family:Montserrat,sans-serif;font-size:16px;line-height:1.5em;
  box-shadow:0 1px 2px rgba(20,22,48,.05);
  transition:border-color .2s ease,box-shadow .2s ease;
}
{s(.bd-field-textarea)}{min-height:118px;resize:vertical;}
{s(.bd-field-input::placeholder)}{color:#a8adb8;}
{s(.bd-field-input:focus)}{
  border-color:#de7e0a;box-shadow:0 0 0 3px rgba(222,126,10,.18);outline:none;
}
{s(.bd-field-invalid .bd-field-input)}{border-color:#b42318;box-shadow:0 0 0 3px rgba(180,35,24,.14);}
{s(.bd-field-error)}{display:block;margin:6px 0 0;color:#b42318;font-family:Montserrat,sans-serif;font-size:13px;line-height:1.4em;}
{s(.bd-field-error[hidden])}{display:none;}

/* Gravity Forms is not installed yet, so everything from here down is inert until the
   plugin is added. It only skins the form to match: the inline Column and the drawer both
   already own the surface and the spacing, so no rule here can move page layout. A
   [gravityform] shortcode dropped into either surface inherits the identical skin. */
{s(.gform_wrapper)}{margin:0;padding:0;max-width:none;}
{s(.gform_wrapper .gform_heading)}{
  margin:0 0 22px;padding:0;text-align:center;
  font-family:Montserrat,sans-serif;font-weight:700;font-size:24px;line-height:1.3em;
  color:#141630;
}
{s(.gfield)}{margin:0 0 20px;}
{s(.gfield_label)}{
  display:block;margin:0 0 7px;
  font-family:Montserrat,sans-serif;font-weight:700;font-size:12px;letter-spacing:.08em;
  text-transform:uppercase;color:#747d88;
}
{s(.gfield_required)}{color:#de7e0a;text-decoration:none;}
{s(.ginput_container input[type=text])},
{s(.ginput_container input[type=email])},
{s(.ginput_container input[type=tel])},
{s(.ginput_container input[type=number])},
{s(.ginput_container input[type=date])},
{s(.ginput_container input[type=url])},
{s(.ginput_container input[type=search])},
{s(.ginput_container select)},
{s(.ginput_container textarea)}{
  width:100%;height:auto;margin:0;padding:13px 15px;
  border:1px solid #dfe1ea;border-radius:10px;
  background-color:#ffffff;color:#353740;
  font-family:Montserrat,sans-serif;font-size:16px;line-height:1.5em;
  box-shadow:0 1px 2px rgba(20,22,48,.05);
  transition:border-color .2s ease,box-shadow .2s ease;
}
{s(.ginput_container textarea)}{min-height:150px;}
{s(.ginput_container input:focus)},
{s(.ginput_container select:focus)},
{s(.ginput_container textarea:focus)}{
  border-color:#de7e0a;box-shadow:0 0 0 3px rgba(222,126,10,.18);outline:none;
}
{s(.gform_wrapper .gform_button)},
{ds(.bd-form-drawer-submit)}{
  display:block;width:100%;padding:15px 38px;border:5px solid transparent;border-radius:100px;
  background-color:#de7e0a;color:#ffffff;cursor:pointer;text-align:center;text-decoration:none;
  font-family:Montserrat,sans-serif;font-weight:700;font-size:14px;letter-spacing:2px;
  text-transform:uppercase;line-height:1;
  transition:background-color .2s ease,color .2s ease,transform .2s ease;
}
{s(.gform_wrapper .gform_button:hover)},
{ds(.bd-form-drawer-submit:hover)}{background-color:#c96c07;color:#ffffff;transform:translateY(-1px);}
{s(.gform_wrapper .gform_footer)}{margin:8px 0 0;}
{s(.gform_validation_errors)}{margin:0 0 18px;padding:0;border:0;}
{s(.gform_validation_errors .validation_message)}{margin:0;color:#b42318;font-family:Montserrat,sans-serif;font-size:13px;}
{s(.validation_message)}{display:block;margin:6px 0 0;color:#b42318;font-family:Montserrat,sans-serif;font-size:13px;}
{s(.gform_wrapper .gform_confirmation)}{
  margin:0;padding:18px 20px;border:1px solid #b7e0c5;border-left:4px solid #2e9e5b;
  border-radius:12px;background-color:#eefaf2;color:#1f6b3f;
  font-family:Montserrat,sans-serif;font-size:15px;line-height:1.6em;
}
{s(.gform_wrapper .gform_anchor)}{display:none;}
{s(.gform_wrapper .gform_complex_field)}{display:none;}
{s(.gform_wrapper .gform_hidden)}{display:none;}

/* --- drawer extras --- */
.bd-form-drawer-alt{
  margin:14px 0 0;font-family:Montserrat,sans-serif;font-size:13px;line-height:1.5em;
  color:#747d88;text-align:center;
}
.bd-form-drawer-alt a{color:#de7e0a;}
.bd-form-drawer-done{
  padding:22px 20px;border:1px solid var(--bd-form-card-border);
  border-left:4px solid #fcd21d;border-radius:12px;
  background-color:rgba(252,210,29,.08);
}
.bd-form-drawer-done[hidden]{display:none;}
.bd-form-drawer-done-title{
  margin:0 0 9px;font-family:Montserrat,sans-serif;font-weight:700;
  font-size:17px;line-height:1.3em;color:#141630;
}
.bd-form-drawer-done-text{
  margin:0 0 18px;font-family:Montserrat,sans-serif;font-size:14px;line-height:1.6em;color:#747d88;
}
.bd-form-drawer-done-wa{
  display:block;padding:14px 20px;border-radius:100px;
  background-color:#25d366;color:#fff;text-align:center;text-decoration:none;
  font-family:Montserrat,sans-serif;font-weight:700;font-size:13px;letter-spacing:1px;
  text-transform:uppercase;
}
.bd-form-drawer-done-wa:hover{background-color:#1fbe59;}
.bd-form-drawer-again{
  display:block;width:100%;margin:12px 0 0;padding:11px 20px;cursor:pointer;
  border:1px solid var(--bd-form-card-border);border-radius:100px;
  background:transparent;color:#747d88;
  font-family:Montserrat,sans-serif;font-weight:700;font-size:12px;
  letter-spacing:1px;text-transform:uppercase;
}
.bd-form-drawer-again:hover{border-color:#de7e0a;color:#de7e0a;}

/* --- drawer dark mode: it lives in the header, outside #main-content --- */
html[data-bd-theme="dark"] {ds()}{
  background:#141630!important;background-color:#141630!important;background-image:none!important;
  border-color:rgba(255,255,255,.16)!important;box-shadow:-28px 0 70px -24px rgba(0,0,0,.9)!important;
  color:#ffffff;
}
html[data-bd-theme="dark"] .bd-form-drawer-title{color:#ffffff;}
html[data-bd-theme="dark"] .bd-form-drawer-sub,
html[data-bd-theme="dark"] .bd-form-drawer-alt,
html[data-bd-theme="dark"] .bd-form-drawer-done-text{color:#d7d9e2;}
html[data-bd-theme="dark"] .bd-form-drawer-close{border-color:rgba(255,255,255,.24);color:#ffffff;}
html[data-bd-theme="dark"] .bd-form-drawer-close:hover{border-color:#fcd21d;color:#fcd21d;}
html[data-bd-theme="dark"] .bd-form-drawer-done{
  background-color:rgba(252,210,29,.10);border-color:rgba(255,255,255,.16);border-left-color:#fcd21d;
}
html[data-bd-theme="dark"] .bd-form-drawer-done-title{color:#ffffff;}
html[data-bd-theme="dark"] .bd-form-drawer-again{border-color:rgba(255,255,255,.24);color:#d7d9e2;}

/* --- dark mode for the shared field rules, per scope --- */
{sd(.bd-field-label)},
{sd(.gfield_label)}{color:#d7d9e2;}
{sd(.bd-field-input)},
{sd(.ginput_container input)},
{sd(.ginput_container select)},
{sd(.ginput_container textarea)}{
  background-color:#1c1f3d!important;color:#ffffff!important;
  border-color:rgba(255,255,255,.22)!important;
}
{sd(.bd-field-input::placeholder)}{color:#b7bac7!important;}
{sd(.bd-field-invalid .bd-field-input)}{border-color:#f97066!important;}
{sd(.gform_wrapper .gform_heading)}{color:#ffffff;}
{sd(.gform_wrapper .gform_confirmation)}{
  background-color:#141630;border-color:rgba(255,255,255,.16);border-left-color:#fcd21d;color:#ffffff;
}

@media(prefers-reduced-motion:reduce){
  {cs()}{transition:none!important;}
  {cs(:hover)}{transform:none!important;}
  {ds()}{transition:none!important;}
  html.bd-form-open {ds()}{transition:none!important;}
  .bd-form-scrim{transition:none!important;}
  html.bd-form-open .bd-form-scrim{transition:none!important;}
}
""")

# ---------------------------------------------------------------------------
# drawer script
# ---------------------------------------------------------------------------

DRAWER_SCRIPT = """
<script>
(function(){
  var root=document.documentElement;
  var button=document.querySelector('.bd-form-toggle');
  var drawer=document.getElementById('bd-form-drawer');
  var scrim=document.getElementById('bd-form-scrim');
  if(!button||!drawer||!scrim)return;
  // The header actions row is a flex container, and any transformed ancestor would trap a
  // position:fixed overlay. The video modal already moves its dialog to the end of body for
  // the same reason, so do it here rather than relying on the header never being animated.
  document.body.appendChild(scrim);
  document.body.appendChild(drawer);
  var WA='__WA__';
  var form=document.getElementById('bd-form-drawer-form');
  var done=document.getElementById('bd-form-drawer-done');
  var doneWa=document.getElementById('bd-form-drawer-wa');
  var again=drawer.querySelector('.bd-form-drawer-again');
  var lastFocus=null;
  var FOCUSABLE='a[href],button:not([disabled]),input:not([disabled]),textarea:not([disabled]),select:not([disabled])';
  // form.name / form.email would resolve to the form's own DOM properties, not the inputs.
  var f={
    name:form.querySelector('#bd-fd-name'),
    phone:form.querySelector('#bd-fd-phone'),
    email:form.querySelector('#bd-fd-email'),
    message:form.querySelector('#bd-fd-message')
  };

  function forEach_(scope,selector,fn){
    var nodes=scope?scope.querySelectorAll(selector):[];
    for(var i=0;i<nodes.length;i++)fn(nodes[i],i);
  }

  function isOpen(){return root.classList.contains('bd-form-open');}
  function setLabel(text){
    button.setAttribute('aria-label',text);
    button.setAttribute('title',text);
  }
  function open(){
    if(isOpen())return;
    lastFocus=document.activeElement;
    root.classList.add('bd-form-open');
    drawer.setAttribute('aria-hidden','false');
    button.setAttribute('aria-expanded','true');
    setLabel('Close the message form');
    var first=drawer.querySelector('.bd-field-input');
    if(first)first.focus();
  }
  function close(){
    if(!isOpen())return;
    root.classList.remove('bd-form-open');
    drawer.setAttribute('aria-hidden','true');
    button.setAttribute('aria-expanded','false');
    setLabel('Open the message form');
    if(lastFocus&&lastFocus.focus)lastFocus.focus();
  }
  function fieldOf(input){
    return input&&input.closest?input.closest('.bd-field'):null;
  }
  function validate(){
    var ok=true;
    var inputs=form.querySelectorAll('.bd-field-input');
    for(var i=0;i<inputs.length;i++){
      var input=inputs[i];
      var wrap=fieldOf(input);
      var value=String(input.value||'').trim();
      var bad=!value;
      if(!bad&&input.type==='email')bad=!/^[^@\\s]+@[^@\\s]+\\.[^@\\s]+$/.test(value);
      if(wrap)wrap.classList.toggle('bd-field-invalid',bad);
      var msg=wrap?wrap.querySelector('.bd-field-error'):null;
      if(msg)msg.hidden=!bad;
      if(bad&&ok){
        ok=false;
        input.setAttribute('aria-invalid','true');
        input.focus();
      }else if(!bad){
        input.removeAttribute('aria-invalid');
      }
    }
    return ok;
  }
  forEach_(form,'.bd-field-input',function(input){
    input.addEventListener('input',function(){
      var wrap=fieldOf(input);
      if(!wrap)return;
      wrap.classList.remove('bd-field-invalid');
      var msg=wrap.querySelector('.bd-field-error');
      if(msg)msg.hidden=true;
      input.removeAttribute('aria-invalid');
    });
  });
  form.addEventListener('submit',function(event){
    event.preventDefault();
    if(!validate())return;
    // The drawer is plain markup in the global header, so there is no Divi form handler
    // behind it yet. Hand the message to WhatsApp instead of silently dropping it, and
    // say plainly that Gravity Forms still needs wiring. Once GF is installed, delete this
    // listener and the .bd-form-drawer-done block, and put a [gravityform] shortcode here.
    var lines=['New message from the website',
      'Name: '+f.name.value.trim(),
      'Phone: '+f.phone.value.trim(),
      'Email: '+f.email.value.trim(),
      '',
      f.message.value.trim()];
    doneWa.href=WA+'?text='+encodeURIComponent(lines.join('\\n'));
    form.hidden=true;
    done.hidden=false;
    doneWa.focus();
  });
  again.addEventListener('click',function(){
    done.hidden=true;
    form.hidden=false;
    var first=form.querySelector('.bd-field-input');
    if(first)first.focus();
  });
  document.addEventListener('click',function(event){
    var target=event.target;
    if(!target||!target.closest)return;
    if(target.closest('.bd-form-toggle')){
      event.preventDefault();
      if(isOpen())close();else open();
      return;
    }
    if(target.closest('.bd-form-drawer-close')||target===scrim){
      event.preventDefault();
      close();
    }
  });
  document.addEventListener('keydown',function(event){
    if(!isOpen())return;
    if(event.key==='Escape'||event.key==='Esc'){
      event.preventDefault();
      close();
      return;
    }
    if(event.key!=='Tab')return;
    var list=[];
    forEach_(drawer,FOCUSABLE,function(node){if(node.offsetParent!==null)list.push(node);});
    if(!list.length)return;
    var first=list[0];
    var last=list[list.length-1];
    if(event.shiftKey&&document.activeElement===first){
      event.preventDefault();
      last.focus();
    }else if(!event.shiftKey&&document.activeElement===last){
      event.preventDefault();
      first.focus();
    }
  });
  // A legacy #bd-contact-form link still scrolls to the inline card; the drawer is additive.
  if(String(location.hash||'').toLowerCase()==='#bd-contact-form'){
    var inlineCard=document.getElementById('bd-contact-form');
    if(inlineCard&&inlineCard.scrollIntoView){
      setTimeout(function(){
        try{inlineCard.scrollIntoView({behavior:'smooth',block:'center'});}catch(e){inlineCard.scrollIntoView();}
      },320);
    }
  }
})();
</script>
""".replace("__WA__", WHATSAPP)

# The 2026-10-03 collapse script, replaced in place by `apply`.
OLD_TOGGLE_SCRIPT = """
<script>
(function(){
  var root=document.documentElement;
  var PANEL='#bd-contact-form';
  var button=document.querySelector('.bd-form-toggle');
  if(!button)return;
  var panel=null;

  function findPanel(){
    panel=document.querySelector(PANEL);
    return !!panel;
  }
  function setOpen(open){
    root.classList.toggle('bd-form-collapsed',!open);
    button.setAttribute('aria-expanded',open?'true':'false');
    var label=open?'Hide the message form':'Show the message form';
    button.setAttribute('aria-label',label);
    button.setAttribute('title',label);
  }
  function scrollToPanel(){
    if(!panel||!panel.scrollIntoView)return;
    try{panel.scrollIntoView({behavior:'smooth',block:'center'});}catch(e){panel.scrollIntoView();}
  }
  function start(){
    setOpen(true);
    if(!findPanel()){
      button.setAttribute('aria-label','Go to the contact form');
      button.setAttribute('title','Go to the contact form');
      return;
    }
    if(String(location.hash||'').toLowerCase()==='#bd-contact-form'){
      setTimeout(scrollToPanel,320);
    }
  }
  document.addEventListener('click',function(event){
    var target=event.target;
    if(!target||!target.closest)return;
    if(!target.closest('.bd-form-toggle'))return;
    event.preventDefault();
    if(findPanel()){
      var collapsed=root.classList.contains('bd-form-collapsed');
      setOpen(collapsed);
      if(collapsed)scrollToPanel();
      return;
    }
    location.href='/contact/#bd-contact-form';
  });
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded',start);
  }else{
    start();
  }
})();
</script>
"""

OLD_CSS_TAIL = """
/* Nav toggle: same circle size, same scroll reveal and same press feel as the WhatsApp
   icon, in the brand orange so the two round buttons never read as one control. */
.bd-form-toggle{display:none;align-items:center;justify-content:center;flex:0 0 auto;align-self:center;width:38px;height:38px;margin:0;padding:0;border:0;border-radius:50%;background:#de7e0a;color:#fff;cursor:pointer;box-shadow:0 8px 18px rgba(222,126,10,.30);font:700 18px/1 Arial,sans-serif;transition:transform .2s ease,box-shadow .2s ease,background-color .2s ease,color .2s ease;}
.bd-form-toggle:hover{transform:translateY(-1px);box-shadow:0 10px 22px rgba(222,126,10,.42);}
.bd-form-toggle:focus-visible{outline:3px solid #f0952e;outline-offset:3px;}
html.bd-hdr-scrolled .bd-form-toggle{display:inline-flex;}
html.bd-form-collapsed .bd-form-toggle{background:#fcd21d;color:#141630;box-shadow:0 8px 18px rgba(252,210,29,.34);}
html.bd-form-collapsed #main-content .bd-contact-form-card{display:none;}
"""


def patch_contact_section() -> None:
    text = read_text_exact(CONTACT_SECTION)
    row = text.index('"adminLabel":{"desktop":{"value":"%s"}' % ROW_LABEL)
    match = COLUMN_OPEN_RE.search(text, row)
    if not match:
        raise SystemExit(f"contact section: no Column after the '{ROW_LABEL}' row")
    attrs = json.loads(match.group(2))
    module = attrs.setdefault("module", {})
    module["meta"] = {"adminLabel": {"desktop": {"value": CARD_LABEL}}}
    module.setdefault("advanced", {})["htmlAttributes"] = {
        "desktop": {"value": {"id": CARD_ID, "class": CARD_CLASS}}
    }
    replacement = (
        match.group(1)
        + json.dumps(attrs, separators=(",", ":"), ensure_ascii=False)
        + match.group(3)
        + match.group(4)
    )
    write_text_exact(CONTACT_SECTION, text[: match.start()] + replacement + text[match.end():])
    print(f"updated {CONTACT_SECTION}")


def header_code_content(text: str) -> tuple[re.Match[str], dict, str]:
    for match in CODE_BLOCK_RE.finditer(text):
        attrs = json.loads(match.group(2))
        if label_of(attrs) == HEADER_CODE_LABEL:
            return match, attrs, attrs["content"]["innerContent"]["desktop"]["value"]
    raise SystemExit(f"header Code module labelled '{HEADER_CODE_LABEL}' was not found")


CSS_BEGIN = "/* bd:form-card:begin */"
CSS_END = "/* bd:form-card:end */"
MARKUP_BEGIN = "<!-- bd:form-drawer:begin -->"
MARKUP_END = "<!-- bd:form-drawer:end -->"
SCRIPT_BEGIN = "<!-- bd:form-drawer-script:begin -->"
SCRIPT_END = "<!-- bd:form-drawer-script:end -->"

# Older revisions of this tool were inserted without sentinels, so each block can also be
# recognised by the marker it used to start with.
LEGACY_CSS_STARTS = (
    "/* ===== Contact message form card =====",
    "/* ===== Contact message form: inline card + floating nav drawer =====",
)


def replace_owned_block(content: str, begin: str, end: str, payload: str, legacy_starts=()):
    """Rewrite the region this tool owns, whatever revision produced it.

    Returns (content, action). Without sentinels the region is located by a legacy marker,
    which is what lets a later edit to CARD_CSS reach a header that a previous run patched.
    """
    if begin in content and end in content:
        head = content[: content.index(begin)]
        rest = content[content.index(begin) :]
        tail = rest[rest.index(end) + len(end) :]
        return head + begin + "\n" + payload.strip("\n") + "\n" + end + tail, "rewrote"
    for marker in legacy_starts:
        if marker in content:
            stop = content.index("</style>", content.index(marker))
            wrapped = begin + "\n" + payload.strip("\n") + "\n" + end
            return content[: content.index(marker)].rstrip("\n") + "\n" + wrapped + "\n" + content[stop:], "migrated"
    return content, "absent"


def splice_before_anchor(content: str, anchor: str, block: str) -> str:
    if content.count(anchor) != 1:
        raise SystemExit("header: the WhatsApp icon anchor was not found exactly once")
    return content.replace(anchor, block + anchor, 1)


def patch_header_manifest() -> None:
    manifest = json.loads(read_text_exact(HEADER_MANIFEST))
    if len(manifest["parts"]) != 1 or manifest["parts"][0]["kind"] != "raw":
        raise SystemExit("header manifest is expected to hold a single raw part")
    text = manifest["parts"][0]["text"] or ""
    match, attrs, content = header_code_content(text)

    if OLD_TOGGLE_BUTTON in content:
        content = content.replace(OLD_TOGGLE_BUTTON, TOGGLE_BUTTON, 1)
        print("migrated the nav toggle button from collapse to drawer semantics")

    content, how = replace_owned_block(
        content, CSS_BEGIN, CSS_END, CARD_CSS, LEGACY_CSS_STARTS
    )
    if how == "absent":
        if "--bd-form-card-surface" in content:
            raise SystemExit("header: an unrecognised form CSS block is already present")
        if content.count("</style>") != 1:
            raise SystemExit("header: expected exactly one </style> in the Code module")
        content = content.replace(
            "</style>", "\n" + CSS_BEGIN + "\n" + CARD_CSS.strip("\n") + "\n" + CSS_END + "\n</style>", 1
        )
        how = "inserted"
    print(f"{how} the card + drawer CSS block")

    if 'class="bd-form-toggle"' not in content:
        content = splice_before_anchor(content, MARKUP_ANCHOR, TOGGLE_BUTTON)

    content, how = replace_owned_block(content, MARKUP_BEGIN, MARKUP_END, DRAWER_MARKUP)
    if how == "absent":
        # A pre-sentinel drawer is recognised by its own markup and replaced in place.
        if f'id="{DRAWER_ID}"' in content:
            head = content[: content.index('<div class="bd-form-scrim"')]
            rest = content[content.index('<div class="bd-form-scrim"') :]
            content = head.rstrip("\n") + "\n" + MARKUP_BEGIN + "\n" + DRAWER_MARKUP.strip("\n") + "\n" + MARKUP_END + "\n" + rest[rest.index("</aside>") + len("</aside>") :].lstrip("\n")
            how = "migrated"
        else:
            content = splice_before_anchor(content, MARKUP_ANCHOR, MARKUP_BEGIN + "\n" + DRAWER_MARKUP.strip("\n") + "\n" + MARKUP_END + "\n")
            how = "inserted"
    print(f"{how} the drawer markup block")

    # Both the collapse script and the drawer script start identically, so the whole
    # script block is matched structurally and rewritten.
    toggle_script = re.compile(
        r"<script>\n\(function\(\)\{\n  var root=document\.documentElement;\n"
        r"  var button=document\.querySelector\('\.bd-form-toggle'\);.*?\n\}\)\(\);\n</script>",
        re.S,
    )
    wrapped = SCRIPT_BEGIN + "\n" + DRAWER_SCRIPT.strip("\n") + "\n" + SCRIPT_END
    content, how = replace_owned_block(content, SCRIPT_BEGIN, SCRIPT_END, DRAWER_SCRIPT)
    if how == "absent":
        if toggle_script.search(content):
            content = toggle_script.sub(lambda _: wrapped, content, count=1)
            how = "migrated"
        elif "bd-form-scrim" not in content:
            content = content + "\n" + wrapped + "\n"
            how = "inserted"
    print(f"{how} the drawer script block")

    # Earlier revisions nested their sentinels, which left inert duplicate markers behind.
    # They are comments, so keeping only the first of each is safe and makes the block
    # boundaries unambiguous.
    for sentinel in (CSS_BEGIN, CSS_END, MARKUP_BEGIN, MARKUP_END, SCRIPT_BEGIN, SCRIPT_END):
        first = content.find(sentinel)
        if first == -1:
            continue
        cut = first + len(sentinel)
        content = content[:cut] + content[cut:].replace(sentinel, "")
    for sentinel in (CSS_BEGIN, CSS_END, MARKUP_BEGIN, MARKUP_END, SCRIPT_BEGIN, SCRIPT_END):
        if content.count(sentinel) != 1:
            raise SystemExit(f"header has {content.count(sentinel)} copies of {sentinel!r}, expected 1")

    attrs["content"]["innerContent"]["desktop"]["value"] = content
    # ensure_ascii=False keeps the theme glyphs as characters here; the compile step's
    # outer json.dumps re-escapes them, which is the single-escaped form Divi exports.
    replacement = (
        match.group(1)
        + json.dumps(attrs, separators=(",", ":"), ensure_ascii=False)
        + match.group(3)
    )
    text = text[: match.start()] + replacement + text[match.end() :]
    manifest["parts"][0]["text"] = text
    write_text_exact(HEADER_MANIFEST, json.dumps(manifest, indent=2, ensure_ascii=False))
    print(f"updated {HEADER_MANIFEST}")


def validate() -> None:
    section = read_text_exact(CONTACT_SECTION)
    for token in (CARD_ID, CARD_CLASS, CARD_LABEL):
        if token not in section:
            raise SystemExit(f"contact section is missing {token}")
    match = COLUMN_OPEN_RE.search(section, section.index('"adminLabel":{"desktop":{"value":"%s"}' % ROW_LABEL))
    attrs = json.loads(match.group(2))
    html_attrs = attrs["module"]["advanced"]["htmlAttributes"]["desktop"]["value"]
    if html_attrs != {"id": CARD_ID, "class": CARD_CLASS}:
        raise SystemExit(f"unexpected card html attributes: {html_attrs}")

    _, _, content = header_code_content(json.loads(read_text_exact(HEADER_MANIFEST))["parts"][0]["text"] or "")

    # The inline form must stay visible: no rule may hide the card any more.
    if "bd-form-collapsed" in content:
        raise SystemExit("the collapse behaviour is still present; the inline form must stay visible")

    if content.count('class="bd-form-toggle"') != 1:
        raise SystemExit("header markup must carry exactly one .bd-form-toggle button")
    if f'aria-controls="{DRAWER_ID}"' not in content:
        raise SystemExit(f"nav toggle button is not wired to {DRAWER_ID}")
    if 'aria-expanded="false"' not in content:
        raise SystemExit("nav toggle button must start collapsed")

    for token in (
        f'id="{DRAWER_ID}"',
        'id="bd-form-scrim"',
        'id="bd-form-drawer-form"',
        'id="bd-form-drawer-done"',
        'class="bd-form-drawer-close"',
        'role="dialog"',
    ):
        if token not in content:
            raise SystemExit(f"drawer markup is missing {token}")
    for field in ("bd-fd-name", "bd-fd-phone", "bd-fd-email", "bd-fd-message"):
        if field not in content:
            raise SystemExit(f"drawer form is missing the {field} field")
    if content.count('id="bd-form-drawer"') != 1:
        raise SystemExit("drawer markup must carry exactly one #bd-form-drawer element")

    style, tail = content.split("</style>", 1)
    for token in (
        "--bd-form-card-surface",
        "html.bd-hdr-scrolled .bd-form-toggle",
        "html.bd-form-open #bd-form-drawer",
        ".bd-form-scrim",
        "max-width:767px",
        "prefers-reduced-motion",
    ):
        if token not in style:
            raise SystemExit(f"header CSS is missing {token}")
    if "bd-contact-form-card" not in style:
        raise SystemExit("header CSS is missing the inline card surface")
    # An unbalanced `{cs()}` inside an extra pair of braces expands to "{{#main-content ...}}"
    # and the whole media query is dropped by the parser, so the responsive card padding
    # silently stops applying with no other error to notice.
    for mo in re.finditer(r"\{\{", style):
        raise SystemExit(f"header CSS has a doubled brace near {style[mo.start() - 40:mo.start() + 40]!r}")
    # The Gravity Forms skin must cover both surfaces, or a shortcode dropped into the
    # drawer renders unstyled. Each rule's whole selector list has to name both scopes.
    gform_lists = [
        selectors
        for selectors, _ in re.findall(r"([^{}]+)\{([^}]*)\}", style)
        if ".gform_" in selectors
    ]
    if not gform_lists:
        raise SystemExit("header CSS is missing the Gravity Forms skin")
    for selectors in gform_lists:
        parts = [part.strip() for part in selectors.split(",")]
        touching = [part for part in parts if ".gform_" in part]
        if not any(part.startswith(CARD_SCOPE) or CARD_SCOPE in part for part in touching):
            raise SystemExit(f"Gravity Forms rule is missing the inline card scope: {selectors.strip()[:120]}")
        if not any(part.startswith(DRAWER_SCOPE) or DRAWER_SCOPE in part for part in touching):
            raise SystemExit(f"Gravity Forms rule is missing the drawer scope: {selectors.strip()[:120]}")
    if DRAWER_SCOPE not in style:
        raise SystemExit("header CSS never mentions the drawer scope")

    # Regression guard. A selector list written as "{scope} .child" expands so that its
    # first branch is the bare scope, so a declaration such as `display:none` lands on the
    # whole inline card and the form silently disappears. No rule may target a bare scope
    # with display:none; only real descendants may be hidden.
    for selectors, body in re.findall(r"([^{}]+)\{([^}]*)\}", style):
        if not re.search(r"display\s*:\s*none", body):
            continue
        for selector in selectors.split(","):
            if selector.strip() in (CARD_SCOPE, DRAWER_SCOPE):
                raise SystemExit(
                    "a display:none rule targets the bare "
                    f"{selector.strip()} scope and would hide the whole surface: "
                    f"{selectors.strip()}"
                )
    for token in ("{s(", "{cs(", "{ds(", "{sd("):
        if token in style:
            raise SystemExit(f"header CSS still contains an unexpanded scope placeholder {token}")
    if re.search(r"#main-content \.bd-contact-form-card\s*,", style):
        raise SystemExit("header CSS contains a bare card scope inside a selector list")

    for token in ("bd-form-open", "Escape", "lastFocus", "forEach_", "aria-expanded"):
        if token not in tail:
            raise SystemExit(f"drawer script is missing {token}")
    # A string placeholder that was never substituted emits literal `" + WHATSAPP + "`
    # into the JavaScript and silently breaks the hand-off link, so assert it is absent.
    for leak in ('" + WHATSAPP + "', "' + WHATSAPP + '", "__WA__", '" + DRAWER_ID'):
        if leak in content:
            raise SystemExit(f"header contains an unsubstituted placeholder: {leak}")
    if f"var WA='{WHATSAPP}';" not in tail:
        raise SystemExit("drawer script is missing the real WhatsApp endpoint")
    if "bd-form-scrim" not in tail:
        raise SystemExit("drawer script is not wired to the scrim")
    if "document.body.appendChild(drawer)" not in tail:
        raise SystemExit("drawer script must move the drawer to the end of body")
    if tail.count("addEventListener('keydown'") != 1:
        raise SystemExit("drawer script must have exactly one keydown handler (Esc and Tab)")
    if tail.count("addEventListener('submit'") != 1:
        raise SystemExit("drawer script must have exactly one submit handler")

    print(
        "inline card hook, shared field + Gravity Forms skin for both surfaces, "
        "and the floating nav drawer are all present"
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("apply", "validate"))
    args = parser.parse_args()
    if args.command == "apply":
        patch_contact_section()
        patch_header_manifest()
    validate()


if __name__ == "__main__":
    main()