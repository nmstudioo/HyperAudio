"""Single source for repository and site URLs (edit site.config.json, then run tools/ship.py)."""
import json, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
C = json.load(open(f'{ROOT}/site.config.json'))
SITE = C['site_url']; REPO = 'https://github.com/' + C['repo']; BRANCH = C['branch']; OWNER_SITE = C['owner_site']
