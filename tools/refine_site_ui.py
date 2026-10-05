#!/usr/bin/env python3
"""Build the approved BD Star UI refresh as native Divi modules.

Uses the original export wrappers byte-for-byte. Run only after making the
named backup. Generates staged exports; promotion is a separate QA step.
"""
from __future__ import annotations

import argparse
import base64
from copy import deepcopy
import html
import json
from pathlib import Path
import re
import tarfile
from urllib.parse import quote

import divi_modules as dm

BASE = dm.BASE
BACKUP = BASE / '.backup/before-modern-ui-20261002.tar.gz'
VERSION = '5.11.1'
NAVY, BODY, MUTED = '#141630', '#353740', '#5f6877'
PAPER, WHITE, LINE, YELLOW = '#f4f6f8', '#ffffff', '#dce1e8', '#fcd21d'
MEDIA = 'https://wordpress-868870-6701729.cloudwaysapps.com/wp-content/uploads/2026/09/'
WA = 'https://wa.me/18299866861'


def bp(value):
    return {'desktop': {'value': value}}


def responsive(desktop, tablet=None, phone=None):
    return {key: {'value': deepcopy(val)} for key, val in
            [('desktop', desktop), ('tablet', tablet if tablet is not None else desktop),
             ('phone', phone if phone is not None else tablet if tablet is not None else desktop)]}


def pad(v, h=None):
    return dict(top=v, bottom=v, left=h or v, right=h or v,
                syncVertical='on', syncHorizontal='on')


def radius(size='12px'):
    return dict(topLeft=size, topRight=size, bottomLeft=size, bottomRight=size, sync='on')


def border(color=LINE, size='12px', width='1px'):
    return bp({'styles': {'all': {'width': width, 'color': color, 'style': 'solid'}},
               'radius': radius(size)})


def font(size='16px', color=BODY, weight='400', height='1.65em', **extra):
    return dict(family='Montserrat', size=size, color=color, weight=weight,
                lineHeight=height, **extra)


def module(cls='', label='', **decoration):
    out = {'decoration': {'spacing': bp({'margin': pad('0px'), 'padding': pad('0px')}), **decoration}}
    if cls:
        out['advanced'] = {'htmlAttributes': bp({'class': cls, 'id': ''})}
    if label:
        out['meta'] = {'adminLabel': bp(label)}
    return out


def node(name, attrs, children=None):
    attrs['builderVersion'] = VERSION
    return {'name': name, 'attrs': attrs, 'children': children}


def text(content, size='16px', color=BODY, weight='400', cls='', width='65ch'):
    return node('text', {
        'module': module(cls, sizing=bp({'width': '100%', 'maxWidth': width})),
        'content': {'innerContent': bp(content), 'decoration': {'bodyFont': {
            'body': {'font': responsive(font(size, color, weight))},
            'link': {'font': bp(font(size, NAVY, '600'))}}}}})


def heading(title, level=2, color=NAVY):
    scale = {1: ('56px', '44px', '34px'), 2: ('38px', '32px', '28px'), 3: ('21px', '21px', '20px')}
    sizes = scale[level]
    return node('heading', {'module': module(sizing=bp({'width': '100%', 'maxWidth': '24ch' if level == 1 else '32ch'})),
        'title': {'innerContent': bp(title), 'decoration': {'font': {'font': responsive(
            *[font(s, color, '700', '1.15em' if level == 1 else '1.25em', headingLevel=f'h{level}',
                   letterSpacing='-0.025em' if level < 3 else '-0.01em', capitalization='none') for s in sizes])}}}})


def eyebrow(title, dark=False):
    n = text(html.escape(title), '12px', YELLOW if dark else MUTED, '600', 'bd-ui-eyebrow')
    n['attrs']['content']['decoration']['bodyFont']['body']['font'] = responsive(
        font('12px', YELLOW if dark else MUTED, '600', '1.5em', letterSpacing='0.12em', capitalization='uppercase'))
    return n


def button(label, url='/contact#inquiry', secondary=False):
    fill, ink = (WHITE, NAVY) if secondary else (YELLOW, NAVY)
    decoration = {
        'button': bp({'enable': 'on', 'icon': {'enable': 'off'}}),
        'background': {'desktop': {'value': {'color': fill}, 'hover': {'color': PAPER if secondary else '#ffe168'}}},
        'font': {'font': responsive(font('15px', ink, '600', '1.5em', letterSpacing='0px', capitalization='none'))},
        'spacing': responsive({'padding': pad('14px', '24px')}, {'padding': pad('14px', '22px')}, {'padding': pad('14px', '20px')}),
        'border': border(LINE if secondary else YELLOW, '8px'),
    }
    return node('button', {'module': module('bd-ui-button-secondary' if secondary else 'bd-ui-button-primary'),
        'button': {'innerContent': bp({'text': label, 'linkUrl': url, 'linkTarget': 'off'}), 'decoration': decoration}})


def image(filename, alt, portrait=False):
    return node('image', {'module': module('bd-ui-image', sizing=bp({'width': '100%', 'maxWidth': '100%'}),
                            border=border('transparent', '12px', '0px')),
        'image': {'innerContent': bp({'src': MEDIA + filename, 'alt': alt}),
                  'decoration': {'sizing': responsive({'width': '100%', 'height': 'auto',
                                                     'aspectRatio': {'width': '4', 'height': '5' if portrait else '3'}}),
                                 'fit': responsive({'objectFit': 'cover', 'objectPosition': 'center center'}),
                                 'border': border('transparent', '12px', '0px')}}})


def group(children, surface=False, gap='16px'):
    deco = {'layout': responsive({'display': 'flex', 'flexDirection': 'column', 'rowGap': gap,
                                  'alignItems': 'stretch', 'justifyContent': 'flex-start'}),
            'sizing': bp({'width': '100%', 'minWidth': '0px'})}
    if surface:
        deco['sizing']['desktop']['value']['height'] = '100%'
        deco.update(background=bp({'color': WHITE}), border=border(),
                    spacing=responsive({'padding': pad('32px'), 'margin': pad('0px')},
                                       {'padding': pad('28px'), 'margin': pad('0px')},
                                       {'padding': pad('24px'), 'margin': pad('0px')}))
    return node('group', {'module': module('bd-ui-surface' if surface else '', **deco)}, children)


def column(children, count=1):
    return node('column', {'module': module(
        sizing=responsive({'flexType': f'{24 // count}_24', 'minWidth': '0px'},
                          {'flexType': '24_24', 'minWidth': '0px'}, {'flexType': '24_24', 'minWidth': '0px'}),
        layout=responsive({'display': 'flex', 'flexDirection': 'column', 'rowGap': '24px', 'alignItems': 'stretch'}))}, children)


def row(columns, narrow=False, align='center'):
    n = len(columns)
    out = module(sizing=responsive({'width': '90%', 'maxWidth': '800px' if narrow else '1200px'},
                                  {'width': '90%', 'maxWidth': '1200px'}, {'width': '90%', 'maxWidth': '1200px'}),
                 spacing=bp({'padding': pad('0px'), 'margin': {'top': '0px', 'bottom': '0px', 'left': 'auto', 'right': 'auto'}}),
                 layout=responsive({'flexWrap': 'nowrap', 'columnGap': '48px', 'rowGap': '32px', 'alignItems': align},
                                   {'flexWrap': 'wrap', 'columnGap': '24px', 'rowGap': '32px', 'alignItems': 'stretch'},
                                   {'flexWrap': 'wrap', 'columnGap': '24px', 'rowGap': '28px', 'alignItems': 'stretch'}))
    out['advanced'] = {'flexColumnStructure': responsive(f'equal-columns_{n}', 'equal-columns_1', 'equal-columns_1')}
    return node('row', {'module': out}, [column(c, n) for c in columns])


def section(label, rows, tone='white', anchor=''):
    dark = tone == 'dark'
    out = module('bd-ui-page' + (' bd-ui-dark' if dark else ''), label,
        background=bp({'color': NAVY if dark else PAPER if tone == 'soft' else WHITE}),
        spacing=responsive({'padding': pad('88px', '0px'), 'margin': pad('0px')},
                           {'padding': pad('64px', '0px'), 'margin': pad('0px')},
                           {'padding': pad('48px', '0px'), 'margin': pad('0px')}),
        layout=responsive({'display': 'flex', 'flexDirection': 'column', 'rowGap': '40px'}))
    out['advanced']['htmlAttributes']['desktop']['value']['id'] = anchor
    return node('section', {'module': out}, rows)


def intro(kicker, title, description, dark=False):
    return [eyebrow(kicker, dark), heading(title, color=WHITE if dark else NAVY),
            text(description, color='#d7d9e2' if dark else MUTED)]


def cta(title='Tell us where you want to go.', description='Send your dates, destination, and group size. We will help you plan the journey.'):
    return section('Plan your journey', [row([
        [eyebrow('Plan your journey', True), heading(title, color=WHITE), text(description, color='#d7d9e2')],
        [button('Request a transfer'), text(f'<a href="{WA}">Prefer WhatsApp? Message our team.</a>', color='#d7d9e2')]
    ])], 'dark')


def blocks(payload):
    for match in dm.OPEN_RE.finditer(payload):
        pos = match.end()
        while payload[pos:pos+1].isspace():
            pos += 1
        if payload[pos:pos+1] == '{':
            attrs, end = json.JSONDecoder().raw_decode(payload, pos)
            yield match[1], attrs, pos, end


def serialize(n):
    attrs = json.dumps(n['attrs'], ensure_ascii=False, separators=(',', ':'))
    # JSON is the sole escaping boundary. Never pre-escape rich text.
    if n['children'] is None:
        return f'<!-- wp:divi/{n["name"]} {attrs} /-->'
    return f'<!-- wp:divi/{n["name"]} {attrs} -->\n' + '\n'.join(map(serialize, n['children'])) + f'\n<!-- /wp:divi/{n["name"]} -->'


def sources():
    if not BACKUP.exists():
        raise SystemExit('Create the before-modern-ui backup before running this build.')
    with tarfile.open(BACKUP) as tar:
        return {page: json.loads(tar.extractfile(path.name).read()) for page, path in dm.EXPORTS.items()}


def form(source, page):
    payload = next(iter(source['data'].values()))
    attrs = deepcopy(next(a for name, a, _, _ in blocks(payload) if name == 'contact-form'))
    attrs['module'].setdefault('advanced', {})['uniqueId'] = bp(
        '324635a4-73de-446e-9b3b-df4ee39df505' if page == 'home' else '6efa7aee-d087-4657-9b1f-5d44b44c30e7')
    attrs['module']['advanced']['htmlAttributes'] = bp({'id': f'{page}-inquiry-form', 'class': 'bd-ui-form'})
    attrs['module']['decoration'] = module()['decoration']
    attrs['button'] = deepcopy(button('Send inquiry')['attrs']['button'])
    attrs['button']['innerContent'] = bp({'text': 'Send inquiry'})
    field_style = {'background': bp({'color': WHITE}), 'border': border(LINE, '6px'),
                   'font': {'font': bp(font())}, 'placeholderFont': {'font': bp(font(color=MUTED))},
                   'spacing': bp({'padding': pad('16px')})}
    attrs['field'] = {'decoration': field_style}
    definitions = [('Name', 'Your name', 'input', True), ('Email', 'Email address', 'email', True),
                   ('Telephone', 'Phone / WhatsApp number (optional)', 'input', False),
                   ('Subject', 'Service', 'select', True),
                   ('Message', 'Travel dates, pickup, destination, and group size', 'text', True)]
    children = []
    for field_id, label, kind, required in definitions:
        adv = {'id': bp(field_id), 'type': bp(kind), 'required': bp('on' if required else 'off'), 'fullwidth': bp('on')}
        if kind == 'select':
            adv['selectOptions'] = bp([{'value': label, 'id': key} for key, label in [
                ('airport', 'Airport transfer'), ('family', 'Family or group trip'),
                ('tour', 'Private tour'), ('other', 'General inquiry')]])
        children.append(node('contact-field', {
            'module': module(sizing=responsive({'flexType': '24_24'}),
                             spacing=bp({'margin': {'bottom': '18px'}, 'padding': pad('0px')})),
            'fieldItem': {'advanced': adv, 'innerContent': bp(label)}}))
    return node('contact-form', attrs, children)


def faq(items):
    # Static native heading/text pairs: always available, no JS dependency.
    return [group([heading(question, 3), text(answer, color=MUTED)], surface=True) for question, answer in items]


def about_page():
    return [
        section('About — introduction', [row([
            [eyebrow('About BD Star'), heading('A family business. A more personal journey.', 1),
             text('Local knowledge and thoughtful service for families visiting Punta Cana and the Dominican Republic.', '18px', MUTED),
             button('Plan your transfer'), text('Airport transfers · Family trips · Private tours', '13px', MUTED)],
            [image('delvis.png', 'BD Star driver seated in a transport vehicle', True)]
        ])], 'soft'),
        section('About — our approach', [row([
            [eyebrow('Our approach'), heading('Good service starts with knowing what matters.')],
            [text('BD Star is a family transportation business based in Punta Cana. We help visiting families get from the airport to their resort, travel together, and explore the Dominican Republic.'),
             text('A smooth trip depends on the details: room for luggage, child seats requested in advance, and a driver who knows the route. We plan around your flight, your group, and where you need to be.', color=MUTED)]
        ], align='flex-start')]),
        section('About — service commitments', [row([intro('What you can expect', 'Practical care, at every stage.', 'Clear communication and thoughtful preparation from your first inquiry to your destination.')]),
            row([
                [group([eyebrow('Before your trip'), heading('Clear plans', 3), text('Share your dates, route, and group size. Tell us about child seats or extra luggage so we can prepare.', color=MUTED)], True)],
                [group([eyebrow('At pickup'), heading('A familiar welcome', 3), text('For airport arrivals, we monitor your flight and meet you with a name sign. Your driver helps with the luggage.', color=MUTED)], True)],
                [group([eyebrow('On the road'), heading('Comfort for your family', 3), text('Travel together in an air-conditioned vehicle, with a local driver and space for the things your family brings.', color=MUTED)], True)]
            ], align='stretch')], 'soft'),
        cta('Let us help plan your arrival.', 'Tell us when you land and where you are staying. We will help arrange the transfer for your group.')
    ]


def service_link(service):
    return WA + '?text=' + quote('Hello BD Star, I would like to arrange ' + service + '. My travel dates, destination, and group size are: ')


SERVICES = [
    ('airport-transfers', 'Airport transfers', 'airport.png', 'Family arriving at Punta Cana airport',
     'From Punta Cana Airport to your destination.',
     'Private transfers between Punta Cana International Airport (PUJ) and your resort or villa, with pickup planned around your flight.',
     [('Flight monitoring', 'We adjust pickup to your flight arrival.'), ('Meet and greet', 'Look for your driver and personalized name sign.'), ('Family preparation', 'Request child seats and tell us about your luggage.')]),
    ('family-trips', 'Family and group trips', 'family.png', 'Guests traveling with BD Star Transport',
     'Your group. Your plans. One vehicle.',
     'Travel together around Punta Cana with a dedicated vehicle and driver. Discuss your pickup times and planned stops when arranging the trip.',
     [('Room to travel together', 'Choose transport suited to your group and bags.'), ('Flexible plans', 'Discuss stops and pickup times with our team.'), ('Local support', 'Coordinate your journey in English or Spanish.')]),
    ('private-tours', 'Private tours', 'explore.png', 'Guests exploring the Dominican Republic',
     'See more of the Dominican Republic.',
     'Arrange a private day trip around your interests, from Santo Domingo to coastal destinations. Our team helps coordinate the route and transport.',
     [('A route around your interests', 'Share the places you would like to visit.'), ('Private transportation', 'Travel with your group and a dedicated driver.'), ('Pickup and return', 'Coordinate departure and return at your accommodation.')])
]


def services_page():
    pages = [section('Services — introduction', [row([[eyebrow('Our services'),
        heading('The right journey for your plans.', 1),
        text('Airport arrivals, days out with the family, and private tours across the Dominican Republic.', '18px', MUTED),
        text('<a href="#airport-transfers">Airport transfers</a> · <a href="#family-trips">Family trips</a> · <a href="#private-tours">Private tours</a>')]], narrow=True)], 'soft')]
    for i, (anchor, name, filename, alt, title, desc, details) in enumerate(SERVICES):
        body = [eyebrow(name), heading(title), text(desc, color=MUTED)]
        body += [group([heading(t, 3), text(d, color=MUTED)], gap='8px') for t, d in details]
        body += [button('Ask about ' + name.lower(), service_link(name.lower()))]
        # Text-first DOM order is consistent on phones; imagery stays alongside on desktop.
        pages.append(section('Services — ' + name, [row([body, [image(filename, alt)]])],
                             'white' if i % 2 == 0 else 'soft', anchor))
    pages.append(section('Services — questions', [row([intro('Before you book', 'A few useful details.', 'Confirm the details of your particular journey with our team.')]), row([faq([
        ('Where do I meet my airport driver?', 'Your driver meets you outside the customs arrival hall with a personalized name sign. Coordinate the pickup details with us before you travel.'),
        ('Can I request a child seat?', 'Yes. Tell us the age of each child and the seats you need when you send your inquiry.'),
        ('Can we include stops along the route?', 'Tell us about your planned stops when requesting the trip so we can confirm the route and quote.'),
        ('How do I arrange my journey?', 'Send your travel dates, pickup location, destination, and group size through our inquiry form or WhatsApp.')
    ])], narrow=True)], 'soft'))
    pages.append(cta())
    return pages


def home_page(src):
    payload = next(iter(src['data'].values()))
    code = deepcopy(next(a for name, a, _, _ in blocks(payload) if name == 'code'))
    raw = code['content']['innerContent']['desktop']['value']
    # Keep the proven video dialog, but its trigger now belongs in normal flow.
    start, end = raw.index('  function positionOpener(){'), raw.index('  function openModal(event){')
    code['content']['innerContent']['desktop']['value'] = raw[:start] + raw[end:]
    reviews = [deepcopy(a) for name, a, _, _ in blocks(payload) if name == 'testimonial']
    review_nodes = []
    for attrs in reviews:
        attrs['module'] = module('bd-ui-surface', background=bp({'color': WHITE}), border=border(),
                                 spacing=responsive({'padding': pad('28px')}, {'padding': pad('24px')}))
        attrs['content']['decoration'] = {'bodyFont': {'body': {'font': bp(font())}}}
        attrs['author']['decoration'] = {'font': {'font': bp(font('15px', NAVY, '600'))}}
        attrs.pop('jobTitle', None)  # Relative review dates become stale.
        review_nodes.append(node('testimonial', attrs))
    return [
        section('Home — introduction', [row([
            [eyebrow('Punta Cana · Dominican Republic'), heading('Your family journey starts here.', 1),
             text('Private airport transfers, family trips, and tours with local drivers who know Punta Cana.', '18px', MUTED),
             button('Request a transfer'), button('Watch our story', '#bdstar-video', True), node('code', code)],
            [image('airport.png', 'Family arriving at Punta Cana airport')]
        ])], 'soft'),
        section('Home — choose your journey', [row([intro('How we can help', 'Three ways to travel with us.', 'Choose the service that fits your plans.')]),
            row([[group([heading(name, 3), text(desc, color=MUTED), button('View service', '/services#' + anchor, True)], True)]
                 for anchor, name, _, _, _, desc, _ in SERVICES], align='stretch')]),
        section('Home — arrival experience', [row([
            [image('transport2.png', 'BD Star vehicle used for family transportation')],
            intro('Your airport arrival', 'From touchdown to your destination.', 'A clear pickup plan makes the first day of your trip easier.') + [
                group([eyebrow('01 · Before arrival'), heading('We follow your flight', 3), text('Share your flight details so we can coordinate the pickup around your arrival.', color=MUTED)], gap='8px'),
                group([eyebrow('02 · At the airport'), heading('Meet your driver', 3), text('Look for your name sign outside customs. Your driver helps with your bags.', color=MUTED)], gap='8px'),
                group([eyebrow('03 · On your way'), heading('Travel together', 3), text('Settle into an air-conditioned vehicle and continue to your resort or villa.', color=MUTED)], gap='8px')]
        ])], 'soft'),
        section('Home — meet BD Star', [row([
            intro('A local family business', 'People who care about your journey.', 'We help families navigate Punta Cana with local knowledge, clear communication, and attention to the details.') + [button('Meet BD Star', '/about', True)],
            [image('delvis.png', 'BD Star driver seated in a transport vehicle', True)]
        ])]),
        section('Home — guest reviews', [row([intro('Guest experiences', 'In our guests\' words.', 'Customer reviews from the existing BD Star review collection.')]),
            row([[review_nodes[0]], [review_nodes[1]]], align='stretch'),
            row([[review_nodes[2]], [review_nodes[3]]], align='stretch')], 'soft'),
        section('Home — inquiry', [row([
            intro('Plan your journey', 'Tell us about your trip.', 'Send your dates, route, and group size. Our team will follow up with availability and a quote.') + [
                button('Message us on WhatsApp', WA, True), text('Sending an inquiry does not confirm a reservation.', '13px', MUTED)],
            [group([form(src, 'home')], True)]
        ], align='flex-start')], anchor='inquiry')
    ]


def contact_page(src):
    return [
        section('Contact — introduction', [row([[eyebrow('Contact BD Star'), heading('Let us plan your next journey.', 1),
            text('Tell us where you are going, when you travel, and who is coming with you.', '18px', MUTED)]], narrow=True)], 'soft'),
        section('Contact — inquiry', [row([
            [heading('Send an inquiry'), text('Share your travel dates, pickup, destination, and group size. We will follow up with availability and a quote.', color=MUTED),
             form(src, 'contact'), text('Sending an inquiry does not confirm a reservation.', '13px', MUTED)],
            [group([eyebrow('Speak with our team'), heading('Prefer to chat?', 3), text('Use WhatsApp to discuss your pickup, route, or travel plans.', color=MUTED),
                    button('Message us on WhatsApp', WA),
                    text('<a href="tel:+18299866861">+1 829 986 6861</a>'),
                    text('<a href="mailto:starlopez978@gmail.com">starlopez978@gmail.com</a>'),
                    text('Punta Cana, La Altagracia<br>Dominican Republic', '14px', MUTED)], True)]
        ], align='flex-start')], anchor='inquiry'),
        section('Contact — useful information', [row([intro('Before you get in touch', 'A few things to include.', 'Help us prepare the right transport for your group.')]), row([faq([
            ('Arriving at the airport?', 'Include your arrival date, flight number, destination, and the number of people traveling.'),
            ('Traveling with children?', 'Let us know their ages and whether you need infant, toddler, or booster seats.'),
            ('Planning a tour or several stops?', 'Share the places you want to visit and your preferred date. We can discuss the route before confirming the trip.')
        ])], narrow=True)], 'soft')
    ]


GLOBAL_ADAPTER = '''
/* BD UI refresh: shared accessibility and theme compatibility only.
   Page layout, typography, spacing, borders and colors remain native Divi settings. */
#main-content .bd-ui-page{scroll-margin-top:calc(var(--bd-hdr-h,82px) + 24px);}
#main-content .bd-ui-page .et_pb_column,#main-content .bd-ui-page .et_pb_group{min-width:0;}
#main-content .bd-ui-page a{overflow-wrap:anywhere;}
#main-content .bd-ui-page a:focus-visible,#main-content .bd-ui-page input:focus-visible,
#main-content .bd-ui-page textarea:focus-visible,#main-content .bd-ui-page select:focus-visible{
 outline:3px solid #345ec6;outline-offset:4px;
}
#main-content .bd-ui-page .bd-ui-button-primary .et_pb_button{color:#141630!important;border-color:#fcd21d!important;background:#fcd21d!important;}
#main-content .bd-ui-page .bd-ui-button-primary .et_pb_button:hover{background:#ffe168!important;}
#main-content .bd-ui-page .bd-ui-button-secondary .et_pb_button{color:#141630!important;background:#fff!important;border-color:#dce1e8!important;}
#main-content .bd-ui-page .bd-ui-form .et_pb_contact_submit{color:#141630!important;background:#fcd21d!important;border-color:#fcd21d!important;}
#main-content .bd-ui-page.bd-ui-dark h2{color:#fff!important;}
#main-content .bd-ui-page.bd-ui-dark p,#main-content .bd-ui-page.bd-ui-dark .et_pb_text_inner{color:#d7d9e2!important;}
#main-content .bd-ui-page.bd-ui-dark a:not(.et_pb_button){color:#fcd21d!important;}
html[data-bd-theme="dark"] #main-content .bd-ui-page .et_pb_row{background:transparent!important;}
html[data-bd-theme="dark"] #main-content .bd-ui-page .bd-ui-surface{background:#201c30!important;border-color:rgba(255,255,255,.16)!important;box-shadow:none!important;}
html[data-bd-theme="dark"] #main-content .bd-ui-page.bd-ui-dark{background:#141630!important;}
.bd-theme-toggle{min-height:44px!important;}
.bd-scroll-whatsapp{width:44px!important;height:44px!important;}
.et-l--header a:focus-visible,.et-l--footer a:focus-visible{outline:3px solid #fcd21d;outline-offset:4px;}
@media(prefers-reduced-motion:reduce){html.bd-theme-ready #main-content .bd-ui-page,html.bd-theme-ready #main-content .bd-ui-page *{transition:none!important;animation:none!important;}}
'''


def refresh_global(page, payload):
    replacements = []
    for name, attrs, start, end in blocks(payload):
        old = deepcopy(attrs)
        if page == 'header' and name == 'code':
            value = attrs['content']['innerContent']['desktop']['value']
            attrs['content']['innerContent']['desktop']['value'] = value.replace('</style>', GLOBAL_ADAPTER + '\n</style>', 1)
        if page == 'header' and name == 'menu':
            def normalize(v):
                if isinstance(v, dict):
                    for key in list(v):
                        if key == 'family': v[key] = 'Montserrat'
                        elif key == 'size' and v[key] == '12px': v[key] = '14px'
                        else: normalize(v[key])
            normalize(attrs)
        if name == 'image':
            attrs.get('image', {}).get('innerContent', {}).get('desktop', {}).get('value', {})['alt'] = 'BD Star Transportation'
        if page == 'footer':
            def repair(v):
                if isinstance(v, dict):
                    for key in list(v):
                        if key == 'width' and v[key] == '70': v[key] = '70%'
                        elif isinstance(v[key], str):
                            for old_url, new_url in [
                                ('/services?service=airport-transfers', '/services#airport-transfers'),
                                ('/services?service=private-transportation', '/services#family-trips'),
                                ('/services?service=group-transportation', '/services#family-trips'),
                                ('/services?service=tours', '/services#private-tours')]:
                                v[key] = v[key].replace(old_url, new_url)
                        else: repair(v[key])
                elif isinstance(v, list):
                    for x in v: repair(x)
            repair(attrs)
        if attrs != old:
            replacements.append((start, end, json.dumps(attrs, ensure_ascii=False, separators=(',', ':'))))
    for start, end, value in reversed(replacements):
        payload = payload[:start] + value + payload[end:]
    return payload


def write_page(page, sections):
    folder = dm.MODULES / page
    manifest_path = folder / 'manifest.json'
    manifest = json.loads(dm.read_text_exact(manifest_path))
    # Original files remain available on disk and in the backup. Manifest selects the new build.
    old_raw = [p for p in manifest['parts'] if p['kind'] == 'raw']
    prefix = next((p['text'] for p in old_raw if 'wp:divi/placeholder' in (p.get('text') or '') and '/wp:divi/placeholder' not in p['text']), '')
    suffix = next((p['text'] for p in old_raw if '/wp:divi/placeholder' in (p.get('text') or '')), '')
    parts = [{'kind': 'raw', 'file': None, 'text': prefix, 'label': None}] if prefix else []
    for idx, n in enumerate(sections, 1):
        label = n['attrs']['module']['meta']['adminLabel']['desktop']['value']
        filename = f'sections/ui-{idx:02d}-{dm.slugify(label, page)}.divi'
        dm.write_text_exact(folder / filename, serialize(n))
        parts += [{'kind': 'section', 'file': filename, 'text': None, 'label': label},
                  {'kind': 'raw', 'file': None, 'text': '\n\n', 'label': None}]
    if suffix:
        parts.append({'kind': 'raw', 'file': None, 'text': suffix, 'label': None})
    manifest['parts'] = parts
    note = 'UI refresh: native Divi components; 88/64/48px section spacing; tablet/phone stacking.'
    if note not in manifest['notes']:
        manifest['notes'].append(note)
    dm.write_text_exact(manifest_path, json.dumps(manifest, indent=2, ensure_ascii=False))
    return dm.compile_one(page)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--preview-assets', action='store_true')
    args = parser.parse_args()
    src = sources()
    pages = {'about': about_page(), 'home': home_page(src['home']),
             'services': services_page(), 'contact': contact_page(src['contact'])}
    for page, sections in pages.items():
        write_page(page, sections)
    for page in ['header', 'footer']:
        manifest = json.loads((dm.MODULES / page / 'manifest.json').read_text())
        parts = [p for p in manifest['parts'] if p['kind'] == 'section']
        with tarfile.open(BACKUP) as tar:
            for part in parts:
                original = tar.extractfile(f'Modules/{page}/{part["file"]}').read().decode('utf-8')
                dm.write_text_exact(dm.MODULES / page / part['file'], refresh_global(page, original))
        dm.compile_one(page)
    preview = BASE / 'evidence/modern-ui'
    preview.mkdir(exist_ok=True)
    dm.write_text_exact(preview / 'page-models.json', json.dumps(pages, ensure_ascii=False))
    if args.preview_assets:
        assets = preview / 'assets'
        assets.mkdir(exist_ok=True)
        for source in src.values():
            for url, data in source.get('images', {}).items():
                if url.startswith(MEDIA) and data.get('encoded'):
                    (assets / url.rsplit('/', 1)[-1]).write_bytes(base64.b64decode(data['encoded']))


if __name__ == '__main__':
    main()
