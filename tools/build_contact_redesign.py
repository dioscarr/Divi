#!/usr/bin/env python3
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def block_ranges(text, wanted):
    token = re.compile(r'<!-- wp:([\w-]+/)?([\w-]+)(?:\s[^>]*)?-->|<!-- /wp:([\w-]+/)?([\w-]+) -->')
    stack = []
    found = []
    for match in token.finditer(text):
        if match.group(3) is None:
            name = (match.group(1) or '') + match.group(2)
            if not match.group(0).rstrip().endswith('/-->'):
                stack.append((name, match.start()))
        elif stack:
            close_name = (match.group(3) or '') + match.group(4)
            open_name, start = stack.pop()
            if open_name != close_name:
                raise ValueError((open_name, close_name))
            if open_name == wanted:
                found.append((start, match.end()))
    return sorted(found)


def first_section(text, label):
    for start, end in block_ranges(text, 'divi/section'):
        block = text[start:end]
        if label in block:
            return block
    raise ValueError(label)


def first_columns(section):
    return [section[a:b] for a, b in block_ranges(section, 'divi/column')]


def text_module(label, html, heading=False, color='#353740', size='16px', align='left'):
    content_decoration = {
        'bodyFont': {'body': {'font': {'desktop': {'value': {
            'family': 'Montserrat', 'weight': '400', 'color': color,
            'size': size, 'lineHeight': '1.7em',
        }}}}},
    }
    if heading:
        content_decoration['headingFont'] = {'h2': {'font': {
            'desktop': {'value': {'family': 'Montserrat', 'weight': '700', 'color': color, 'size': '42px', 'lineHeight': '1.2em', 'textAlign': align}},
            'phone': {'value': {'size': '30px', 'lineHeight': '1.2em', 'textAlign': align}},
        }}}
    attrs = {
        'module': {
            'meta': {'adminLabel': {'desktop': {'value': label}}},
            'advanced': {'text': {'text': {'desktop': {'value': {'orientation': align}}}}},
            'decoration': {'layout': {'desktop': {'value': {'display': 'block'}}}},
        },
        'content': {
            'decoration': content_decoration,
            'innerContent': {'desktop': {'value': html}},
        },
        'builderVersion': '5.11.1',
    }
    return '<!-- wp:divi/text ' + json.dumps(attrs, separators=(',', ':')) + ' /-->'


def tab(label, title, recommendation, questions):
    items = ''.join(f'<li>{q}</li>' for q in questions)
    html = f'<h3>{title}</h3><p>{recommendation}</p><ul>{items}</ul><p><strong>Recommended request:</strong> {title}</p>'
    attrs = {
        'module': {'meta': {'adminLabel': {'desktop': {'value': label}}}},
        'tab': {'innerContent': {'desktop': {'value': {'title': label, 'content': html}}}},
        'builderVersion': '5.11.1',
    }
    return '<!-- wp:divi/tab ' + json.dumps(attrs, separators=(',', ':')) + ' /-->'


def build_workflow_section():
    tabs = [
        tab('Airport Transfer', 'Airport Transfer', 'For arrivals, departures, and round trips between an airport and a hotel, resort, villa, or private address.', [
            'Are you arriving, departing, or booking a round trip?',
            'Which airport and what is the flight number?',
            'What hotel, resort, villa, or address are you traveling to?',
            'How many passengers, bags, and child seats?',
        ]),
        tab('Hotel Transfer', 'Hotel or Point-to-Point Transfer', 'For travel between resorts, hotels, villas, restaurants, marinas, and cities.', [
            'What are the pickup and destination addresses?',
            'One way, return, or multiple stops?',
            'What date and pickup time?',
            'How many passengers and pieces of luggage?',
        ]),
        tab('Tours', 'Tour and Excursion Transportation', 'For Saona Island departures, Santo Domingo, beaches, attractions, and custom sightseeing days.', [
            'Which destination or activity interests you?',
            'Do you already have excursion tickets?',
            'Where should we pick up your group?',
            'Would you like a fixed return time or a flexible itinerary?',
        ]),
        tab('Private Driver', 'Private Driver or Special Group', 'For hourly chauffeurs, weddings, events, large groups, accessibility needs, and custom itineraries.', [
            'How many hours or days do you need a driver?',
            'Which stops should be included?',
            'How many passengers are traveling?',
            'Do you need a specific vehicle, accessibility support, or luggage capacity?',
        ]),
    ]
    tabs_markup = '\n'.join(tabs)
    return f'''<!-- wp:divi/section {{"module":{{"meta":{{"adminLabel":{{"desktop":{{"value":"Service Finder Workflow"}}}}}},"decoration":{{"background":{{"desktop":{{"value":{{"color":"#f5f7fb"}}}}}},"spacing":{{"desktop":{{"value":{{"padding":{{"top":"88px","right":"0px","bottom":"88px","left":"0px","syncVertical":"off","syncHorizontal":"on"}}}}}},"phone":{{"value":{{"padding":{{"top":"54px","right":"0px","bottom":"54px","left":"0px","syncVertical":"off","syncHorizontal":"on"}}}}}}}}}}}},"builderVersion":"5.11.1"}} -->
<!-- wp:divi/row {{"module":{{"meta":{{"adminLabel":{{"desktop":{{"value":"Wide Service Finder Heading"}}}}}},"advanced":{{"columnStructure":{{"desktop":{{"value":"4_4"}}}}}},"decoration":{{"sizing":{{"desktop":{{"value":{{"width":"94%","maxWidth":"1440px"}}}},"tablet":{{"value":{{"width":"92%","maxWidth":"1440px"}}}},"phone":{{"value":{{"width":"90%","maxWidth":"1440px"}}}}}},"spacing":{{"desktop":{{"value":{{"margin":{{"bottom":"42px"}}}}}},"phone":{{"value":{{"margin":{{"bottom":"28px"}}}}}}}}}}}},"builderVersion":"5.11.1"}} -->
<!-- wp:divi/column {{"module":{{"advanced":{{"type":{{"desktop":{{"value":"4_4"}}}}}},"decoration":{{"layout":{{"desktop":{{"value":{{"display":"block"}}}}}}}}}},"builderVersion":"5.11.1"}} -->
{text_module('Service Finder Eyebrow','<p>Not sure what to book?</p>',color='#d7770b',size='15px',align='center')}
{text_module('Service Finder Title','<h2>Find the right transportation service</h2>',heading=True,color='#141630',align='center')}
{text_module('Service Finder Intro','<p>Choose the situation that sounds closest to your trip. We will show you the details needed to prepare the correct service request.</p>',color='#5f6673',size='17px',align='center')}
<!-- /wp:divi/column -->
<!-- /wp:divi/row -->
<!-- wp:divi/row {{"module":{{"meta":{{"adminLabel":{{"desktop":{{"value":"Wide Service Finder Workspace"}}}}}},"advanced":{{"columnStructure":{{"desktop":{{"value":"4_4"}}}}}},"decoration":{{"sizing":{{"desktop":{{"value":{{"width":"94%","maxWidth":"1440px"}}}},"tablet":{{"value":{{"width":"92%","maxWidth":"1440px"}}}},"phone":{{"value":{{"width":"90%","maxWidth":"1440px"}}}}}},"background":{{"desktop":{{"value":{{"color":"#ffffff"}}}}}},"border":{{"desktop":{{"value":{{"radius":{{"sync":"on","topLeft":"22px","topRight":"22px","bottomRight":"22px","bottomLeft":"22px"}},"styles":{{"all":{{"width":"1px","color":"#e3e7ef"}}}}}}}},"spacing":{{"desktop":{{"value":{{"padding":{{"top":"34px","right":"34px","bottom":"34px","left":"34px","syncVertical":"on","syncHorizontal":"on"}}}}}},"phone":{{"value":{{"padding":{{"top":"20px","right":"16px","bottom":"20px","left":"16px","syncVertical":"on","syncHorizontal":"on"}}}}}}}}}}}},"builderVersion":"5.11.1"}} -->
<!-- wp:divi/column {{"module":{{"advanced":{{"type":{{"desktop":{{"value":"4_4"}}}}}},"decoration":{{"layout":{{"desktop":{{"value":{{"display":"block"}}}}}}}}}},"builderVersion":"5.11.1"}} -->
<!-- wp:divi/tabs {{"module":{{"meta":{{"adminLabel":{{"desktop":{{"value":"Service Finder Paths"}}}}}},"decoration":{{"border":{{"desktop":{{"value":{{"radius":{{"sync":"on","topLeft":"16px","topRight":"16px","bottomRight":"16px","bottomLeft":"16px"}}}}}}}}}}}},"builderVersion":"5.11.1"}} -->
{tabs_markup}
<!-- /wp:divi/tabs -->
<!-- /wp:divi/column -->
<!-- /wp:divi/row -->
<!-- /wp:divi/section -->'''


def build_contact_section(existing_form):
    return f'''<!-- wp:divi/section {{"module":{{"meta":{{"adminLabel":{{"desktop":{{"value":"Contact Request Workspace"}}}}}},"decoration":{{"background":{{"desktop":{{"value":{{"color":"#ffffff"}}}}}},"spacing":{{"desktop":{{"value":{{"padding":{{"top":"92px","right":"0px","bottom":"92px","left":"0px","syncVertical":"off","syncHorizontal":"on"}}}}}},"phone":{{"value":{{"padding":{{"top":"56px","right":"0px","bottom":"56px","left":"0px","syncVertical":"off","syncHorizontal":"on"}}}}}}}}}}}},"builderVersion":"5.11.1"}} -->
<!-- wp:divi/row {{"module":{{"meta":{{"adminLabel":{{"desktop":{{"value":"Wide Contact Form Row"}}}}}},"advanced":{{"columnStructure":{{"desktop":{{"value":"2_3,1_3"}}}}}},"decoration":{{"sizing":{{"desktop":{{"value":{{"width":"94%","maxWidth":"1440px"}}}},"tablet":{{"value":{{"width":"92%","maxWidth":"1440px"}}}},"phone":{{"value":{{"width":"90%","maxWidth":"1440px"}}}}}},"layout":{{"desktop":{{"value":{{"flexWrap":"nowrap"}}}},"tablet":{{"value":{{"flexWrap":"wrap"}}}},"phone":{{"value":{{"flexWrap":"wrap"}}}}}}}}}},"builderVersion":"5.11.1"}} -->
<!-- wp:divi/column {{"module":{{"advanced":{{"type":{{"desktop":{{"value":"2_3"}}}}}},"decoration":{{"sizing":{{"desktop":{{"value":{{"flexType":"16_24"}}}},"tablet":{{"value":{{"flexType":"24_24"}}}},"phone":{{"value":{{"flexType":"24_24"}}}}}},"background":{{"desktop":{{"value":{{"color":"#f5f7fb"}}}}}},"border":{{"desktop":{{"value":{{"radius":{{"sync":"on","topLeft":"22px","topRight":"22px","bottomRight":"22px","bottomLeft":"22px"}}}}}}}},"spacing":{{"desktop":{{"value":{{"padding":{{"top":"44px","right":"44px","bottom":"44px","left":"44px","syncVertical":"on","syncHorizontal":"on"}}}}}},"phone":{{"value":{{"padding":{{"top":"26px","right":"20px","bottom":"26px","left":"20px","syncVertical":"on","syncHorizontal":"on"}}}}}}}}}}}},"builderVersion":"5.11.1"}} -->
{text_module('Request Title','<h2>Request your transportation</h2>',heading=True,color='#141630')}
{text_module('Gravity Forms Migration Note','<p>Tell us what you selected above and share your trip details. This form area is prepared for the Gravity Forms service finder.</p>',color='#5f6673',size='16px')}
{existing_form}
<!-- /wp:divi/column -->
<!-- wp:divi/column {{"module":{{"advanced":{{"type":{{"desktop":{{"value":"1_3"}}}}}},"decoration":{{"sizing":{{"desktop":{{"value":{{"flexType":"8_24"}}}},"tablet":{{"value":{{"flexType":"24_24"}}}},"phone":{{"value":{{"flexType":"24_24"}}}}}},"background":{{"desktop":{{"value":{{"color":"#141630"}}}}}},"border":{{"desktop":{{"value":{{"radius":{{"sync":"on","topLeft":"22px","topRight":"22px","bottomRight":"22px","bottomLeft":"22px"}}}}}}}},"spacing":{{"desktop":{{"value":{{"padding":{{"top":"44px","right":"38px","bottom":"44px","left":"38px","syncVertical":"on","syncHorizontal":"on"}}}}}},"phone":{{"value":{{"padding":{{"top":"30px","right":"24px","bottom":"30px","left":"24px","syncVertical":"on","syncHorizontal":"on"}},"margin":{{"top":"24px"}}}}}}}}}}}},"builderVersion":"5.11.1"}} -->
{text_module('Direct Help','<h2>Prefer direct help?</h2>',heading=True,color='#ffffff')}
{text_module('Contact Details','<p>Send us your hotel, travel date, passenger count, and expected route. We will help identify the correct service.</p><p><strong>WhatsApp</strong><br><a href="https://wa.me/18299866861">+1 829 986 6861</a></p><p><strong>Email</strong><br><a href="mailto:starlopez978@gmail.com">starlopez978@gmail.com</a></p><p><strong>Service area</strong><br>Punta Cana and destinations across the Dominican Republic</p>',color='#e4e6ef',size='16px')}
<!-- /wp:divi/column -->
<!-- /wp:divi/row -->
<!-- /wp:divi/section -->'''


def gravity_schema():
    choices = [
        {'text': 'Airport arrival or departure', 'value': 'airport'},
        {'text': 'Hotel or point-to-point transfer', 'value': 'hotel'},
        {'text': 'Tour or excursion transportation', 'value': 'tour'},
        {'text': 'Private driver or special group', 'value': 'private'},
        {'text': 'I am not sure', 'value': 'unsure'},
    ]
    def logic(value):
        return {'actionType': 'show', 'logicType': 'any', 'rules': [{'fieldId': '1', 'operator': 'is', 'value': value}]}
    fields = [
        {'type': 'radio', 'id': 1, 'label': 'What transportation do you need?', 'adminLabel': 'Service Path', 'isRequired': True, 'choices': choices},
        {'type': 'page', 'id': 2, 'label': 'Service Details', 'nextButton': {'type': 'text', 'text': 'Continue'}, 'previousButton': {'type': 'text', 'text': 'Back'}},
        {'type': 'select', 'id': 3, 'label': 'Airport trip type', 'choices': [{'text': x, 'value': x.lower().replace(' ', '_')} for x in ['Arrival', 'Departure', 'Round Trip']], 'conditionalLogic': logic('airport')},
        {'type': 'text', 'id': 4, 'label': 'Airport and flight number', 'conditionalLogic': logic('airport')},
        {'type': 'text', 'id': 5, 'label': 'Pickup location', 'conditionalLogic': {'actionType': 'show', 'logicType': 'any', 'rules': [{'fieldId': '1', 'operator': 'is', 'value': v} for v in ['hotel', 'tour', 'private', 'unsure']]}},
        {'type': 'text', 'id': 6, 'label': 'Destination or places you want to visit'},
        {'type': 'select', 'id': 7, 'label': 'Trip format', 'choices': [{'text': x, 'value': x.lower().replace(' ', '_')} for x in ['One Way', 'Round Trip', 'Multiple Stops', 'Hourly Driver']]},
        {'type': 'number', 'id': 8, 'label': 'Passengers', 'isRequired': True},
        {'type': 'number', 'id': 9, 'label': 'Pieces of luggage'},
        {'type': 'checkbox', 'id': 10, 'label': 'Additional needs', 'choices': [{'text': x, 'value': x.lower().replace(' ', '_')} for x in ['Child Seats', 'Accessible Vehicle', 'Large Luggage Capacity', 'Multiple Vehicles']]},
        {'type': 'page', 'id': 11, 'label': 'Trip and Contact Information', 'nextButton': {'type': 'text', 'text': 'Review Request'}, 'previousButton': {'type': 'text', 'text': 'Back'}},
        {'type': 'date', 'id': 12, 'label': 'Travel date', 'isRequired': True},
        {'type': 'time', 'id': 13, 'label': 'Pickup time'},
        {'type': 'name', 'id': 14, 'label': 'Name', 'isRequired': True},
        {'type': 'email', 'id': 15, 'label': 'Email', 'isRequired': True},
        {'type': 'phone', 'id': 16, 'label': 'WhatsApp or phone number', 'isRequired': True},
        {'type': 'textarea', 'id': 17, 'label': 'Anything else we should know?'},
    ]
    return [{
        'title': 'BD Star Service Finder',
        'description': 'Guided transportation questionnaire for airport, hotel, tour, and private-driver requests.',
        'labelPlacement': 'top_label',
        'descriptionPlacement': 'below',
        'button': {'type': 'text', 'text': 'Request This Service'},
        'fields': fields,
        'confirmations': [{'id': 'bdstar_confirmation', 'name': 'Default Confirmation', 'isDefault': True, 'type': 'message', 'message': 'Thank you. We received your transportation request and will contact you shortly.'}],
        'notifications': [],
        'version': '2.9',
    }]


def main():
    contact = json.loads((ROOT / 'bdstar-contact-v5.json').read_text())
    contact_payload = contact['data']['2']
    services = json.loads((ROOT / 'releases/bdstar-services-hero-slider-v1.json').read_text())
    services_payload = services['data']['2']

    current_hero = first_section(contact_payload, 'Contact Split Hero')
    slider_hero = first_section(services_payload, 'Services Hero Image Slider')
    contact_left = first_columns(current_hero)[0]
    contact_left = contact_left.replace('#353740', '#e4e6ef').replace('"right":"8%"', '"right":"4%"').replace('"left":"8%"', '"left":"4%"')
    slider_columns = first_columns(slider_hero)
    slider_hero = slider_hero.replace(slider_columns[0], contact_left, 1)
    slider_hero = slider_hero.replace('Services Hero Image Slider', 'Contact Hero Image Slider', 1)

    old_body = first_section(contact_payload, 'Contact Body')
    form_start, form_end = block_ranges(old_body, 'divi/contact-form')[0]
    existing_form = old_body[form_start:form_end]
    redesigned = build_workflow_section() + '\n\n' + build_contact_section(existing_form)
    malformed = '"right":"16px","bottom":"20px","left":"16px","syncVertical":"on","syncHorizontal":"on"}}}}}},"builderVersion"'
    corrected = '"right":"16px","bottom":"20px","left":"16px","syncVertical":"on","syncHorizontal":"on"}}}}}}},"builderVersion"'
    redesigned = redesigned.replace(malformed, corrected, 1)

    new_payload = contact_payload.replace(current_hero, slider_hero, 1).replace(old_body, redesigned, 1)
    contact['data']['2'] = new_payload
    contact['images'] = services.get('images', contact.get('images', []))

    release = ROOT / 'releases' / 'bdstar-contact-service-finder-v1.json'
    release.write_text(json.dumps(contact, ensure_ascii=False, separators=(',', ':')) + '\n')

    hero_source = ROOT / 'Modules/contact/sections/01-contact-split-hero.divi'
    body_source = ROOT / 'Modules/contact/sections/03-contact-body.divi'
    hero_source.write_text(slider_hero)
    body_source.write_text(redesigned)

    schema_dir = ROOT / 'gravity-forms'
    schema_dir.mkdir(exist_ok=True)
    (schema_dir / 'bdstar-service-finder.json').write_text(json.dumps(gravity_schema(), ensure_ascii=False, indent=2) + '\n')

    print(release)
    print(schema_dir / 'bdstar-service-finder.json')


if __name__ == '__main__':
    main()
