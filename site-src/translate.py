"""English decides. Re-translates only the English texts that changed since the last run.

Runs in the GitHub Action before build.py. Needs the repository secret DEEPL_API_KEY
(DeepL API Free or Pro). Without it, nothing is translated and the old translations stay.

- Keys listed in dnt.json are copied from English unchanged (names, numbers, contact details).
- Brand names inside a text stay in English (PROTECT below).
- A translation is replaced only when its English text changed, so hand fixes survive
  until you change that English line.
- Services, reasons, career and education items are matched by their English name/role;
  a new item is translated, a removed one is dropped.
"""
import hashlib, json, os, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
os.chdir(HERE)
KEY = os.environ.get('DEEPL_API_KEY', '').strip()
LANGS = {'da': 'DA', 'es': 'ES', 'pt': 'PT-BR', 'sv': 'SV', 'fr': 'FR', 'id': 'ID', 'ar': 'AR'}
LISTS = {'services': ('name', ['name', 'text', 'points']), 'reasons': ('name', ['name', 'text']),
         'career': ('role', ['role']), 'education': ('role', ['role'])}
PROTECT = ['Siwa Law Advokatanpartsselskab', 'siwa law', 'Mousta M. Moustafa', 'Mousta', 'Advokatsamfundet',
           'Dahlberg Assurance Agentur', 'Gorrissen Federspiel', 'Cuatrecasas', 'People Ventures', 'Next11',
           'Designit', 'WhatsApp', 'Esade', 'LSE']
STATE = 'translation-state.json'

def h(s): return hashlib.sha1(s.encode('utf-8')).hexdigest()[:12]
def protect(s):
    for p in sorted(PROTECT, key=len, reverse=True):
        s = s.replace(p, '<x translate="no">%s</x>' % p)
    return s.replace('\n', '<br/>')
def unprotect(s):
    import re
    s = re.sub(r'<x translate="no">(.*?)</x>', r'\1', s)
    return re.sub(r'\s*<br\s*/?>\s*', '\n', s)

def deepl(texts, target):
    url = 'https://api-free.deepl.com/v2/translate' if KEY.endswith(':fx') else 'https://api.deepl.com/v2/translate'
    out = []
    for i in range(0, len(texts), 40):
        data = [('target_lang', target), ('source_lang', 'EN'), ('tag_handling', 'html'), ('preserve_formatting', '1')]
        data += [('text', protect(t)) for t in texts[i:i + 40]]
        req = urllib.request.Request(url, data=urllib.parse.urlencode(data).encode(),
                                     headers={'Authorization': 'DeepL-Auth-Key ' + KEY})
        out += [unprotect(x['text']) for x in json.load(urllib.request.urlopen(req, timeout=60))['translations']]
    return out

def main():
    en = json.load(open('en.json'))
    dnt = set(json.load(open('dnt.json')))
    state = json.load(open(STATE)) if os.path.exists(STATE) else {}
    if not KEY:
        print('DEEPL_API_KEY not set: translations left as they are.')
        return
    for code, target in LANGS.items():
        path = code + '.json'
        tr = json.load(open(path))
        st = state.setdefault(code, {})
        todo = []  # (path tuple, english)
        for k, v in en.items():
            if not isinstance(v, str):
                continue
            if k in dnt or not v.strip():
                tr[k] = v; continue
            if k in tr and (st.get(k) == h(v) or k not in st):
                st[k] = h(v); continue  # unchanged, or first run: trust the reviewed text
            todo.append((('key', k), v))
        lists = tr.setdefault('lists', {})
        for name, (key, fields) in LISTS.items():
            cur = lists.setdefault(name, {})
            names = []
            for it in en.get(name, []):
                n = (it.get(key) or '').strip()
                if not n:
                    continue
                names.append(n)
                item = cur.setdefault(n, {})
                for f in fields:
                    src = it.get(f) or ''
                    sk = '%s/%s/%s' % (name, n, f)
                    if not src.strip():
                        item.pop(f, None); continue
                    if f in item and (st.get(sk) == h(src) or sk not in st):
                        st[sk] = h(src); continue
                    todo.append((('list', name, n, f), src))
            for n in list(cur):
                if n not in names:
                    del cur[n]
        if todo:
            for (where, src), out in zip(todo, deepl([e for _, e in todo], target)):
                if where[0] == 'key':
                    tr[where[1]] = out; st[where[1]] = h(src)
                else:
                    _, name, n, f = where
                    lists[name][n][f] = out; st['%s/%s/%s' % (name, n, f)] = h(src)
            print('%s: %d texts translated' % (code, len(todo)))
        json.dump(tr, open(path, 'w'), ensure_ascii=False, indent=1)
    json.dump(state, open(STATE, 'w'), ensure_ascii=False, indent=1)
    print('done')

if __name__ == '__main__':
    main()
