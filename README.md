# siwalaw.com

Edit texts, services, career and photo at https://app.pagescms.org (sign in with GitHub, open this repository).
English decides: saving runs the "Build site" action, which translates changed English lines into the other 7 languages (DeepL, needs the DEEPL_API_KEY repository secret) and rebuilds the pages. Privacy and Terms are English only.

- site-src/en.json: English texts and lists
- site-src/da|es|pt|sv|fr|id|ar.json: translations (hand fixes stay until the English line changes)
- site-src/dnt.json: values copied from English to every language (names, numbers, contact details)
- site-src/privacy.md, terms.md: legal pages
- site-src/template.html: design; build.py and translate.py: the build
