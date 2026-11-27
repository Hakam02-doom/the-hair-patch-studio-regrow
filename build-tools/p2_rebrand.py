"""Project 2: apply The Hair Patch Studio branding, copy and site fixes to the pristine Regrow mirror.
usage: venv/bin/python -I p2_rebrand.py PRISTINE_DIR SITE_DIR ORIG_ASSETS_DIR"""
import os, re, sys, html, shutil
from bs4 import BeautifulSoup
sys.path.insert(0, os.path.dirname(__file__))
from p2_content import TEXT, COUNTERS, MARQUEE, PHONE, TEL, EMAIL, ADDRESS, MAPS

PR, SITE, OA = sys.argv[1:4]
ASSETS = os.path.join(SITE, 'assets')

COLOR_SUBS = [
    (r'(?i)#FF7B5F', '#FD9800'), (r'(?i)#F86A4C', '#E98C00'),
    (r'(?i)#FFF8F5', '#FFFDF7'), (r'(?i)#FAF2EA', '#FEF9E1'), (r'(?i)#F2DFD7', '#F9F0C8'),
    (r'(?i)#221B17', '#0F172A'), (r'(?i)#8B8582', '#454F5E'), (r'(?i)#B1A5A0', '#6B7585'),
    (r'(?i)#0A0A0A', '#0F172A'), (r'(?i)#151515', '#16213A'), (r'(?i)#383432', '#2A3550'),
    (r'(?i)#C4B4AE', '#C9D0DB'), (r'(?i)#A39893', '#9AA4B2'),
    (r'255,\s*123,\s*95', '253, 152, 0'), (r'248,\s*106,\s*76', '233, 140, 0'),
    (r'34,\s*27,\s*23', '15, 23, 42'), (r'255,\s*248,\s*245', '255, 253, 247'), (r'250,\s*242,\s*234', '254, 249, 225'),
    (r'"?Onest"?(,\s*sans-serif)?', "'Karla', sans-serif"),
    (r'(?i)#F5FA4F', '#FD9800'), (r'245,\s*250,\s*79', '253, 152, 0'),
    (r'(?i)#3DA5EF', '#0F172A'), (r'61,\s*165,\s*239', '15, 23, 42'),
]

TOK = re.compile(r'(<script\b.*?</script>|<style\b.*?</style>|<!--.*?-->|<[^>]+>)', re.S | re.I)

def norm(s): return ' '.join(html.unescape(s).replace('​', '').split())

def map_text(h):
    out = []
    for t in TOK.split(h):
        if not t: continue
        if t.startswith('<'):
            out.append(t); continue
        n = norm(t)
        key = n if n in TEXT else (n + '​' if n + '​' in TEXT else None)
        if n and key is not None:
            lead = t[:len(t) - len(t.lstrip())]; trail = t[len(t.rstrip()):]
            out.append(lead + html.escape(TEXT[key], quote=False) + trail)
        else:
            out.append(t)
    return ''.join(out)

def process(name):
    h = open(os.path.join(PR, name), encoding='utf-8').read()
    for a, b in COLOR_SUBS: h = re.sub(a, b, h)
    h = map_text(h)
    # MetForm templates live in a JS string: map visible strings there too
    for a, b in [('+1-310-555-0198', PHONE), ('[email protected]', EMAIL)]:
        h = h.replace(a, b)
    # counters (in page order)
    vals = iter(COUNTERS.get(name, []))
    h = re.sub(r'data-to="\d+"', lambda m: f'data-to="{next(vals, m.group(0)[9:-1])}"', h)
    # marquee text + delimiter (Regrow 'S' mark -> sparkle)
    h = re.sub(r'(&quot;bg_text&quot;:&quot;)Hair Transplantation(&quot;)', r'\g<1>' + MARQUEE + r'\2', h)
    h = re.sub(r'https?:(?:\\\\?/){2}regrow\.themerex\.net(?:\\\\?/)wp-content(?:\\\\?/)uploads(?:\\\\?/)2025(?:\\\\?/)09(?:\\\\?/)(logo-icon|marquee-icon-copyright)\.svg', r'assets/\1.svg', h)
    h = h.replace('Regrow', 'The Hair Patch Studio')

    soup = BeautifulSoup(h, 'html.parser')
    # --- remove demo / third-party leftovers
    for s in soup.find_all('script'):
        src = s.get('src', ''); body = s.string or ''
        if any(k in src for k in ('leadiosa', 'cdn-cgi', 'trx_demo', 'cloudflareinsights')) or 'leadiosa' in body or 'cdn-cgi/rum' in body or '__CF$cv$params' in body:
            s.decompose()
    for l in soup.find_all('link', href=re.compile(r'trx_demo|fonts\.googleapis|gfonts-')):
        l.decompose()
    for e in soup.select('.trx_demo_panels, .trx_demo_panel, .trx_addons_demo_panel, #trx_demo_panels, [class*=trx_demo_]'):
        e.decompose()
    # cloudflare-obfuscated emails -> real mailto
    for a in soup.select('a.__cf_email__, a[href*="email-protection"]'):
        a['href'] = f'mailto:{EMAIL}'; a.string = EMAIL
        for k in ('data-cfemail', 'class'): a.attrs.pop(k, None)
    for sp in soup.select('span.__cf_email__'):
        sp.replace_with(EMAIL)

    # --- decorative line drawings (laser hair-removal themed) -> flowing hair strands
    HAIR_SVG = ('<svg class="e-font-icon-svg hps-hair-lines" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg" fill="none" '
                'stroke="currentColor" stroke-width="3" stroke-linecap="round">'
                '<path d="M60 340C90 250 70 170 140 110S280 60 330 40"/>'
                '<path d="M90 352C118 268 110 190 170 134S300 92 350 74"/>'
                '<path d="M122 360C146 286 146 214 200 162S318 128 362 112"/>'
                '<path d="M156 364C174 304 182 240 228 194S334 166 370 152"/>'
                '<path d="M40 300C70 230 52 168 104 120"/></svg>')
    for wid in ('f21c6d0', '6a460c0', '95b09e9'):
        for w in soup.select(f'.elementor-element-{wid}'):
            old = w.find('svg')
            if old: old.replace_with(BeautifulSoup(HAIR_SVG, 'html.parser'))

    # about: the Google-reviews counter replaced a percentage
    for c in soup.select('.trx-addons-counter-535ddbb'):   # 8 services: exact, no '+'
        for t in c.find_all(string=re.compile(r'^\s*\+\s*$')): t.replace_with('')
    for c in soup.select('.trx-addons-counter-d29f5e8'):
        for t in c.find_all(string=re.compile(r'^\s*%\s*$')): t.replace_with('')

    # --- navigation: Home / About / Services (mega) / Contact, no demo or blog menus
    for menu in soup.select('ul.trx-addons-nav-menu, ul.trx-addons-mobile-menu, ul.sc_layouts_menu_nav, ul.menu, ul[id^=menu-]'):
        for li in menu.find_all('li', recursive=False):
            a = li.find('a')
            if not a: continue
            label = norm(a.get_text())
            if label in ('Blog',):
                li.decompose(); continue
            target = {'Home': 'index.html', 'About': 'about.html', 'Services': 'services.html', 'Contact': 'contact.html'}.get(label)
            if target:
                a['href'] = target
                if label in ('Home', 'About'):
                    for sub in li.find_all(['ul', 'div'], recursive=False):
                        if sub.get('class') and any('sub' in c or 'mega' in c for c in sub['class']): sub.decompose()
                    for sub in li.select('ul.sub-menu, ul.trx-addons-submenu, .trx-addons-mega-content-container, .sc_layouts_submenu_wrap'):
                        sub.decompose()
                    cls = [c for c in li.get('class', []) if 'has-children' not in c and 'mega' not in c]
                    a['class'] = [c for c in a.get('class', []) if c != 'trx-addons-menu-link-parent']
                    li['class'] = cls
    # services mega items -> services page
    for a in soup.select('a'):
        t = norm(a.get_text())
        href = a.get('href', '')
        if t in ('Hair Patch Fixing', 'Glue Bond System', 'Tape Bond System', 'Clip-On System', 'Hair Toppers', 'Maintenance',
                 'Learn More', 'Learn more', 'Read More', 'Hair system maintenance', 'Hair patch cleaning & refitting', 'Custom hair system design', 'Hair patch fixing'):
            a['href'] = 'services.html'
        elif t in ('Book Free Consultation', 'Book your free consultation today!', 'Book your free consultation!', 'Get in Touch') or href.startswith('tel:'):
            a['href'] = TEL
        elif re.search(r'Plashet', t):
            a['href'] = MAPS; a['target'] = '_blank'; a['rel'] = 'noopener'
        elif href in ('#', '') and t in ('Home',): a['href'] = 'index.html'
        elif href in ('#', '') and t == 'The Hair Patch Studio': a['href'] = 'index.html'
        elif href in ('#', '') and t in ('Aftercare', 'Design', 'Fitting', 'Hair systems'): a['href'] = 'services.html'
    # remaining '#' links: map to a real page, or drop list items for demo pages HPS doesn't have
    LINKMAP = {'About Us': 'about.html', 'About': 'about.html', 'Our Team': 'about.html', 'FAQs': 'about.html',
               'Testimonials': 'index.html', 'Before & After': 'index.html', 'Services': 'services.html',
               'Hair systems': 'services.html', 'Contact': 'contact.html', 'Home': 'index.html'}
    for a in soup.find_all('a'):
        if a.get('href', '#') not in ('#', ''): continue
        t = norm(a.get_text())
        if t in LINKMAP:
            a['href'] = LINKMAP[t]
        elif t:
            li = a.find_parent('li', class_=re.compile('elementor-icon-list-item|menu-item'))
            if li and not li.find(class_=re.compile('mega|submenu')): li.decompose()
    for a in soup.select('a[href*="themerex"]'):
        a['href'] = 'index.html'; a.attrs.pop('target', None)
    # social icons: HPS is on Instagram (+ WhatsApp); drop the demo's other networks
    for a in soup.select('a[href*="instagram.com"]'):
        a['href'] = 'https://www.instagram.com/hairpatchlondon/'; a['target'] = '_blank'; a['rel'] = 'noopener'
    for a in soup.select('a[href*="facebook.com"], a[href*="twitter.com"], a[href*="//x.com"], a[href*="youtube.com"], a[href*="linkedin.com"], a[href*="dribbble"], a[href*="behance"], a[href*="pinterest"]'):
        if a.decomposed: continue
        li = a.find_parent('li')
        (li if li and len(li.find_all('a')) == 1 else a).decompose()

    # --- meta
    if soup.title: soup.title.string = norm(TEXT.get(norm(soup.title.get_text()), soup.title.get_text()))
    for m in soup.find_all('meta', attrs={'name': 'description'}) + soup.find_all('meta', attrs={'property': 'og:description'}):
        m['content'] = 'The Hair Patch Studio — specialist non-surgical hair replacement in London: hair patch fixing, custom hair systems, glue & tape bonding, toppers and maintenance. Call ' + PHONE + '.'
    for m in soup.find_all('meta', attrs={'property': re.compile('og:(site_name|title|url)')}):
        p = m['property']
        m['content'] = {'og:site_name': 'The Hair Patch Studio', 'og:url': 'https://www.thehairpatchstudio.com/'}.get(p, soup.title.string if soup.title else 'The Hair Patch Studio')
    for l in soup.find_all('link', rel=lambda r: r and 'canonical' in r):
        l['href'] = 'https://www.thehairpatchstudio.com/'

    head = soup.head
    head.append(BeautifulSoup('<link rel="stylesheet" href="assets/hps/fonts/fonts.css"><link rel="stylesheet" href="assets/hps-brand.css">', 'html.parser'))
    soup.body.append(BeautifulSoup('<script src="assets/hps-site.js" defer></script>', 'html.parser'))
    out = str(soup)
    # config urls pointing at the demo server
    for pre in ('https://regrow.themerex.net', 'https:\\/\\/regrow.themerex.net', 'https:\\\\/\\\\/regrow.themerex.net'):
        out = out.replace(pre, '.')
    out = re.sub(r'(src|href)="/cdn-cgi[^"]*"', r'\1=""', out)
    open(os.path.join(SITE, name), 'w', encoding='utf-8').write(out)
    print('built', name)

# CSS assets: restore from backup, then recolour + refont
os.makedirs(os.path.join(OA, 'css'), exist_ok=True)
for f in os.listdir(ASSETS):
    if not f.endswith('.css') or f == 'hps-brand.css': continue
    p = os.path.join(ASSETS, f); b = os.path.join(OA, 'css', f)
    if not os.path.exists(b): shutil.copy2(p, b)
    css = open(b, encoding='utf-8', errors='replace').read()
    for a, c in COLOR_SUBS: css = re.sub(a, c, css)
    open(p, 'w', encoding='utf-8').write(css)

for f in sorted(os.listdir(PR)):
    if f.endswith('.html'): process(f)
