"""Builds the artifact page and the standalone site page from body.html."""
import os, sys
D = os.path.dirname(os.path.abspath(__file__))
os.chdir(D)

old = open('agora-athinon.html', encoding='utf-8').read()
head = old[:old.index('</style>') + len('</style>')]   # title, meta, fonts, base CSS
body = open('body.html', encoding='utf-8').read()
q = [l.rstrip('\n') for l in open('quotes.csv', encoding='utf-8') if l.strip()]
body = body.replace('__QUOTES__', '\n'.join(q))

# 1. claude.ai artifact: no external fetch (blocked there anyway)
art = head + body.replace('var DATA_URL = "__DATA_URL__";', 'var DATA_URL = "";')
open('agora-athinon.html', 'w', encoding='utf-8').write(art)

# 2. standalone site page
data_url = sys.argv[1] if len(sys.argv) > 1 else 'data.json'
frag = (head + body).replace('var DATA_URL = "__DATA_URL__";', 'var DATA_URL = "%s";' % data_url)
FB = {"apiKey": "AIzaSyDd3-HyjHU6Cji1DwPtZ6epuJxFUT6luws", "authDomain": "agora-athinon.firebaseapp.com", "projectId": "agora-athinon", "storageBucket": "agora-athinon.firebasestorage.app", "messagingSenderId": "178881580605", "appId": "1:178881580605:web:81019bf8af752c0b456454"}
import json as _json
assert frag.count('var FIREBASE_CONFIG = null;') == 1
frag = frag.replace('var FIREBASE_CONFIG = null;', 'var FIREBASE_CONFIG = ' + _json.dumps(FB) + ';')
frag = frag.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '')
page = ('<!doctype html>\n<html lang="el">\n<head>\n<meta charset="utf-8">\n'
        '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">\n'
        '<meta name="description" content="Axiogram: ελληνικές και αμερικανικές μετοχές, crypto και το χαρτοφυλάκιό σου σε ένα σημείο, με τιμές, διαγράμματα, μερίσματα και heatmap.">\n'
        '<link rel="manifest" href="manifest.webmanifest">\n'
        '<meta name="theme-color" content="#2a3040">\n'
        '<link rel="icon" type="image/png" sizes="32x32" href="icons/favicon-32.png">\n'
        '<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">\n'
        '<meta name="apple-mobile-web-app-capable" content="yes">\n'
        '<meta name="mobile-web-app-capable" content="yes">\n'
        '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">\n'
        '<meta name="apple-mobile-web-app-title" content="Axiogram">\n'
        '<style>:root{color-scheme:dark;padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}'
        'body{margin:0;font:14px system-ui,sans-serif}img{max-width:100%}[hidden]{display:none!important}</style>\n'
        '</head>\n<body>\n' + frag + '\n</body>\n</html>\n')
os.makedirs('repo', exist_ok=True)
open('repo/index.html', 'w', encoding='utf-8').write(page)
print('built', len(q), 'embedded rows; DATA_URL =', data_url)
