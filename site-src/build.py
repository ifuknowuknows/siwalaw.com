"""Builds the 8 language pages plus /privacy and /terms from en.json, the translation files and template.html."""
import json, re, os, sys, datetime, html as H
HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
tpl = open('template.html').read()
en = json.load(open('en.json'))
LANGS = [('en', 'English'), ('da', 'Dansk'), ('es', 'Español'), ('pt', 'Português'), ('sv', 'Svenska'),
         ('fr', 'Français'), ('id', 'Bahasa Indonesia'), ('ar', 'العربية')]
# list name -> (key field, translatable fields)
LISTS = {'services': ('name', ['name', 'text', 'points']), 'reasons': ('name', ['name', 'text']),
         'career': ('role', ['role']), 'education': ('role', ['role'])}
SITE = 'https://www.siwalaw.com'
FONT = 'https://cdn.jsdelivr.net/npm/@fontsource/geist-sans@5.2.5/files/geist-sans-%s-%d-normal.woff2'
def fonts():
    css = ''
    for w in (400, 500, 600, 700):
        css += "@font-face{font-family:'Geist';font-weight:%d;font-display:swap;src:url(%s) format('woff2')}\n" % (w, FONT % ('latin', w))
    return css
def esc(s): return H.escape(s or '', quote=False)
def url(code): return '/' if code == 'en' else '/' + code

def items(code, t, name):
    key, fields = LISTS[name]
    tr = (t.get('lists') or {}).get(name, {}) if code != 'en' else {}
    out = []
    for it in en.get(name, []):
        k = (it.get(key) or '').strip()
        if not k:
            continue
        loc = dict(it); loc.update({f: v for f, v in tr.get(k, {}).items() if v})
        out.append(loc)
    return out

def render_lists(code, t):
    r = {}
    svcs = items(code, t, 'services')
    tabs, panels = [], []
    for i, s in enumerate(svcs):
        pts = ''.join('<li>%s</li>' % esc(p.strip()) for p in (s.get('points') or '').split('\n') if p.strip())
        tabs.append('<button class="svc-tab" role="tab" type="button" id="svt%d" aria-controls="svp%d" aria-selected="%s" tabindex="%d">'
                    '<span class="num">%02d</span><span class="t2">%s</span></button>' % (i, i, 'true' if i == 0 else 'false', 0 if i == 0 else -1, i + 1, esc(s.get('name'))))
        panels.append('<div class="svc-panel" role="tabpanel" id="svp%d" aria-labelledby="svt%d"%s><h3 class="h5">%s</h3><p class="b7">%s</p><ul class="b3">%s</ul></div>'
                      % (i, i, '' if i == 0 else ' data-off', esc(s.get('name')), esc(s.get('text')), pts))
    r['SERVICES'] = '<div class="svc-list" role="tablist" aria-label="%s">%s</div>\n<div class="svc-panels">%s</div>' % (esc(t['services_label']), ''.join(tabs), ''.join(panels))
    r['REASONS'] = '\n'.join('<article class="reveal"><div><span class="n num">%02d</span><h3 class="h5">%s</h3></div><p class="b7">%s</p></article>'
                             % (i, esc(x.get('name')), esc(x.get('text'))) for i, x in enumerate(items(code, t, 'reasons'), 1))
    import urllib.parse
    r['CALL_SUBJ'] = urllib.parse.quote(t.get('call_subject') or en.get('call_subject', ''))
    for name, ph in (('career', 'CAREER'), ('education', 'EDUCATION')):
        r[ph] = ''.join('<li><span>%s</span><span>%s</span></li>' % (esc(x.get('years')), esc(x.get('role'))) for x in items(code, t, name))
    addr = (t.get('address') or en.get('address') or '').strip()
    r['ADDR1'] = esc(addr.replace('\n', ', '))
    r['ADDRESS'] = ('<div class="way"><span class="mono">%s</span><span class="v t2">%s</span></div>' % (esc(t['address_label']), esc(addr).replace('\n', '<br>'))) if addr else ''
    digits = re.sub(r'\D', '', en['phone'])
    r['PHONE_TEL'] = '+' + digits
    r['PHONE_WA'] = digits
    r['YEAR'] = str(datetime.date.today().year)
    r['__LANG__'] = json.dumps(json.load(open('lang_countries.json')))
    r['__DEAL__'] = json.dumps([c for c in en.get('deal_countries', []) if isinstance(c, str) and c.strip()])
    return r

def switcher(code, page=''):
    opts = ''.join('<a href="%s" lang="%s" data-l="%s"%s>%s</a>' % (url(l), l, l, ' aria-current="true"' if l == code else '', n) for l, n in LANGS)
    return ('<details class="lang"><summary aria-label="Language">%s</summary><div class="menu">%s</div></details>' % (code.upper() if code != 'ar' else 'ع', opts))

LANG_CSS = ('.lang{position:relative}.lang summary{list-style:none;cursor:pointer;font-size:14px;line-height:20px;font-weight:500;color:var(--soft);'
            'border:1px solid var(--line);border-radius:9999px;padding:4px 12px;user-select:none;transition:color .3s var(--ease)}.lang summary::-webkit-details-marker{display:none}'
            '.lang summary:hover{color:var(--ink)}.lang .menu{position:absolute;right:0;top:calc(100% + 12px);background:var(--bg);border:1px solid var(--line);'
            'border-radius:16px;padding:8px;display:flex;flex-direction:column;min-width:192px;z-index:40}'
            '.lang .menu a{padding:8px 12px;border-radius:8px;text-decoration:none;font-size:14px;line-height:20px;color:var(--ink);transition:background-color .3s var(--ease)}'
            '.lang .menu a:hover,.lang .menu a[aria-current]{background:var(--stone)}')
RTL_CSS = ('[dir=rtl] *{letter-spacing:0!important}[dir=rtl] body{font-family:"Noto Sans Arabic","Geeza Pro","Segoe UI",Tahoma,sans-serif}'
           '[dir=rtl] .lang .menu{right:auto;left:0}[dir=rtl] .arr{transform:scaleX(-1)}[dir=rtl] .tlink:hover .arr{transform:scaleX(-1) translateX(4px)}'
           '[dir=rtl] .seal{right:auto;left:max(24px,env(safe-area-inset-left,0px))}[dir=rtl] .facts dl>div{border-left:0;border-right:1px solid var(--cream-line);padding-left:0;padding-right:16px}'
           '[dir=rtl] .svc li{padding-left:0;padding-right:24px}[dir=rtl] .svc li::before{left:auto;right:0}[dir=rtl] .way .v{direction:ltr;text-align:right}'
           '[dir=rtl] .oasis svg{right:auto;left:-20px}')

def load(code):
    t = dict(en)
    if code != 'en':
        t.update(json.load(open(code + '.json')))
        for k in json.load(open('dnt.json')):
            if k in en:
                t[k] = en[k]
    return t

def build(code):
    t = load(code)
    html = tpl.replace('/*FONTS*/', fonts())
    for k, v in render_lists(code, t).items():
        html = html.replace('{{%s}}' % k, v) if not k.startswith('__') else html.replace(k, v)
    for k, v in t.items():
        if isinstance(v, str):
            html = html.replace('{{%s}}' % k, esc(v))
    left = re.findall(r'\{\{(\w+)\}\}', html)
    assert not left, (code, left)
    html = html.replace('<html lang="en">', '<html lang="%s"%s>' % (code, ' dir="rtl"' if code == 'ar' else ''), 1)
    alts = ''.join('<link rel="alternate" hreflang="%s" href="%s%s">' % (l, SITE, url(l)) for l, _ in LANGS)
    alts += '<link rel="alternate" hreflang="x-default" href="%s/"><link rel="canonical" href="%s%s">' % (SITE, SITE, url(code))
    html = html.replace('<title>', alts + '<title>', 1)
    html = html.replace('<nav', '<div class="right"><nav', 1).replace('</nav>', '</nav>' + switcher(code) + '</div>', 1)
    remember = ('<script>document.querySelectorAll(".lang a").forEach(function(a){a.addEventListener("click",function(){try{localStorage.setItem("lang",a.dataset.l)}catch(e){}})});'
                'document.addEventListener("click",function(e){var d=document.querySelector(".lang");if(d&&d.open&&!d.contains(e.target))d.open=false});</script>')
    if code == 'en':  # first visit: follow the browser language
        redirect = ('<script>(function(){try{if(localStorage.getItem("lang"))return}catch(e){}'
                    'var L=["da","es","pt","sv","fr","id","ar"],n=(navigator.languages||[navigator.language||""]);'
                    'for(var i=0;i<n.length;i++){var c=(n[i]||"").slice(0,2).toLowerCase();if(c==="en")return;if(c==="nb"||c==="no")c="da";if(L.indexOf(c)>-1){location.replace("/"+c+location.hash);return}}})();</script>')
        html = html.replace('<title>', redirect + '<title>', 1)
    html = html.replace('</body>', remember + '</body>', 1)
    css = LANG_CSS + (RTL_CSS if code == 'ar' else '')
    html = html.replace('</style>', css + '\n</style>', 1)
    return html

# ---- privacy and terms (English, Markdown in privacy.md / terms.md) ----
def md(text):
    if re.search(r'<(p|h[1-6]|ul|ol)\b', text):
        return text  # already HTML (saved by the editor)
    out, ul = [], False
    for line in text.strip().split('\n'):
        s = line.strip()
        if s.startswith('- ') or s.startswith('* '):
            if not ul: out.append('<ul>'); ul = True
            out.append('<li>%s</li>' % inline(s[2:])); continue
        if ul: out.append('</ul>'); ul = False
        if not s: continue
        if s.startswith('## '): out.append('<h2 class="h5">%s</h2>' % inline(s[3:]))
        elif s.startswith('# '): out.append('<h1 class="d2">%s</h1>' % inline(s[2:]))
        else: out.append('<p>%s</p>' % inline(s))
    if ul: out.append('</ul>')
    return '\n'.join(out)
def inline(s):
    s = esc(s)
    s = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', s)
    return re.sub(r'\[(.+?)\]\((https?://[^)\s]+|mailto:[^)\s]+|/[^)\s]*)\)', r'<a href="\2">\1</a>', s)

def front(text):
    m = re.match(r'^---\n(.*?)\n---\n?(.*)$', text, re.S)
    meta = {}
    if m:
        for l in m.group(1).split('\n'):
            if ':' in l:
                k, v = l.split(':', 1); meta[k.strip()] = v.strip().strip('"')
        text = m.group(2)
    return meta, text

def legal(name):
    meta, body = front(open(name + '.md').read())
    t = en
    head = tpl.split('<body')[0].replace('/*FONTS*/', fonts())
    head = re.sub(r'<title>.*?</title>', '<title>%s · siwa law</title>' % esc(meta.get('title', name.title())), head)
    head = head.replace('{{meta_desc}}', esc(meta.get('title', ''))).replace('{{title}}', esc(meta.get('title', '')))
    css = ('.doc{max-width:760px;margin:0 auto;padding:var(--s900) max(var(--s300),env(safe-area-inset-right,0px)) var(--s900) max(var(--s300),env(safe-area-inset-left,0px))}'
           '.doc h1{margin-bottom:var(--s200)}.doc h2{margin:var(--s500) 0 var(--s100)}.doc p,.doc li{color:var(--soft);font-size:17px;line-height:28px}.doc p+p{margin-top:var(--s200)}'
           '.doc ul{margin:var(--s100) 0;display:flex;flex-direction:column;gap:var(--s50)}.doc li{padding-left:var(--s300);position:relative}.doc li::before{content:"";position:absolute;left:0;top:14px;width:12px;height:1px;background:var(--ink)}'
           '.doc a{color:var(--link)}.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:var(--s700)}.upd{color:var(--soft);margin-bottom:var(--s400)}')
    head = head.replace('</style>', css + '</style>')
    upd = meta.get('updated', '')
    body_html = ('<body><main class="doc"><div class="top"><a class="mark" href="/">siwa law</a><a class="tlink btn-t" href="/">%s</a></div>%s%s'
                 '<p class="b6" style="margin-top:var(--s700);color:var(--soft)">%s · %s</p></main></body></html>') % (
        'Home', md(body).replace('</h1>', '</h1>' + (('<p class="upd mono">Updated %s</p>' % esc(upd)) if upd else ''), 1), '', esc(t['legal_name']), esc(t['cvr']))
    return head + body_html

out = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
os.makedirs(out, exist_ok=True)
for code, _ in LANGS:
    if code != 'en' and not os.path.exists(code + '.json'):
        print('missing', code); continue
    fname = 'index.html' if code == 'en' else code + '.html'
    open(os.path.join(out, fname), 'w').write(build(code))
    print('built', fname)
for name in ('privacy', 'terms'):
    if os.path.exists(name + '.md'):
        open(os.path.join(out, name + '.html'), 'w').write(legal(name)); print('built', name + '.html')
