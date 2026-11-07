#!/bin/sh
# run from the repo root after unzipping HyperAudio_seo.zip
cat >> site/assets/css/nav.css <<'CSS'
.pg-about{margin-top:calc(var(--u,8px) * 5);padding-top:calc(var(--u,8px) * 3);border-top:1px solid var(--bd)}
.pg-about h2{font-size:15px;margin:0 0 8px}
.pg-about .note{max-width:62ch;margin:0}
CSS
python3 build/docs_site.py && python3 build/seo.py && python3 tests/check.py
