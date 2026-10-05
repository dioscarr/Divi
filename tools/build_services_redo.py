import json, sys
from pathlib import Path

BASE = Path('/home/dioscarr/Work/divi-working-set')
sys.path.append(str(BASE / 'tools'))
import divi_modules

SECDIR = BASE / 'Modules/services/sections'
SECDIR.mkdir(parents=True, exist_ok=True)

def b(name, attrs, children=None):
    s = json.dumps(attrs, separators=(',', ':'), ensure_ascii=True)
    if children is None:
        return f'<!-- wp:divi/{name} {s} /-->'
    return f'<!-- wp:divi/{name} {s} -->\n{children}\n<!-- /wp:divi/{name} -->'

# SVGs
SVG_PLANE = '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fcd21d" aria-hidden="true"><path d="M3.478 2.404a.75.75 0 00-.926.941l2.432 7.905H13.5a.75.75 0 010 1.5H4.984l-2.432 7.905a.75.75 0 00.926.94c6.699-1.946 12.92-5.014 18.445-8.987a.75.75 0 000-1.218C16.398 7.418 10.177 4.35 3.478 2.404z"/></svg>'
SVG_SHIELD = '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fcd21d" aria-hidden="true"><path fill-rule="evenodd" clip-rule="evenodd" d="M12.516 2.17a.75.75 0 00-1.032 0 11.209 11.209 0 01-7.877 3.08.75.75 0 00-.722.515A12.74 12.74 0 002.25 9.75c0 5.942 4.064 10.933 9.563 12.348a.749.749 0 00.374 0c5.499-1.415 9.563-6.406 9.563-12.348 0-1.39-.223-2.73-.635-3.985a.75.75 0 00-.722-.516l-.143.001c-2.996 0-5.717-1.17-7.734-3.08zm3.094 8.016a.75.75 0 10-1.22-.872l-3.236 4.53L9.53 12.22a.75.75 0 00-1.06 1.06l2.25 2.25a.75.75 0 001.14-.094l3.75-5.25z"/></svg>'
SVG_STAR = '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fcd21d" aria-hidden="true"><path fill-rule="evenodd" clip-rule="evenodd" d="M10.788 3.21c.448-1.077 1.976-1.077 2.424 0l2.082 5.006 5.404.434c1.164.093 1.636 1.545.749 2.305l-4.117 3.527 1.257 5.273c.271 1.136-.964 2.033-1.96 1.425L12 18.354 7.373 21.18c-.996.608-2.231-.29-1.96-1.425l1.257-5.273-4.117-3.527c-.887-.76-.415-2.212.749-2.305l5.404-.434 2.082-5.005z"/></svg>'
SVG_HEART = '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fcd21d" aria-hidden="true"><path d="M11.645 20.91l-.007-.003-.022-.012a15.247 15.247 0 01-.383-.218 25.18 25.18 0 01-4.244-3.17C4.688 15.36 2.25 12.174 2.25 8.25 2.25 5.322 4.714 3 7.688 3A5.5 5.5 0 0112 5.052 5.5 5.5 0 0116.313 3c2.973 0 5.437 2.322 5.437 5.25 0 3.925-2.438 7.111-4.739 9.256a25.175 25.175 0 01-4.244 3.17 15.247 15.247 0 01-.383.219l-.022.012-.007.004-.003.001a.752.752 0 01-.704 0l-.003-.001z"/></svg>'
SVG_CLOCK = '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fcd21d" aria-hidden="true"><path fill-rule="evenodd" clip-rule="evenodd" d="M12 2.25c-5.385 0-9.75 4.365-9.75 9.75s4.365 9.75 9.75 9.75 9.75-4.365 9.75-9.75S17.385 2.25 12 2.25zM12.75 6a.75.75 0 00-1.5 0v6c0 .414.336.75.75.75h4.5a.75.75 0 000-1.5h-3.75V6z"/></svg>'
SVG_CHAT = '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fcd21d" aria-hidden="true"><path fill-rule="evenodd" clip-rule="evenodd" d="M4.848 2.772A49.11 49.11 0 0112 2.25c2.43 0 4.817.177 7.152.522 1.45.213 2.598 1.34 2.84 2.775a49.65 49.65 0 010 12.906c-.242 1.435-1.39 2.562-2.84 2.775a49.033 49.033 0 01-5.632.488l-4.197 3.148a.75.75 0 01-1.2-.6V21.1a49.336 49.336 0 01-3.275-.377C3.398 20.51 2.25 19.383 2.008 17.948a49.65 49.65 0 010-12.906c.242-1.435 1.39-2.562 2.84-2.775z"/></svg>'
SVG_VAN = '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fcd21d" aria-hidden="true"><path d="M3.375 4.5C2.339 4.5 1.5 5.34 1.5 6.375V13.5h1.564a3.375 3.375 0 016.622 0h4.628a3.375 3.375 0 016.622 0H22.5V9.75a3.375 3.375 0 00-3.375-3.375h-2.25V4.5H3.375zM14.344 15a1.875 1.875 0 103.75 0 1.875 1.875 0 00-3.75 0zM5.906 15a1.875 1.875 0 103.75 0 1.875 1.875 0 00-3.75 0z"/></svg>'
SVG_MAP = '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fcd21d" aria-hidden="true"><path fill-rule="evenodd" clip-rule="evenodd" d="M11.54 22.351l.07.04.028.016a.76.76 0 00.723 0l.028-.015.071-.041a16.975 16.975 0 001.144-.742 19.58 19.58 0 002.683-2.282c1.944-1.99 3.963-4.98 3.963-8.827a8.25 8.25 0 00-16.5 0c0 3.846 2.02 6.837 3.963 8.827a19.58 19.58 0 002.682 2.282 16.975 16.975 0 001.145.742zM12 13.5a3 3 0 100-6 3 3 0 000 6z"/></svg>'
SVG_SPARKLES = '<svg viewBox="0 0 24 24" width="18" height="18" fill="#fcd21d" aria-hidden="true"><path fill-rule="evenodd" clip-rule="evenodd" d="M9 4.5a.75.75 0 01.721.544l.813 2.846a3.75 3.75 0 002.576 2.576l2.846.813a.75.75 0 010 1.442l-2.846.813a3.75 3.75 0 00-2.576 2.576l-.813 2.846a.75.75 0 01-1.442 0l-.813-2.846a3.75 3.75 0 00-2.576-2.576l-2.846-.813a.75.75 0 010-1.442l2.846-.813a3.75 3.75 0 002.576-2.576l.813-2.846A.75.75 0 019 4.5z"/></svg>'

# ==============================================================================
# 01: Split Hero
# ==============================================================================
hero_t1 = b('text', {
    "module": {
        "decoration": {
            "spacing": {
                "desktop": {"value": {"margin": {"top": "", "right": "", "bottom": "36px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"margin": {"top": "", "bottom": "24.75px", "left": "", "right": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}},
            "animation": {"desktop": {"value": {"style": "slide", "direction": "bottom"}}}
        }
    },
    "content": {
        "decoration": {"bodyFont": {"body": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "500", "capitalization": "uppercase", "color": "#353740", "size": "16px", "letterSpacing": "3px"}}}}}},
        "innerContent": {"desktop": {"value": "Our Services"}}
    },
    "builderVersion": "5.11.1"
})

hero_t2 = b('text', {
    "module": {
        "decoration": {
            "spacing": {
                "desktop": {"value": {"margin": {"top": "", "right": "", "bottom": "32px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"margin": {"top": "", "bottom": "22px", "left": "", "right": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}},
            "animation": {"desktop": {"value": {"style": "fade"}}}
        }
    },
    "content": {
        "decoration": {"headingFont": {"h1": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "700", "capitalization": "uppercase", "color": "#f7f7f7", "size": "52px", "lineHeight": "1.3em"}}}}}},
        "innerContent": {"desktop": {"value": "<h1>Professional Family Transportation</h1>"}}
    },
    "builderVersion": "5.11.1"
})

hero_t3 = b('text', {
    "module": {
        "decoration": {
            "spacing": {
                "desktop": {"value": {"margin": {"top": "", "right": "", "bottom": "40px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"margin": {"top": "", "bottom": "27.5px", "left": "", "right": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}},
            "animation": {"desktop": {"value": {"style": "slide", "direction": "top", "intensity": {"slide": "17%"}}}}
        }
    },
    "content": {
        "decoration": {"bodyFont": {"body": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "400", "color": "#353740", "size": "18px", "lineHeight": "1.8em"}}}}}},
        "innerContent": {"desktop": {"value": "Stress-free airport transfers, private family excursions, and custom Dominican Republic tours with certified professional drivers."}}
    },
    "builderVersion": "5.11.1"
})

hero_btn = b('button', {
    "module": {
        "decoration": {
            "layout": {"desktop": {"value": {"display": "block"}}},
            "animation": {"desktop": {"value": {"style": "fade"}}}
        }
    },
    "button": {
        "innerContent": {"desktop": {"value": {"linkUrl": "/contact", "text": "Book Your Transfer Now"}}},
        "decoration": {
            "button": {"desktop": {"value": {"enable": "on", "icon": {"settings": {"unicode": "&#x45;", "type": "divi", "weight": "400"}}}}},
            "font": {"font": {"desktop": {"value": {"color": "#ffffff", "letterSpacing": "2px", "family": "Montserrat", "weight": "700", "capitalization": "uppercase"}, "hover": {"color": "#ffffff", "letterSpacing": "2px"}}}},
            "border": {"desktop": {"value": {"styles": {"all": {"width": "4px", "color": "#ffffff"}}, "radius": {"sync": "on", "topLeft": "100px", "topRight": "100px", "bottomRight": "100px", "bottomLeft": "100px"}}, "hover": {"styles": {"all": {"color": "#ffffff"}}}}},
            "background": {"desktop": {"hover": {"color": "rgba(0,0,0,0)"}}}
        }
    },
    "builderVersion": "5.11.1"
})

hero_col1 = b('column', {
    "module": {
        "advanced": {"type": {"desktop": {"value": "1_2"}}},
        "decoration": {
            "spacing": {
                "desktop": {"value": {"padding": {"top": "8%", "right": "8%", "bottom": "8%", "left": "8%", "syncVertical": "off", "syncHorizontal": "off"}}, "hover": {"padding": {"top": "", "right": "", "bottom": "", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"padding": {"top": "8%", "bottom": "8%", "left": "8%", "right": "8%", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}}
        }
    },
    "builderVersion": "5.11.1"
}, f'{hero_t1}\n{hero_t2}\n{hero_t3}\n{hero_btn}')

hero_col2 = b('column', {
    "module": {
        "advanced": {"type": {"desktop": {"value": "1_2"}}},
        "decoration": {
            "border": {"desktop": {"value": {"radius": {"sync": "on", "topLeft": "12px", "topRight": "12px", "bottomRight": "12px", "bottomLeft": "12px"}}}},
            "background": {"desktop": {"value": {"image": {"url": "https://wordpress-868870-6701729.cloudwaysapps.com/wp-content/uploads/2026/09/airport.png", "position": "center", "size": "cover", "repeat": "no-repeat", "parallax": {"enabled": "off"}}}}},
            "spacing": {"desktop": {"value": {"padding": {"top": "", "right": "", "bottom": "", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}, "hover": {"padding": {"top": "", "right": "", "bottom": "", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}},
            "layout": {"desktop": {"value": {"display": "block"}}}
        }
    },
    "builderVersion": "5.11.1"
}, '')

hero_row = b('row', {
    "module": {
        "advanced": {
            "gutter": {"desktop": {"value": {"enable": "on", "width": "1", "makeEqual": "on"}}},
            "htmlAttributes": {"desktop": {"value": {"class": "", "id": ""}}},
            "columnStructure": {"desktop": {"value": "1_2,1_2"}}
        },
        "decoration": {
            "background": {"desktop": {"value": {"color": "#fcd21d", "image": {"url": "https://wordpress-868870-6701729.cloudwaysapps.com/wp-content/uploads/2021/03/circle-background-pattern.png"}}}},
            "sizing": {"desktop": {"value": {"width": "100%", "maxWidth": "100%"}}, "tablet": {"value": {"width": "100%", "maxWidth": "100%"}}},
            "spacing": {
                "desktop": {"value": {"padding": {"top": "0px", "right": "", "bottom": "0px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"padding": {"top": "0px", "bottom": "0px", "left": "", "right": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}},
            "attributes": {"desktop": {"value": {"attributes": [{"id": "c9ae41a0-8283-4d6e-bc76-7137272354bd", "name": "class", "value": " et_pb_row_fullwidth", "adminLabel": "CSS Class"}]}}},
            "animation": {"desktop": {"value": {"style": "slide", "direction": "top", "intensity": {"slide": "3%"}}}}
        }
    },
    "builderVersion": "5.11.1"
}, f'{hero_col1}\n{hero_col2}')

hero_sec = b('section', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Services Split Hero"}}},
        "decoration": {
            "spacing": {
                "desktop": {"value": {"padding": {"top": "0px", "right": "", "bottom": "0px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "tablet": {"value": {"padding": {"top": "0px", "right": "", "bottom": "0px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"padding": {"top": "0px", "bottom": "0px", "left": "", "right": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}},
            "background": {"desktop": {"value": {}}},
            "animation": {"desktop": {"value": {"style": "zoom", "intensity": {"zoom": "4%"}}}}
        },
        "advanced": {"htmlAttributes": {"desktop": {"value": {"class": "bd-services-hero"}}}}
    },
    "builderVersion": "5.11.1"
}, hero_row)

(SECDIR / '01-services-split-hero.divi').write_text(hero_sec + '\n', encoding='utf-8')

# ==============================================================================
# Helper for 02, 03, 04 (Feature sections)
# ==============================================================================
def build_feature_section(sec_label, sec_bg, row_label, is_inverted, img_url, tag, title, lead, items, btn_text, btn_link):
    # Image column
    img_module = b('image', {
        "module": {
            "meta": {"adminLabel": {"desktop": {"value": f"{title} Image"}}},
            "advanced": {"sizing": {"desktop": {"value": {"forceFullwidth": "on"}}}},
            "decoration": {
                "border": {"desktop": {"value": {"styles": {"all": {"width": "0px"}}, "radius": {"sync": "on", "topLeft": "12px", "topRight": "12px", "bottomRight": "12px", "bottomLeft": "12px"}}}},
                "boxShadow": {"desktop": {"value": {"style": "custom", "horizontal": "0px", "vertical": "12px", "blur": "32px", "spread": "-12px", "color": "rgba(20,22,48,0.24)"}}},
                "layout": {"desktop": {"value": {"display": "block"}}}
            }
        },
        "image": {"innerContent": {"desktop": {"value": {"src": img_url}}}},
        "builderVersion": "5.11.1"
    })
    
    img_col = b('column', {
        "module": {
            "advanced": {"type": {"desktop": {"value": "1_2"}}},
            "decoration": {
                "sizing": {"desktop": {"value": {"flexType": "12_24"}}, "phone": {"value": {"flexType": "24_24"}}},
                "layout": {"desktop": {"value": {"display": "flex", "alignItems": "center"}}}
            }
        },
        "builderVersion": "5.11.1"
    }, img_module)

    # Content column
    items_html = []
    for icon_svg, st, sp in items:
        items_html.append(f'<div class="bd-family-trust-item"><div class="bd-family-trust-icon">{icon_svg}</div><div class="bd-family-trust-text"><strong>{st}</strong><span>{sp}</span></div></div>')
    grid_html = '<div class="bd-family-trust-grid">' + ''.join(items_html) + '</div>'
    body_html = f'<div class="bd-family-trust-body"><span style="display:inline-block;font-family:Montserrat,sans-serif;font-size:12px;font-weight:700;color:#de7e0a;letter-spacing:2px;text-transform:uppercase;margin-bottom:8px;">{tag}</span><h2 style="margin:0 0 10px;font-family:Montserrat,sans-serif;font-size:32px;font-weight:700;color:#353740;line-height:1.25em;letter-spacing:0.01em;text-transform:uppercase;">{title}</h2><p style="margin:0 0 20px;font-family:Montserrat,sans-serif;font-weight:400;color:#747d88;font-size:15px;line-height:1.65em;">{lead}</p>{grid_html}</div>'

    text_module = b('text', {
        "module": {
            "meta": {"adminLabel": {"desktop": {"value": "Trust Body & Grid"}}},
            "decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}
        },
        "content": {"innerContent": {"desktop": {"value": body_html}}},
        "builderVersion": "5.11.1"
    })

    btn_module = b('button', {
        "module": {
            "meta": {"adminLabel": {"desktop": {"value": "Feature Action Button"}}},
            "advanced": {"alignment": {"desktop": {"value": "left"}}},
            "decoration": {
                "layout": {"desktop": {"value": {"display": "block"}}},
                "spacing": {"desktop": {"value": {"margin": {"top": "16px", "right": "", "bottom": "0px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}}
            }
        },
        "button": {
            "innerContent": {"desktop": {"value": {"linkUrl": btn_link, "text": btn_text}}},
            "decoration": {
                "button": {"desktop": {"value": {"enable": "on", "icon": {"settings": {"unicode": "&#x45;", "type": "divi", "weight": "400"}}, "color": "#ffffff"}}, "hover": {"value": {"enable": "on"}}},
                "font": {"font": {"desktop": {"value": {"color": "#ffffff", "letterSpacing": "2px", "family": "Montserrat", "weight": "700", "capitalization": "uppercase"}, "hover": {"color": "#ffffff", "letterSpacing": "2px"}}}},
                "border": {"desktop": {"value": {"styles": {"all": {"width": "0px", "color": "#141630"}}, "radius": {"sync": "on", "topLeft": "100px", "topRight": "100px", "bottomRight": "100px", "bottomLeft": "100px"}}}},
                "background": {"desktop": {"value": {"color": "#141630"}, "hover": {"color": "#de7e0a", "enableColor": "on"}}}
            }
        },
        "builderVersion": "5.11.1"
    })

    panel_col = b('column', {
        "module": {
            "advanced": {"type": {"desktop": {"value": "1_2"}}},
            "decoration": {
                "sizing": {"desktop": {"value": {"flexType": "12_24"}}, "phone": {"value": {"flexType": "24_24"}}},
                "spacing": {
                    "desktop": {"value": {"padding": {"top": "8px", "right": "12px", "bottom": "8px", "left": "12px", "syncVertical": "on", "syncHorizontal": "on"}}},
                    "phone": {"value": {"padding": {"top": "0px", "right": "0px", "bottom": "0px", "left": "0px", "syncVertical": "on", "syncHorizontal": "on"}}}
                },
                "layout": {"desktop": {"value": {"display": "flex", "flexDirection": "column", "justifyContent": "center", "alignItems": "stretch"}}}
            }
        },
        "builderVersion": "5.11.1"
    }, f'{text_module}\n{btn_module}')

    cols = f'{panel_col}\n{img_col}' if is_inverted else f'{img_col}\n{panel_col}'

    row = b('row', {
        "module": {
            "meta": {"adminLabel": {"desktop": {"value": row_label}}},
            "advanced": {
                "columnStructure": {"desktop": {"value": "1_2,1_2"}},
                "flexColumnStructure": {"desktop": {"value": "equal-columns_2"}}
            },
            "decoration": {
                "sizing": {"desktop": {"value": {"width": "90%", "maxWidth": "1200px"}}, "phone": {"value": {"width": "92%", "maxWidth": "100%"}}},
                "spacing": {"desktop": {"value": {"padding": {"top": "0px", "right": "", "bottom": "0px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}},
                "layout": {"desktop": {"value": {"flexWrap": "nowrap", "columnGap": "36px", "alignItems": "center"}}, "phone": {"value": {"flexWrap": "wrap", "rowGap": "24px"}}}
            }
        },
        "builderVersion": "5.11.1"
    }, cols)

    sec = b('section', {
        "module": {
            "meta": {"adminLabel": {"desktop": {"value": sec_label}}},
            "advanced": {"htmlAttributes": {"desktop": {"value": {"class": "bd-services-feature-section"}}}},
            "decoration": {
                "background": {"desktop": {"value": {"color": sec_bg}}},
                "spacing": {
                    "desktop": {"value": {"padding": {"top": "48px", "right": "", "bottom": "48px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                    "phone": {"value": {"padding": {"top": "24px", "right": "", "bottom": "24px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}
                },
                "layout": {"desktop": {"value": {"display": "block"}}}
            }
        },
        "builderVersion": "5.11.1"
    }, row)

    return sec

# 02
sec02 = build_feature_section(
    "Airport Transfers Section",
    "#ffffff",
    "Airport Feature Row",
    False,
    "https://wordpress-868870-6701729.cloudwaysapps.com/wp-content/uploads/2026/09/transport2.png",
    "Punta Cana Airport (PUJ)",
    "Private Airport Transfers",
    "Direct, stress-free transfers between Punta Cana International Airport (PUJ) and your resort or villa. Your chauffeur tracks your flight in real time and handles all luggage with care.",
    [
        (SVG_PLANE, "Real-Time Flight Tracking", "Automatic pickup adjustment for delays"),
        (SVG_CHAT, "Meet &amp; Greet Service", "Chauffeur with name sign at customs exit"),
        (SVG_CLOCK, "60 Min Free Waiting", "Relaxed airport exit with zero extra fees"),
        (SVG_HEART, "Free Child Safety Seats", "Sanitized infant and booster car seats")
    ],
    "Book Airport Transfer",
    "/contact"
)
(SECDIR / '02-feature-section.divi').write_text(sec02 + '\n', encoding='utf-8')

# 03
sec03 = build_feature_section(
    "Family Trips Section",
    "#f7f7f7",
    "Family Trips Row",
    True,
    "https://wordpress-868870-6701729.cloudwaysapps.com/wp-content/uploads/2026/09/explore.png",
    "Exclusive Family Travel",
    "Family Private &amp; Group Trips",
    "Travel together on your own schedule without the stress of crowded shuttles. Dedicated private vans and minibuses tailored to your family's baggage, comfort, and schedule.",
    [
        (SVG_VAN, "Spacious Modern Fleet", "Air-conditioned vans with ample legroom"),
        (SVG_CLOCK, "Flexible Itineraries", "Custom stops, grocery runs &amp; timing"),
        (SVG_SHIELD, "Licensed &amp; Insured", "Full commercial passenger liability"),
        (SVG_CHAT, "Bilingual Chauffeurs", "Friendly English and Spanish support")
    ],
    "Reserve Family Vehicle",
    "/contact"
)
(SECDIR / '03-feature-section.divi').write_text(sec03 + '\n', encoding='utf-8')

# 04
sec04 = build_feature_section(
    "Tours & Excursions Section",
    "#ffffff",
    "Tours Feature Row",
    False,
    "https://wordpress-868870-6701729.cloudwaysapps.com/wp-content/uploads/2026/09/explore.png",
    "Explore The Dominican Republic",
    "Private Tours &amp; Excursions",
    "Discover the authentic Dominican Republic at your own pace. Custom day trips to Saona Island, historic Santo Domingo, and secluded beaches with your own private vehicle and chauffeur.",
    [
        (SVG_MAP, "Custom Sightseeing", "Tailored itineraries for beaches &amp; culture"),
        (SVG_SHIELD, "Dedicated Chauffeur", "Your vehicle stays with you all day"),
        (SVG_VAN, "Door-to-Door Service", "Direct pickup and return from resort lobby"),
        (SVG_SPARKLES, "Chilled Refreshments", "Complimentary cold bottled water included")
    ],
    "Explore Custom Tours",
    "/contact"
)
(SECDIR / '04-feature-section.divi').write_text(sec04 + '\n', encoding='utf-8')

# ==============================================================================
# 05: Included with Every Ride
# ==============================================================================
def make_std_card(icon_svg, title, desc):
    inner = f'<div style="width:36px;height:36px;border-radius:8px;background:rgba(252,210,29,0.18);border:1px solid rgba(222,126,10,0.26);display:flex;align-items:center;justify-content:center;margin-bottom:16px;">{icon_svg}</div><h3 style="margin:0 0 10px;font-family:Montserrat,sans-serif;font-size:18px;font-weight:700;color:#353740;line-height:1.3em;">{title}</h3><p style="margin:0;font-family:Montserrat,sans-serif;font-size:14px;color:#747d88;line-height:1.6em;">{desc}</p>'
    txt = b('text', {
        "module": {
            "meta": {"adminLabel": {"desktop": {"value": f"{title} Content"}}},
            "decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}
        },
        "content": {"innerContent": {"desktop": {"value": inner}}},
        "builderVersion": "5.11.1"
    })
    clean_title = title.replace('&amp;', '&')
    grp = b('group', {
        "module": {
            "meta": {"adminLabel": {"desktop": {"value": f"{clean_title} Card"}}},
            "advanced": {"htmlAttributes": {"desktop": {"value": {"class": "bd-premium-service-card"}}}},
            "decoration": {
                "background": {"desktop": {"value": {"color": "#ffffff"}}},
                "border": {"desktop": {"value": {"styles": {"all": {"width": "1px", "color": "#e0e0e0", "style": "solid"}}, "radius": {"sync": "on", "topLeft": "12px", "topRight": "12px", "bottomRight": "12px", "bottomLeft": "12px"}}}},
                "boxShadow": {"desktop": {"value": {"style": "custom", "horizontal": "0px", "vertical": "4px", "blur": "16px", "spread": "0px", "color": "rgba(0,0,0,0.12)"}}},
                "layout": {"desktop": {"value": {"display": "flex", "flexDirection": "column", "alignItems": "flex-start"}}},
                "sizing": {"desktop": {"value": {"width": "100%", "height": "100%"}}},
                "spacing": {
                    "desktop": {"value": {"padding": {"top": "30px", "right": "30px", "bottom": "30px", "left": "30px", "syncVertical": "off", "syncHorizontal": "off"}}},
                    "phone": {"value": {"padding": {"top": "20px", "right": "20px", "bottom": "20px", "left": "20px", "syncVertical": "off", "syncHorizontal": "off"}}}
                }
            }
        },
        "builderVersion": "5.11.1"
    }, txt)
    col = b('column', {
        "module": {
            "advanced": {"type": {"desktop": {"value": "1_3"}}},
            "decoration": {"sizing": {"desktop": {"value": {"flexType": "8_24"}}, "phone": {"value": {"flexType": "24_24"}}}}
        },
        "builderVersion": "5.11.1"
    }, grp)
    return col

sec05_title = b('text', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Title"}}},
        "advanced": {"text": {"text": {"desktop": {"value": {"orientation": "center"}}}}},
        "decoration": {"sizing": {"desktop": {"value": {"maxWidth": "700px", "alignment": "center"}}}, "layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "content": {
        "decoration": {"headingFont": {"h2": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "700", "capitalization": "uppercase", "size": "42px", "lineHeight": "1.3em"}}}}}},
        "innerContent": {"desktop": {"value": "<h2>Included With Every Ride</h2>"}}
    },
    "builderVersion": "5.11.1"
})

sec05_sub = b('text', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Subtitle"}}},
        "advanced": {"text": {"text": {"desktop": {"value": {"orientation": "center"}}}}},
        "decoration": {"sizing": {"desktop": {"value": {"maxWidth": "700px", "alignment": "center"}}}, "layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "content": {
        "decoration": {"bodyFont": {"body": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "400", "color": "#747d88", "size": "16px", "lineHeight": "1.8em"}}}}}},
        "innerContent": {"desktop": {"value": "<p>Premium service is our standard, never an expensive upgrade.</p>"}}
    },
    "builderVersion": "5.11.1"
})

sec05_header_col = b('column', {
    "module": {"advanced": {"type": {"desktop": {"value": "4_4"}}}, "decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}},
    "builderVersion": "5.11.1"
}, f'{sec05_title}\n{sec05_sub}')

sec05_header_row = b('row', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Section Title"}}},
        "decoration": {
            "spacing": {
                "desktop": {"value": {"margin": {"top": "", "right": "", "bottom": "24px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"margin": {"top": "", "bottom": "16px", "left": "", "right": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}}
        }
    },
    "builderVersion": "5.11.1"
}, sec05_header_col)

r1_cards = [
    make_std_card(SVG_CHAT, "Personalized Meet &amp; Greet", "Your chauffeur greets you directly outside customs with a personalized name sign and assists with your luggage."),
    make_std_card(SVG_PLANE, "Real-Time Flight Tracking", "We monitor incoming flights live to ensure prompt pickup even if your plane arrives early or gets delayed."),
    make_std_card(SVG_HEART, "Complimentary Child Seats", "Sanitized, certified infant car seats, toddler seats, and booster seats provided free upon request.")
]
row1_std = b('row', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Services Cards Row 1"}}},
        "advanced": {"columnStructure": {"desktop": {"value": "1_3,1_3,1_3"}}, "flexColumnStructure": {"desktop": {"value": "equal-columns_3"}}},
        "decoration": {
            "sizing": {"desktop": {"value": {"width": "90%", "maxWidth": "1200px"}}, "phone": {"value": {"width": "92%", "maxWidth": "100%"}}},
            "spacing": {
                "desktop": {"value": {"margin": {"top": "", "right": "", "bottom": "24px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}, "padding": {"top": "0px", "right": "", "bottom": "0px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}},
                "phone": {"value": {"margin": {"top": "", "bottom": "16px", "left": "", "right": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"flexWrap": "nowrap", "columnGap": "24px"}}, "phone": {"value": {"flexWrap": "wrap", "rowGap": "16px"}}}
        }
    },
    "builderVersion": "5.11.1"
}, '\n'.join(r1_cards))

r2_cards = [
    make_std_card(SVG_SHIELD, "Bilingual Professional Drivers", "Fluent English &amp; Spanish speaking licensed chauffeurs dedicated to your family&#8217;s safety and comfort."),
    make_std_card(SVG_SPARKLES, "Climate Control &amp; Cold Water", "High-capacity air conditioning and cold bottled water ready for you the moment you step inside."),
    make_std_card(SVG_CLOCK, "24/7 Dispatch &amp; Support", "Round-the-clock WhatsApp and phone coordination for seamless updates, questions, or itinerary changes.")
]
row2_std = b('row', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Services Cards Row 2"}}},
        "advanced": {"columnStructure": {"desktop": {"value": "1_3,1_3,1_3"}}, "flexColumnStructure": {"desktop": {"value": "equal-columns_3"}}},
        "decoration": {
            "sizing": {"desktop": {"value": {"width": "90%", "maxWidth": "1200px"}}, "phone": {"value": {"width": "92%", "maxWidth": "100%"}}},
            "spacing": {"desktop": {"value": {"padding": {"top": "0px", "right": "", "bottom": "0px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}},
            "layout": {"desktop": {"value": {"flexWrap": "nowrap", "columnGap": "24px"}}, "phone": {"value": {"flexWrap": "wrap", "rowGap": "16px"}}}
        }
    },
    "builderVersion": "5.11.1"
}, '\n'.join(r2_cards))

sec05 = b('section', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Included With Every Ride Section"}}},
        "advanced": {"htmlAttributes": {"desktop": {"value": {"class": "bd-service-standard-section"}}}},
        "decoration": {
            "background": {"desktop": {"value": {"color": "#f7f7f7"}}},
            "spacing": {
                "desktop": {"value": {"padding": {"top": "40px", "right": "", "bottom": "40px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"padding": {"top": "24px", "right": "", "bottom": "24px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}}
        }
    },
    "builderVersion": "5.11.1"
}, f'{sec05_header_row}\n{row1_std}\n{row2_std}')

(SECDIR / '05-service-section.divi').write_text(sec05 + '\n', encoding='utf-8')

# ==============================================================================
# 06: Trust Numbers / Fun Facts
# ==============================================================================
def make_stat_col(num, title):
    cnt = b('number-counter', {
        "module": {"decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}},
        "title": {
            "innerContent": {"desktop": {"value": title}},
            "decoration": {"font": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "600", "capitalization": "uppercase", "color": "#353740", "size": "13px", "letterSpacing": "1px"}}}}}
        },
        "number": {
            "innerContent": {"desktop": {"value": num}},
            "advanced": {"enablePercentSign": {"desktop": {"value": "off"}}},
            "decoration": {"font": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "700", "color": "#141630", "size": "56px", "lineHeight": "1em"}}}}}
        },
        "builderVersion": "5.11.1"
    })
    col = b('column', {
        "module": {
            "advanced": {"type": {"desktop": {"value": "1_4"}}, "htmlAttributes": {"desktop": {"value": {"class": "bd-stat-counter-card"}}}},
            "decoration": {
                "spacing": {"desktop": {"value": {"padding": {"top": "24px", "right": "20px", "bottom": "24px", "left": "20px", "syncVertical": "off", "syncHorizontal": "off"}}}},
                "layout": {"desktop": {"value": {"display": "block"}}},
                "border": {"desktop": {"value": {"styles": {"all": {"width": "1px", "color": "#e0e0e0", "style": "solid"}}, "radius": {"sync": "on", "topLeft": "12px", "topRight": "12px", "bottomRight": "12px", "bottomLeft": "12px"}}}},
                "boxShadow": {"desktop": {"value": {"style": "custom", "horizontal": "0px", "vertical": "4px", "blur": "16px", "spread": "0px", "color": "rgba(0,0,0,0.12)"}}},
                "background": {"desktop": {"value": {"color": "#ffffff"}}}
            }
        },
        "builderVersion": "5.11.1"
    }, cnt)
    return col

sec06_title = b('text', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Title"}}},
        "advanced": {"text": {"text": {"desktop": {"value": {"orientation": "center"}}}}},
        "decoration": {"sizing": {"desktop": {"value": {"maxWidth": "700px", "alignment": "center"}}}, "layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "content": {
        "decoration": {"headingFont": {"h2": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "700", "capitalization": "uppercase", "color": "#353740", "size": "42px", "lineHeight": "1.3em"}}}}}},
        "innerContent": {"desktop": {"value": "<h2>A Decade Of Excellence</h2>"}}
    },
    "builderVersion": "5.11.1"
})

sec06_sub = b('text', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Subtitle"}}},
        "advanced": {"text": {"text": {"desktop": {"value": {"orientation": "center"}}}}},
        "decoration": {"sizing": {"desktop": {"value": {"maxWidth": "700px", "alignment": "center"}}}, "layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "content": {
        "decoration": {"bodyFont": {"body": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "500", "color": "#353740", "size": "16px", "lineHeight": "1.8em"}}}}}},
        "innerContent": {"desktop": {"value": "<p>By the numbers — ten years of safe, reliable, five-star family transportation in Punta Cana.</p>"}}
    },
    "builderVersion": "5.11.1"
})

sec06_header_col = b('column', {
    "module": {"advanced": {"type": {"desktop": {"value": "4_4"}}}, "decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}},
    "builderVersion": "5.11.1"
}, f'{sec06_title}\n{sec06_sub}')

sec06_header_row = b('row', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Numbers Title Row"}}},
        "decoration": {
            "spacing": {
                "desktop": {"value": {"margin": {"top": "", "right": "", "bottom": "24px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"margin": {"top": "", "bottom": "16px", "left": "", "right": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}}
        }
    },
    "builderVersion": "5.11.1"
}, sec06_header_col)

stat_cols = [
    make_stat_col('10', 'Years Serving Families'),
    make_stat_col('24', 'Hour Dispatch & Support'),
    make_stat_col('5', 'Star Rating on TripAdvisor'),
    make_stat_col('60', 'Minutes Free Wait Time')
]
sec06_grid_row = b('row', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Numbers Grid"}}},
        "decoration": {
            "spacing": {"desktop": {"value": {"padding": {"top": "0px", "right": "", "bottom": "0px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}},
            "layout": {"desktop": {"value": {"display": "block"}}},
            "sizing": {"desktop": {"value": {"width": "90%", "maxWidth": "1200px"}}, "phone": {"value": {"width": "92%", "maxWidth": "100%"}}}
        },
        "advanced": {"columnStructure": {"desktop": {"value": "1_4,1_4,1_4,1_4"}}}
    },
    "builderVersion": "5.11.1"
}, '\n'.join(stat_cols))

sec06 = b('section', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Trust Numbers Section"}}},
        "decoration": {
            "background": {"desktop": {"value": {"color": "#fcd21d"}}},
            "spacing": {
                "desktop": {"value": {"padding": {"top": "40px", "right": "", "bottom": "40px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"padding": {"top": "24px", "right": "", "bottom": "24px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}}
        }
    },
    "builderVersion": "5.11.1"
}, f'{sec06_header_row}\n{sec06_grid_row}')

(SECDIR / '06-fun-fact-section.divi').write_text(sec06 + '\n', encoding='utf-8')

# ==============================================================================
# 07: Services CTA Banner
# ==============================================================================
sec07_txt = b('text', {
    "module": {
        "advanced": {"text": {"text": {"desktop": {"value": {"orientation": "center"}}}}},
        "decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "content": {
        "decoration": {
            "headingFont": {"h2": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "700", "color": "#ffffff", "size": "34px", "capitalization": "uppercase", "lineHeight": "1.3em"}}}}},
            "bodyFont": {"body": {"font": {"desktop": {"value": {"family": "Montserrat", "color": "#c9cbe0", "size": "16px", "lineHeight": "1.7em"}}}}}
        },
        "innerContent": {"desktop": {"value": "<h2>Ready For A Smooth, Relaxing Trip?</h2><p style=\"margin-top:10px;\">Send us your dates, group size, and destination — we’ll confirm your reservation with transparent, fixed pricing and zero hidden fees.</p>"}}
    },
    "builderVersion": "5.11.1"
})

sec07_btn = b('button', {
    "module": {
        "advanced": {"alignment": {"desktop": {"value": "center"}}},
        "decoration": {
            "spacing": {
                "desktop": {"value": {"margin": {"top": "22px", "right": "", "bottom": "", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"margin": {"top": "16px", "bottom": "", "left": "", "right": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}}
        }
    },
    "button": {
        "innerContent": {"desktop": {"value": {"linkUrl": "/contact", "text": "Book Your Transfer Now"}}},
        "decoration": {
            "button": {"desktop": {"value": {"enable": "on", "icon": {"settings": {"unicode": "&#x45;", "type": "divi", "weight": "400"}}}}},
            "font": {"font": {"desktop": {"value": {"color": "#ffffff", "letterSpacing": "2px", "family": "Montserrat", "weight": "700", "capitalization": "uppercase"}}}},
            "background": {"desktop": {"value": {"color": "#de7e0a"}, "hover": {"color": "#ff9203", "enableColor": "on"}}},
            "border": {"desktop": {"value": {"styles": {"all": {"width": "0px"}}, "radius": {"sync": "on", "topLeft": "100px", "topRight": "100px", "bottomRight": "100px", "bottomLeft": "100px"}}}}
        }
    },
    "builderVersion": "5.11.1"
})

sec07_col = b('column', {
    "module": {
        "advanced": {"type": {"desktop": {"value": "4_4"}}, "text": {"text": {"desktop": {"value": {"orientation": "center"}}}}},
        "decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "builderVersion": "5.11.1"
}, f'{sec07_txt}\n{sec07_btn}')

sec07_row = b('row', {
    "module": {
        "advanced": {"columnStructure": {"desktop": {"value": "4_4"}}},
        "decoration": {"sizing": {"desktop": {"value": {"width": "80%", "maxWidth": "850px"}}}, "layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "builderVersion": "5.11.1"
}, sec07_col)

sec07 = b('section', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Services CTA"}}},
        "decoration": {
            "background": {"desktop": {"value": {"color": "#141630"}}},
            "spacing": {
                "desktop": {"value": {"padding": {"top": "50px", "right": "", "bottom": "50px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"padding": {"top": "32px", "right": "", "bottom": "32px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}}
        }
    },
    "builderVersion": "5.11.1"
}, sec07_row)

(SECDIR / '07-services-cta.divi').write_text(sec07 + '\n', encoding='utf-8')

# ==============================================================================
# 08: Frequently Asked Questions
# ==============================================================================
def make_faq_card(q, a):
    return f'<div class="bd-faq-card"><h3 style="margin:0 0 8px;font-family:Montserrat,sans-serif;font-size:16px;font-weight:700;color:#141630;line-height:1.35em;">{q}</h3><p style="margin:0;font-family:Montserrat,sans-serif;font-size:14px;color:#747d88;line-height:1.7em;">{a}</p></div>'

faq_col1_html = "".join([
    make_faq_card("Where do I meet my driver at Punta Cana Airport (PUJ)?", "Your chauffeur will be waiting right outside the customs arrival hall holding a personalized sign with your name. We also coordinate with you via WhatsApp as soon as your plane touches down."),
    make_faq_card("What happens if my flight is delayed or arrives early?", "We track all flights in real time using live satellite tracking. Your pickup schedule automatically updates with zero delay fees and up to 60 minutes of complimentary waiting time."),
    make_faq_card("Are child safety seats and booster seats available?", "Yes! We provide certified infant car seats, toddler seats, and booster seats completely free of charge upon request. Simply select your required seats when booking.")
])

faq_col2_html = "".join([
    make_faq_card("Is the transfer rate per person or per vehicle?", "All our rates are private and charged per vehicle, not per person. There are never any hidden baggage fees, airport parking charges, or fuel surcharges."),
    make_faq_card("Can we make stops along the way to our resort?", "Yes, absolutely. Because all our transfers are 100% private, you can request supermarket runs, pharmacy stops, or currency exchanges along your route."),
    make_faq_card("How do I book and pay for our transportation?", "You can book directly on our website or message us on WhatsApp. We accept secure credit card payments, online reservations, or cash on arrival.")
])

sec08_title = b('text', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Title"}}},
        "advanced": {"text": {"text": {"desktop": {"value": {"orientation": "center"}}}}},
        "decoration": {"sizing": {"desktop": {"value": {"maxWidth": "700px", "alignment": "center"}}}, "layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "content": {
        "decoration": {"headingFont": {"h2": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "700", "capitalization": "uppercase", "size": "42px", "lineHeight": "1.3em"}}}}}},
        "innerContent": {"desktop": {"value": "<h2>Frequently Asked Questions</h2>"}}
    },
    "builderVersion": "5.11.1"
})

sec08_sub = b('text', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "Subtitle"}}},
        "advanced": {"text": {"text": {"desktop": {"value": {"orientation": "center"}}}}},
        "decoration": {"sizing": {"desktop": {"value": {"maxWidth": "700px", "alignment": "center"}}}, "layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "content": {
        "decoration": {"bodyFont": {"body": {"font": {"desktop": {"value": {"family": "Montserrat", "weight": "400", "color": "#747d88", "size": "16px", "lineHeight": "1.8em"}}}}}},
        "innerContent": {"desktop": {"value": "<p>Common questions about airport pickups, private tours, car seats, and reservations.</p>"}}
    },
    "builderVersion": "5.11.1"
})

sec08_header_col = b('column', {
    "module": {"advanced": {"type": {"desktop": {"value": "4_4"}}}, "decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}},
    "builderVersion": "5.11.1"
}, f'{sec08_title}\n{sec08_sub}')

sec08_header_row = b('row', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "FAQ Title Row"}}},
        "decoration": {
            "spacing": {
                "desktop": {"value": {"margin": {"top": "", "right": "", "bottom": "24px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"margin": {"top": "", "bottom": "16px", "left": "", "right": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}}
        }
    },
    "builderVersion": "5.11.1"
}, sec08_header_col)

faq_t1 = b('text', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "FAQ Column 1"}}},
        "decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "content": {"innerContent": {"desktop": {"value": faq_col1_html}}},
    "builderVersion": "5.11.1"
})

faq_t2 = b('text', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "FAQ Column 2"}}},
        "decoration": {"layout": {"desktop": {"value": {"display": "block"}}}}
    },
    "content": {"innerContent": {"desktop": {"value": faq_col2_html}}},
    "builderVersion": "5.11.1"
})

faq_col1 = b('column', {
    "module": {
        "advanced": {"type": {"desktop": {"value": "1_2"}}},
        "decoration": {"sizing": {"desktop": {"value": {"flexType": "12_24"}}, "phone": {"value": {"flexType": "24_24"}}}}
    },
    "builderVersion": "5.11.1"
}, faq_t1)

faq_col2 = b('column', {
    "module": {
        "advanced": {"type": {"desktop": {"value": "1_2"}}},
        "decoration": {"sizing": {"desktop": {"value": {"flexType": "12_24"}}, "phone": {"value": {"flexType": "24_24"}}}}
    },
    "builderVersion": "5.11.1"
}, faq_t2)

sec08_grid_row = b('row', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "FAQ Grid Row"}}},
        "advanced": {"columnStructure": {"desktop": {"value": "1_2,1_2"}}, "flexColumnStructure": {"desktop": {"value": "equal-columns_2"}}},
        "decoration": {
            "sizing": {"desktop": {"value": {"width": "90%", "maxWidth": "1200px"}}, "phone": {"value": {"width": "92%", "maxWidth": "100%"}}},
            "spacing": {"desktop": {"value": {"padding": {"top": "0px", "right": "", "bottom": "0px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}},
            "layout": {"desktop": {"value": {"flexWrap": "nowrap", "columnGap": "24px"}}, "phone": {"value": {"flexWrap": "wrap", "rowGap": "16px"}}}
        }
    },
    "builderVersion": "5.11.1"
}, f'{faq_col1}\n{faq_col2}')

sec08 = b('section', {
    "module": {
        "meta": {"adminLabel": {"desktop": {"value": "FAQ Section"}}},
        "decoration": {
            "background": {"desktop": {"value": {"color": "#ffffff"}}},
            "spacing": {
                "desktop": {"value": {"padding": {"top": "40px", "right": "", "bottom": "50px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}},
                "phone": {"value": {"padding": {"top": "24px", "right": "", "bottom": "32px", "left": "", "syncVertical": "off", "syncHorizontal": "off"}}}
            },
            "layout": {"desktop": {"value": {"display": "block"}}}
        }
    },
    "builderVersion": "5.11.1"
}, f'{sec08_header_row}\n{sec08_grid_row}')

(SECDIR / '08-faq-section.divi').write_text(sec08 + '\n', encoding='utf-8')

print("All 8 sections built cleanly with 100% dictionary JSON generation!")
