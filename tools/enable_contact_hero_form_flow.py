#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
hero_path = ROOT / 'Modules/contact/sections/01-contact-split-hero.divi'
body_path = ROOT / 'Modules/contact/sections/03-contact-body.divi'


def ranges(text, wanted):
    token = re.compile(r'<!-- wp:([\w-]+/)?([\w-]+)(?:\s[^>]*)?-->|<!-- /wp:([\w-]+/)?([\w-]+) -->')
    stack, found = [], []
    for m in token.finditer(text):
        if m.group(3) is None:
            name = (m.group(1) or '') + m.group(2)
            if not m.group(0).rstrip().endswith('/-->'):
                stack.append((name, m.start()))
        elif stack:
            close_name = (m.group(3) or '') + m.group(4)
            open_name, start = stack.pop()
            if open_name != close_name:
                raise ValueError((open_name, close_name))
            if open_name == wanted:
                found.append((start, m.end()))
    return sorted(found)


def button_from(source, old_url, old_text, new_url, new_text):
    return source.replace(old_url, new_url).replace(old_text, new_text).replace('WhatsApp', new_text)


def main():
    hero = hero_path.read_text()
    body = body_path.read_text()
    row_start, row_end = ranges(hero, 'divi/row')[0]
    row = hero[row_start:row_end]
    cols = [row[a:b] for a, b in ranges(row, 'divi/column')]
    original_cols = list(cols)
    if len(cols) != 2:
        raise ValueError('expected two hero columns')

    button_match = re.search(r'<!-- wp:divi/button\s+.*? /-->', cols[0])
    if not button_match:
        raise ValueError('hero button missing')
    open_button = button_match.group(0)
    open_button = button_from(open_button, 'https://wa.me/18299866861', 'Whatsapp', '#bd-contact-hero-form', 'Find My Service')
    close_button = button_from(open_button, '#bd-contact-hero-form', 'Find My Service', '#bd-contact-hero-close', 'Cancel')

    form_start, form_end = ranges(body, 'divi/contact-form')[0]
    form = body[form_start:form_end]
    form = form.replace('et_pb_contact_form_0', 'bd_contact_hero_form')
    form_open = re.search(r'<!-- wp:divi/contact-form (\{.*?\}) -->', form, re.S)
    if not form_open:
        raise ValueError('contact form opening block missing')
    form_attrs = json.loads(form_open.group(1))
    form_decoration = form_attrs['module'].setdefault('decoration', {})
    form_sizing = form_decoration.setdefault('sizing', {}).setdefault('desktop', {}).setdefault('value', {})
    form_sizing.update({
        'width': '100%',
        'maxWidth': '100%',
        'height': '100%',
        'minHeight': '100%',
        'alignSelf': 'flex-start',
    })
    form_sizing.pop('alignment', None)
    form_decoration['overflow'] = {'desktop': {'value': {'y': 'scroll'}}}
    form_open_rebuilt = '<!-- wp:divi/contact-form ' + json.dumps(form_attrs, separators=(',', ':')) + ' -->'
    form = form[:form_open.start()] + form_open_rebuilt + form[form_open.end():]
    def tighten_field(match):
        attrs = json.loads(match.group(1))
        decoration = attrs.setdefault('module', {}).setdefault('decoration', {})
        decoration['spacing'] = {
            'desktop': {'value': {'margin': {'top': '0px', 'right': '0px', 'bottom': '12px', 'left': '0px', 'syncVertical': 'off', 'syncHorizontal': 'off'}}},
            'phone': {'value': {'margin': {'top': '0px', 'right': '0px', 'bottom': '10px', 'left': '0px', 'syncVertical': 'off', 'syncHorizontal': 'off'}}},
        }
        return '<!-- wp:divi/contact-field ' + json.dumps(attrs, separators=(',', ':')) + ' /-->'
    form = re.sub(r'<!-- wp:divi/contact-field (\{.*?\}) /-->', tighten_field, form, flags=re.S)

    slider_start, slider_end = ranges(cols[1], 'divi/slider')[0]
    slider = cols[1][slider_start:slider_end]
    slides = [(m.start(), m.end()) for m in re.finditer(r'<!-- wp:divi/slide\s+.*? /-->', slider)]
    if not slides:
        raise ValueError('hero slider has no slides')
    cols[1] = cols[1][:slider_start] + slider + cols[1][slider_end:]

    script = '''<style>
.bd-contact-hero-section{overflow:hidden!important;position:relative;z-index:20;transition:height .65s ease,min-height .65s ease;}
.bd-contact-flow-open{overflow:hidden!important;}
.bd-contact-hero-section.is-contact-fullscreen{height:calc(100vh - 84px)!important;min-height:calc(100vh - 84px)!important;width:100vw!important;max-width:100vw!important;margin-top:0!important;}
.bd-contact-hero-section.is-contact-fullscreen .bd-contact-hero-row{height:100%!important;min-height:0!important;}
.bd-contact-hero-section.is-contact-fullscreen .bd-contact-hero-row>.et_pb_column{height:100%!important;min-height:0!important;}
.bd-contact-hero-section.is-contact-fullscreen .bd-contact-hero-row .et_pb_slider{height:100%!important;min-height:0!important;}
.bd-contact-hidden-section{display:none!important;}
.bd-contact-hero-row{width:150%!important;max-width:none!important;min-height:500px!important;display:flex!important;flex-wrap:nowrap!important;overflow:visible!important;transform:translateX(0);transition:transform .65s cubic-bezier(.22,.61,.36,1);}
.bd-contact-hero-row>.et_pb_column{flex:0 0 33.333333%!important;width:33.333333%!important;max-width:none!important;min-height:500px!important;transition:flex-basis .65s cubic-bezier(.22,.61,.36,1),width .65s cubic-bezier(.22,.61,.36,1),opacity .45s ease,transform .65s cubic-bezier(.22,.61,.36,1);}
.bd-contact-hero-row>.et_pb_column:nth-child(2){overflow:hidden;}
.bd-contact-hero-row>.et_pb_column:nth-child(3){background:#fff!important;border:3px solid #141630!important;border-radius:30px!important;box-sizing:border-box;overflow:hidden;padding:28px 4%!important;height:500px!important;max-height:500px!important;margin-left:18px!important;position:relative;z-index:30;}
.bd-contact-hero-row>.et_pb_column:nth-child(3) .et_pb_contact_form_container{width:100%!important;max-width:none!important;height:100%!important;box-sizing:border-box;overflow-y:auto;overflow-x:hidden;display:flex!important;flex-direction:column!important;}
.bd-contact-hero-row>.et_pb_column:nth-child(3) .et_pb_contact_form{width:100%!important;max-width:none!important;flex:1 1 auto;box-sizing:border-box;display:flex!important;flex-direction:column!important;gap:10px!important;}
.bd-contact-hero-form-panel .et_pb_contact_field{margin-bottom:0!important;}
.bd-contact-hero-row.is-form-open{transform:translateX(-33.333333%);}
.bd-contact-hero-row.is-form-open{width:100%!important;transform:translateX(0)!important;}
.bd-contact-hero-row.is-form-open>.et_pb_column:nth-child(1){flex:0 0 0!important;width:0!important;opacity:0;pointer-events:none;padding-left:0!important;padding-right:0!important;overflow:hidden!important;transform:translateX(-100%);}
.bd-contact-hero-row.is-form-open>.et_pb_column:nth-child(2),.bd-contact-hero-row.is-form-open>.et_pb_column:nth-child(3){flex:0 0 50%!important;width:50%!important;}
.bd-contact-hero-row.is-form-open>.et_pb_column:nth-child(2){border-radius:30px!important;overflow:hidden!important;}
.bd-contact-hero-row.is-form-open>.et_pb_column:nth-child(3){height:100%!important;max-height:none!important;box-shadow:-10px 0 28px rgba(0,0,0,.18);}
.bd-contact-hero-form-panel{position:relative!important;}
.bd-contact-hero-form-panel .bd-contact-hero-close-wrap{position:absolute;top:10px;right:10px;z-index:100;}
.bd-contact-hero-form-panel .bd-contact-hero-close-wrap a{position:relative;z-index:101;}
.bd-contact-hero-form-title{color:#141630!important;margin:0 0 18px!important;font-family:Montserrat,sans-serif;font-weight:700;}
.bd-contact-hero-form-panel .et_pb_contact_form_container,.bd-contact-hero-form-panel .et_pb_contact_form{background:#fff!important;color:#141630!important;}
.bd-contact-hero-form-panel .et_pb_contact_field label,.bd-contact-hero-form-panel .et_pb_contact_field_desc{color:#353740!important;}
.bd-contact-hero-form-panel .et_pb_contact_field input,.bd-contact-hero-form-panel .et_pb_contact_field textarea,.bd-contact-hero-form-panel .et_pb_contact_field select{background:#fff!important;color:#141630!important;border:1px solid #cfd5df!important;}
.bd-contact-hero-form-panel .et_pb_contact_field input::placeholder,.bd-contact-hero-form-panel .et_pb_contact_field textarea::placeholder{color:#697386!important;opacity:1;}
html[data-bd-theme="light"] .bd-contact-hero-row>.et_pb_column:nth-child(3){background:#fff!important;color:#141630!important;}
html[data-bd-theme="light"] .bd-contact-hero-form-panel .et_pb_contact_form_container,html[data-bd-theme="light"] .bd-contact-hero-form-panel .et_pb_contact_form{background:#fff!important;color:#141630!important;}
html[data-bd-theme="light"] .bd-contact-hero-form-panel .et_pb_contact_field label,html[data-bd-theme="light"] .bd-contact-hero-form-panel .et_pb_contact_field_desc{color:#353740!important;}
html[data-bd-theme="dark"] .bd-contact-hero-row>.et_pb_column:nth-child(3){background:#4f5663!important;color:#fff!important;}
html[data-bd-theme="dark"] .bd-contact-hero-form-title,html[data-bd-theme="dark"] .bd-contact-hero-form-panel .et_pb_contact_field label,html[data-bd-theme="dark"] .bd-contact-hero-form-panel .et_pb_contact_field_desc{color:#fff!important;}
html[data-bd-theme="dark"] .bd-contact-hero-form-panel .et_pb_contact_form_container,html[data-bd-theme="dark"] .bd-contact-hero-form-panel .et_pb_contact_form{background:#4f5663!important;color:#fff!important;}
html[data-bd-theme="dark"] .bd-contact-hero-form-panel .et_pb_contact_field input,html[data-bd-theme="dark"] .bd-contact-hero-form-panel .et_pb_contact_field textarea,html[data-bd-theme="dark"] .bd-contact-hero-form-panel .et_pb_contact_field select{background:#eef0f3!important;color:#141630!important;border-color:#d7dce5!important;}
html[data-bd-theme="dark"] .bd-contact-hero-form-panel .et_pb_contact_field input::placeholder,html[data-bd-theme="dark"] .bd-contact-hero-form-panel .et_pb_contact_field textarea::placeholder{color:#697386!important;opacity:1;}
@media (prefers-color-scheme:dark){.bd-contact-hero-row>.et_pb_column:nth-child(3){background:#555b66!important;color:#fff!important;}.bd-contact-hero-form-title{color:#fff!important;}.bd-contact-hero-row>.et_pb_column:nth-child(3) label{color:#fff!important;}.bd-contact-hero-row>.et_pb_column:nth-child(3) input,.bd-contact-hero-row>.et_pb_column:nth-child(3) textarea,.bd-contact-hero-row>.et_pb_column:nth-child(3) select{background:#eef0f3!important;color:#141630!important;}}
@media (max-width:767px){.bd-contact-hero-section.is-contact-fullscreen{height:calc(100vh - 72px)!important;min-height:calc(100vh - 72px)!important;margin-top:0!important;}.bd-contact-hero-row{width:100%!important;min-height:0!important;display:block!important;transform:none!important;}.bd-contact-hero-row>.et_pb_column{width:100%!important;min-height:0!important;}.bd-contact-hero-row>.et_pb_column:nth-child(1){min-height:420px!important;}.bd-contact-hero-row>.et_pb_column:nth-child(2){min-height:380px!important;}.bd-contact-hero-row>.et_pb_column:nth-child(3){display:none!important;border-radius:30px!important;max-height:none!important;margin-left:0!important;padding:20px 5%!important;}.bd-contact-hero-row.is-form-open>.et_pb_column:nth-child(1),.bd-contact-hero-row.is-form-open>.et_pb_column:nth-child(2){display:none!important;}.bd-contact-hero-row.is-form-open>.et_pb_column:nth-child(3){display:flex!important;min-height:380px!important;max-height:380px!important;height:380px!important;overflow:auto!important;}.bd-contact-hero-row>.et_pb_column:nth-child(3) .et_pb_contact_form_container{height:100%!important;max-height:none;}}
</style><script>(function(){function init(){var rows=document.querySelectorAll('.bd-contact-hero-row');rows.forEach(function(row){if(row.dataset.contactFlowBound)return;row.dataset.contactFlowBound='1';var section=row.closest('.et_pb_section');if(section)section.classList.add('bd-contact-hero-section');var open=row.querySelector('a[href="#bd-contact-hero-form"]');var close=row.querySelector('a[href="#bd-contact-hero-close"]');var closeWrap=close&&close.closest('.et_pb_button_module_wrapper');if(closeWrap)closeWrap.classList.add('bd-contact-hero-close-wrap');function setFormVisible(visible){var form=row.querySelector('.bd-contact-hero-form-panel');if(form)form.setAttribute('aria-hidden',visible?'false':'true');}function hideRest(){if(!section)return;document.documentElement.classList.add('bd-contact-flow-open');document.body.classList.add('bd-contact-flow-open');section.classList.add('is-contact-fullscreen');var passed=false;document.querySelectorAll('.et_pb_section').forEach(function(item){if(passed)item.classList.add('bd-contact-hidden-section');if(item===section)passed=true;});}function restore(){if(!section)return;document.documentElement.classList.remove('bd-contact-flow-open');document.body.classList.remove('bd-contact-flow-open');section.classList.remove('is-contact-fullscreen');document.querySelectorAll('.bd-contact-hidden-section').forEach(function(item){item.classList.remove('bd-contact-hidden-section');});}function closeFlow(){row.classList.remove('is-form-open');restore();setFormVisible(false);if(location.hash==='#bd-contact-hero-form')history.replaceState(null,document.title,location.pathname+location.search);}if(open)open.addEventListener('click',function(e){e.preventDefault();hideRest();row.classList.add('is-form-open');setFormVisible(true);history.pushState({contactHeroForm:true},'', '#bd-contact-hero-form');});if(close)close.addEventListener('click',function(e){e.preventDefault();closeFlow();});document.addEventListener('keydown',function(e){if(e.key==='Escape'&&row.classList.contains('is-form-open'))closeFlow();});window.addEventListener('popstate',function(){if(row.classList.contains('is-form-open'))closeFlow();});});}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();window.addEventListener('et_builder_api_ready',init);})();</script>'''
    code = '<!-- wp:divi/code ' + json.dumps({'module': {'meta': {'adminLabel': {'desktop': {'value': 'Contact Hero Form Flow'}}}}, 'content': {'innerContent': {'desktop': {'value': script}}}, 'builderVersion': '5.11.1'}, separators=(',', ':')) + ' /-->'

    row = row.replace('"1_2,1_2"', '"1_3,1_3,1_3"', 1)
    row = row.replace('"width":"100%","maxWidth":"100%"', '"width":"150%","maxWidth":"none"', 1)
    row = row.replace('value":" et_pb_row_fullwidth"', 'value":" et_pb_row_fullwidth bd-contact-hero-row"', 1)
    cols[0] = cols[0].replace('<!-- /wp:divi/column -->', code + '\n<!-- /wp:divi/column -->', 1)
    cols[0] = cols[0].replace('"1_2"', '"1_3"', 1)
    cols[1] = cols[1].replace('"1_2"', '"1_3"', 1)
    cols[1] = cols[1].replace('<!-- wp:divi/slider', open_button + '\n<!-- wp:divi/slider', 1)
    cols[1] = cols[1].replace('bd-hero-history-column', 'bd-contact-hero-media', 1)
    form_image = '''<!-- wp:divi/image {"module":{"decoration":{"sizing":{"desktop":{"value":{"width":"96px","maxWidth":"96px","height":"64px","alignSelf":"flex-start"}},"phone":{"value":{"width":"76px","maxWidth":"76px","height":"50px","alignSelf":"flex-start"}}},"spacing":{"desktop":{"value":{"margin":{"bottom":"14px"}}},"phone":{"value":{"margin":{"bottom":"10px"}}}},"border":{"desktop":{"value":{"radius":{"sync":"on","topLeft":"14px","topRight":"14px","bottomRight":"14px","bottomLeft":"14px"}}},"phone":{"value":{"radius":{"sync":"on","topLeft":"11px","topRight":"11px","bottomRight":"11px","bottomLeft":"11px"}}}}}},"image":{"innerContent":{"desktop":{"value":{"src":"https://wordpress-868870-6701729.cloudwaysapps.com/wp-content/uploads/2026/09/1.png","alt":"BD Star Transport van"}}}},"builderVersion":"5.11.1"} /-->'''
    form_column = '''<!-- wp:divi/column {"module":{"advanced":{"type":{"desktop":{"value":"1_3"}}},"decoration":{"sizing":{"desktop":{"value":{"flexType":"8_24","height":"100%","minHeight":"100%"}},"tablet":{"value":{"flexType":"24_24"}},"phone":{"value":{"flexType":"24_24"}}},"spacing":{"desktop":{"value":{"padding":{"top":"28px","right":"4%","bottom":"28px","left":"4%","syncVertical":"on","syncHorizontal":"on"}}},"phone":{"value":{"padding":{"top":"20px","right":"5%","bottom":"20px","left":"5%","syncVertical":"on","syncHorizontal":"on"}}}},"layout":{"desktop":{"value":{"display":"flex","flexDirection":"column","justifyContent":"center"}},"tablet":{"value":{"display":"flex","flexDirection":"column","justifyContent":"center"}},"phone":{"value":{"display":"flex","flexDirection":"column","justifyContent":"center"}}}},"attributes":{"desktop":{"value":{"attributes":[{"id":"bd-contact-hero-form-panel","name":"class","value":"bd-contact-hero-form-panel","adminLabel":"CSS Class"}]}}}},"builderVersion":"5.11.1"} -->
'''+form_image+'''\n'''+text_module('Hero Form Title','<h2 class="bd-contact-hero-form-title">Tell us about your trip</h2>')+'''\n'''+close_button+'''\n'''+form+'''\n<!-- /wp:divi/column -->'''
    new_row = row.replace(original_cols[0], cols[0], 1).replace(original_cols[1], cols[1], 1)
    new_row = new_row.replace('<!-- /wp:divi/row -->', form_column + '\n<!-- /wp:divi/row -->', 1)
    new_row = re.sub(r'"builderVersion":"[^"]+"', '"builderVersion":"5.11.1"', new_row)
    compiled_hero = hero[:row_start] + new_row + hero[row_end:]
    compiled_hero = re.sub(r'"builderVersion":"[^"]+"', '"builderVersion":"5.11.1"', compiled_hero)
    hero_path.write_text(compiled_hero)


def text_module(label, html):
    attrs = {'module': {'meta': {'adminLabel': {'desktop': {'value': label}}}, 'decoration': {'layout': {'desktop': {'value': {'display': 'block'}}}}}, 'content': {'innerContent': {'desktop': {'value': html}}}, 'builderVersion': '5.11.1'}
    return '<!-- wp:divi/text ' + json.dumps(attrs, separators=(',', ':')) + ' /-->'


if __name__ == '__main__':
    main()
