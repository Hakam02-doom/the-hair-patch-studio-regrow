"""Project 2: replace Regrow images in place with The Hair Patch Studio imagery (same filename + pixel size).
usage: venv/bin/python -I p2_assets.py SITE_ASSETS BACKUP_DIR FONTS_DIR"""
import os, re, sys, shutil
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps

A, BK, FD = sys.argv[1:4]
HPS = os.path.join(A, 'hps')
os.makedirs(BK, exist_ok=True)
ORANGE = (253, 152, 0); ORANGE_D = (233, 140, 0); NAVY = (15, 23, 42); SLATE = (69, 79, 94)
CREAM = (254, 249, 225); CREAM2 = (249, 240, 200); WHITE = (255, 255, 255)

STOCK = os.path.join(A, 'stock')   # high-res Unsplash photos (Unsplash License) for large generic slots

def src(name):
    if name.startswith('stock:'):
        im = Image.open(os.path.join(STOCK, name[6:] + '.jpg'))
        return im.convert('RGB')
    f = [x for x in os.listdir(HPS) if x.startswith(name)][0]
    im = Image.open(os.path.join(HPS, f))
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGBA', im.size, (*WHITE, 255)); bg.alpha_composite(im); im = bg
    return im.convert('RGB')

def half(name, side):
    im = src(name); w, h = im.size
    return im.crop((0, 0, w // 2, h)) if side == 'L' else im.crop((w - w // 2, 0, w, h))

def cover(im, size, fx=.5, fy=.5):
    w, h = size
    s = max(w / im.width, h / im.height)
    im = im.resize((max(w, round(im.width * s)), max(h, round(im.height * s))), Image.LANCZOS)
    if s > 1.15:  # source smaller than the slot: restore edge detail lost in upscaling
        im = im.filter(ImageFilter.UnsharpMask(radius=1.4 * min(s, 3), percent=70, threshold=2))
    x = int((im.width - w) * fx); y = int((im.height - h) * fy)
    return im.crop((x, y, x + w, y + h))

def font(name, size):
    return ImageFont.truetype(os.path.join(FD, name), size)

def hero_composite(im, size, place=.62, darken=.45):
    """Wide banner from a portrait photo: blurred fill + sharp photo, no extreme upscaling."""
    w, h = size
    bg = cover(im, size).filter(ImageFilter.GaussianBlur(40))
    bg = Image.blend(bg, Image.new('RGB', size, NAVY), darken)
    s = h / im.height
    fg = im.resize((round(im.width * s), h), Image.LANCZOS)
    x = int(w * place - fg.width / 2)
    mask = Image.new('L', fg.size, 255)
    fade = 80
    d = ImageDraw.Draw(mask)
    for i in range(fade):
        a = int(255 * i / fade)
        d.line([(i, 0), (i, h)], fill=a); d.line([(fg.width - 1 - i, 0), (fg.width - 1 - i, h)], fill=a)
    bg.paste(fg, (x, 0), mask)
    return bg

def initials(size, letter):
    im = Image.new('RGB', size, ORANGE); d = ImageDraw.Draw(im)
    d.text((size[0] / 2, size[1] / 2 + 1), letter, font=font('rubik-500.ttf', int(size[1] * .46)), fill=NAVY, anchor='mm')
    return im

def badge(size, text, sub=None):
    im = Image.new('RGBA', size, (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    d.text((size[0] / 2, size[1] / 2 - (8 if sub else 0)), text, font=font('rubik-500.ttf', 19), fill=NAVY, anchor='mm')
    if sub:
        d.text((size[0] / 2, size[1] / 2 + 16), sub, font=font('karla-500.ttf', 13), fill=SLATE, anchor='mm')
    return im

def faces_group(size):
    """'Happy clients' avatar cluster: two client 'after' photos + plus circle (Regrow layout 167x72)."""
    w, h = size; im = Image.new('RGBA', size, (0, 0, 0, 0)); d = 64
    for i, (nm, side, fx, fy) in enumerate([('Men8', 'R', .5, .25), ('Men7', 'R', .55, .3)]):
        face = cover(half(nm, side), (d * 2, d * 2), fx, fy).resize((d, d), Image.LANCZOS)
        m = Image.new('L', (d, d), 0); ImageDraw.Draw(m).ellipse((0, 0, d - 1, d - 1), fill=255)
        ring = Image.new('RGBA', (d + 6, d + 6), (0, 0, 0, 0)); ImageDraw.Draw(ring).ellipse((0, 0, d + 5, d + 5), fill=(*WHITE, 255))
        im.alpha_composite(ring, (i * 48, (h - d - 6) // 2)); im.paste(face, (i * 48 + 3, (h - d) // 2), m)
    cx = 2 * 48 + 3
    ImageDraw.Draw(im).ellipse((cx, (h - d) // 2, cx + d, (h + d) // 2), fill=(*WHITE, 255))
    ImageDraw.Draw(im).text((cx + d / 2, h / 2), '+', font=font('rubik-500.ttf', 34), fill=NAVY, anchor='mm')
    return im

# Regrow stem -> how to build the replacement
PHOTO = {
    'background-07-copyright': ('hero', 'g5062', .66),                      # home hero
    'background-06-copyright': ('shade', 'Men4', .5, .3),                   # mid-page CTA band (navy shade under the headline)
    'custom-img-10-copyright': ('cover', 'stock:tools', .5, .5),  # card: hair system maintenance
    'custom-img-07-copyright': ('cover', 'stock:sinks', .5, .55),          # card: cleaning & refitting
    'custom-img-09-copyright': ('cover', 'stock:hairline', .5, .3),           # card: hair patch fixing
    'custom-img-23-copyright': ('cover', 'stock:cutting', .6, .4),
    'custom-img-24-copyright': ('cover', 'Glue_Bond_Hair_System', .5, .4),   # card: glue bond
    'custom-img-20-copyright': ('cover', 'Tape_Bond_Hair_System', .5, .4),   # card: tape bond
    'custom-img-21-copyright': ('cover', 'Clip_On_Hair_System', .5, .4),     # card: clip-on
    'custom-img-22-copyright': ('cover', 'Custom_Hair_System_Design', .5, .4),  # card: consultation
    'custom-img-26-copyright': ('pair', 'Men1', 'L'),                        # before (fit, not zoomed)
    'custom-img-27-copyright': ('pair', 'Men1', 'R'),                        # after
    'custom-img-36-copyright': ('cover', 'stock:gloves', .5, .35),
    'custom-img-37-copyright': ('cover', 'stock:scissors', .5, .4),
    'custom-img-38-copyright': ('cover', 'stock:blowdry', .5, .3),
    'custom-img-39-copyright': ('cover', 'stock:hairline', .5, .3),           # team: technicians
    'custom-img-41-copyright': ('cover', 'stock:scissors', .5, .35),  # team: designers
    'custom-img-43-copyright': ('cover', 'stock:modernsalon', .5, .5),
    'custom-img-44-copyright': ('cover', 'Men2', .5, .25),
    'custom-img-01-copyright': ('cover', 'stock:roundbrick', .5, .5),  # beside a named review: no client face
    'banner-01-copyright': ('cover', 'Men5', .5, .3),
    'custom-img-16': ('cover', 'Men2', .5, .3), 'custom-img-17': ('cover', 'Men3', .5, .3), 'custom-img-18': ('cover', 'Men6', .5, .3),
}
AVATARS = {'testimonials-02-copyright': 'B', 'testimonials-01-copyright': 'P', 'testimonials-03-copyright': 'D', 'testimonials-04-copyright': 'J'}
BADGES = {'partner-01-copyright': ('Non-surgical', 'hair replacement'), 'partner-02-copyright': ('Custom-made', 'hair systems'),
          'partner-03-copyright': ('Natural finish', 'undetectable'), 'partner-04-copyright': ('Secure bonding', 'glue · tape · clip-on'),
          'partner-05-copyright': ('Free', 'consultation'), 'partner-06-copyright': ('★ 4.9 Google', '29 reviews')}

# Hair_System_Maintenance has no own photo on the HPS site: use the cleaning photo
ALIASES = {'Hair_System_Maintenance': 'Hair_Patch_Cleaning'}

def stem_of(f):
    return re.sub(r'(-\d+x\d+)?-[0-9a-f]{6}\.\w+$', '', f)

n = 0
for f in sorted(os.listdir(A)):
    p = os.path.join(A, f)
    if not os.path.isfile(p) or not re.search(r'\.(jpe?g|png|webp)$', f): continue
    st = stem_of(f)
    if st not in PHOTO and st not in AVATARS and st not in BADGES and st not in ('logo', 'logo-retina', 'secondary-logo', 'secondary-logo-retina', 'favicon-90x90', 'favicon-300x300', 'custom-img-25-copyright'):
        continue
    b = os.path.join(BK, f)
    if not os.path.exists(b): shutil.copy2(p, b)
    size = Image.open(b).size
    if st in PHOTO:
        spec = PHOTO[st]; kind = spec[0]
        name = ALIASES.get(spec[1], spec[1])
        if kind == 'hero': out = hero_composite(src(name), size, spec[2])
        elif kind == 'pair': out = hero_composite(half(name, spec[2]), size, .5, .12)
        elif kind == 'fit': out = hero_composite(src(name), size, .5, .12)
        elif kind == 'half': out = cover(half(name, spec[2]), size, spec[3], spec[4])
        elif kind == 'shade':
            out = cover(src(name), size, spec[2], spec[3]).convert('RGBA'); w_, h_ = size
            g = Image.new('L', (w_, 1))
            for x in range(w_): g.putpixel((x, 0), max(0, int(215 * (1 - x / (w_ * .62)))))
            ov = Image.new('RGBA', size, (*NAVY, 255)); ov.putalpha(g.resize(size)); out.alpha_composite(ov); out = out.convert('RGB')
        else: out = cover(src(name), size, spec[2], spec[3])
    elif st in AVATARS: out = initials(size, AVATARS[st])
    elif st in BADGES: out = badge(size, *BADGES[st])
    elif st == 'custom-img-25-copyright': out = faces_group(size)
    elif st.startswith('favicon'):
        logo = Image.open(os.path.join(HPS, 'HairPatchLogo-removebg-preview.png')).convert('RGBA')
        icon = logo.crop((150, 0, 470, 250))
        out = Image.new('RGB', size, CREAM); icon.thumbnail((int(size[0] * .9), int(size[1] * .9)), Image.LANCZOS)
        out.paste(icon, ((size[0] - icon.width) // 2, (size[1] - icon.height) // 2), icon)
    else:  # logos: full HPS logo; secondary (dark footer) gets light text
        logo = Image.open(os.path.join(HPS, 'HairPatchLogo-removebg-preview.png')).convert('RGBA')
        if st.startswith('secondary'):
            px = logo.load(); W, Hh = logo.size
            for y in range(int(Hh * .55), Hh):
                for x in range(W):
                    r, g, bb, a = px[x, y]
                    if a > 40 and r < 120 and g < 120 and bb < 140: px[x, y] = (255, 255, 255, a)
        scale = 2 if 'retina' in st else 1
        h = 64 * scale; w = round(logo.width * h / logo.height)
        out = logo.resize((w, h), Image.LANCZOS)
        out.save(p, 'PNG'); n += 1; continue
    if f.lower().endswith('.png'):
        (out if out.mode == 'RGBA' else out.convert('RGB')).save(p, 'PNG', optimize=True)
    else:
        out.convert('RGB').save(p, 'JPEG', quality=88, optimize=True, progressive=True)
    n += 1
print('replaced', n)

# SVG accents: Regrow coral -> HPS orange
for f in os.listdir(A):
    if f.endswith('.svg'):
        p = os.path.join(A, f); s = open(p, encoding='utf-8', errors='ignore').read()
        t = re.sub(r'(?i)#FF7B5F|#F86A4C|#FF7A5F', '#FD9800', s)
        if t != s: open(p, 'w', encoding='utf-8').write(t)
