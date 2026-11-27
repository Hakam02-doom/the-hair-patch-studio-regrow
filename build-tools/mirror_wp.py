"""Mirror Regrow (WordPress/Elementor) pages into a static local site.
usage: python3 -I mirror_wp.py OUT_DIR"""
import os, re, sys, hashlib, urllib.request, urllib.parse, concurrent.futures as cf, html as H

OUT = sys.argv[1]
ASSETS = os.path.join(OUT, 'assets')
os.makedirs(ASSETS, exist_ok=True)
UA = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Chrome/126 Safari/537.36'}
BASE = 'https://regrow.themerex.net'
PAGES = {'/hair-removal/': 'index.html', '/about-us/': 'about.html', '/services/': 'services.html', '/contact-us/': 'contact.html'}
HOSTS = r'(?:regrow\.themerex\.net|fonts\.googleapis\.com|fonts\.gstatic\.com|cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net|unpkg\.com)'
ASSET_RE = re.compile(r'''((?:https?:)?(?:\\?/){2}''' + HOSTS + r'''(?:\\?/)[^"'\s)<>,]+)''')
done = {}

def local_name(full):
    u = urllib.parse.urlsplit(full)
    base = os.path.basename(u.path) or 'file'
    stem, ext = os.path.splitext(base)
    if 'fonts.googleapis.com' in u.netloc:
        ext = '.css'; stem = 'gfonts'
    h = hashlib.md5((u.path + '?' + (u.query if 'googleapis' in u.netloc else '')).encode()).hexdigest()[:6]
    return f'{stem[:60]}-{h}{ext}'

def fetch(url):
    full = H.unescape(url.replace('\\/', '/'))
    if full.startswith('//'): full = 'https:' + full
    if full in done: return done[full]
    name = local_name(full)
    dest = os.path.join(ASSETS, name)
    if not os.path.exists(dest):
        try:
            data = urllib.request.urlopen(urllib.request.Request(full, headers=UA), timeout=40).read()
        except Exception as e:
            print('FAIL', full, e); done[full] = None; return None
        if name.endswith('.css'):
            data = rewrite_css(data.decode('utf-8', 'replace'), full).encode()
        open(dest, 'wb').write(data)
    done[full] = name
    return name

def rewrite_css(css, base):
    def sub(m):
        raw = m.group(1).strip().strip('\'"')
        if raw.startswith(('data:', '#')): return m.group(0)
        n = fetch(urllib.parse.urljoin(base, raw))
        return f'url({n})' if n else m.group(0)
    css = re.sub(r'url\(([^)]+)\)', sub, css)
    css = re.sub(r'@import\s+["\']([^"\']+)["\']', lambda m: f'@import "{fetch(urllib.parse.urljoin(base, m.group(1))) or m.group(1)}"', css)
    return css

DROP = re.compile(r'googletagmanager|google-analytics|gtag\(|fbq\(|hotjar|wp-emoji|emoji-release|wpemojiSettings|cookie-law|ccw_|chaty|tidio|jivo|livechat', re.I)

def process(html):
    html = re.sub(r'<script\b[^>]*>.*?</script>', lambda m: '' if DROP.search(m.group(0)) else m.group(0), html, flags=re.S)
    html = re.sub(r'<link[^>]+rel=["\'](?:dns-prefetch|preconnect|pingback|EditURI|alternate|https://api.w.org/|shortlink)["\'][^>]*>', '', html)
    urls = set(ASSET_RE.findall(html))
    urls = {u for u in urls if not re.search(r'regrow\.themerex\.net(?:\\?/)(?!wp-content|wp-includes)', u.replace('\\/', '/')) or re.search(r'\.(css|js|png|jpe?g|webp|svg|gif|woff2?|ttf|mp4|webm|json)(\?|$)', u)}
    with cf.ThreadPoolExecutor(16) as ex:
        names = dict(zip(urls, ex.map(fetch, urls)))
    for u in sorted(urls, key=len, reverse=True):
        if names[u]:
            rep = 'assets/' + names[u]
            if '\\/' in u: rep = rep.replace('/', '\\/')
            html = html.replace(u, rep)
    # internal page links
    def link(m):
        p = urllib.parse.urlsplit(H.unescape(m.group(2))).path
        return m.group(1) + PAGES.get(p, PAGES.get(p.rstrip('/') + '/', '#')) + m.group(3)
    html = re.sub(r'(href=["\'])(https://regrow\.themerex\.net/[^"\'#]*)(["\'])', link, html)
    return html

for path, dst in PAGES.items():
    html = urllib.request.urlopen(urllib.request.Request(BASE + path, headers=UA), timeout=40).read().decode('utf-8')
    raw = os.path.join(OUT, '..', 'raw-' + dst)
    open(raw, 'w').write(html)
    out = process(html)
    open(os.path.join(OUT, dst), 'w', encoding='utf-8').write(out)
    print('wrote', dst, len(out), 'remaining remote:', len(re.findall(r'regrow\.themerex\.net', out)))
