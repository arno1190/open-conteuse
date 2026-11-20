#!/usr/bin/env python3
"""Check the deployable static showcase and its bilingual content contract."""
import json
import re
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent

class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.references=[]; self.keys=set(); self.forbidden=[]
    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag in {'form','iframe'}: self.forbidden.append(tag)
        for key in ('src','href'):
            value=attrs.get(key,'')
            if value and not value.startswith(('https:','http:','#','?','mailto:')): self.references.append(value)
        for key in ('data-i18n','data-i18n-alt','data-i18n-aria'):
            if key in attrs:self.keys.add(attrs[key])

page=Page();page.feed((ROOT/'index.html').read_text())
assert not page.forbidden, page.forbidden
generated={f'assets/{v}-current-cad.png':ROOT.parent/f'docs/design/images/{v}-hero-front.png' for v in ('mini','explore')}
for reference in page.references:
    assert generated.get(reference,ROOT/reference).is_file(), reference
script=(ROOT/'strings.js').read_text()
copy=json.loads(script[script.index('{'):script.rindex('}')+1])
for key in page.keys:
    assert key in copy['strings']['en'], f'Missing English key: {key}'
content=json.loads((ROOT/'content/index.json').read_text())
assert len(content['stories'])>=3
for story in content['stories']:
    assert (ROOT/story['art']).is_file(),story['art']
    for language in ('fr','en'):
        for field in ('title','subtitle','script','activity','preview_audio'):
            assert story[language][field],(story['id'],language,field)
assert content['script_approval']=='pending'
assert content['audio_approval']=='pending'
print(f'Showcase static checks passed: {len(page.references)} local references, {len(page.keys)} translated labels, {len(content["stories"])} bilingual stories.')

for story in content["stories"]:
    for lang in ("fr","en"):
        assert (ROOT/story[lang]["preview_audio"]).is_file()
