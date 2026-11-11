#!/usr/bin/env python3
"""One command: python3 build/build.py [--out DIR] [--no-site]
Reads VERSION + src/, writes VDC/IRS/EEL, bundles, SHA256SUMS.txt, profiles.json,
acceptance.json, DIFF.md to releases/<ver>/ and publishes them to site/."""
import argparse, json, os, shutil, sys, zipfile
sys.path.insert(0, os.path.dirname(__file__)); from verify import sha, acceptance
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ap = argparse.ArgumentParser(); ap.add_argument('--out'); ap.add_argument('--no-site', action='store_true'); ap.add_argument('--publish', action='store_true'); ap.add_argument('--no-runtime', action='store_true'); ap.add_argument('--write-stats', action='store_true'); a = ap.parse_args()
if a.publish:
    # downloads are generated from releases/ and never committed; evidence in site/data/profiles.json comes from device-tests.json
    import glob
    dst = f'{ROOT}/site/downloads'; shutil.rmtree(dst, ignore_errors=True); vs = []
    for r in sorted(glob.glob(f'{ROOT}/releases/*/SHA256SUMS.txt')):
        v = os.path.basename(os.path.dirname(r)); vs.append(v)
        shutil.copytree(os.path.dirname(r), f'{dst}/{v}', ignore=shutil.ignore_patterns('profiles.json', 'DIFF.md', 'acceptance.json', 'FROZEN'))
    cv = open(f'{ROOT}/VERSION').read().strip(); pj = json.load(open(f'{ROOT}/releases/{cv}/profiles.json'))
    ev = {}
    for e in json.load(open(f'{ROOT}/docs/evidence/device-tests.json'))['entries']:
        if e['release'] == 'v' + cv and e['result'] in ('pass', 'fail'): ev[e['build']] = e
    for q in pj['profiles']:
        if q['id'] in ev: q['evidence'] = {'offline': True, 'device': 'reported', 'deviceNote': ev[q['id']]['notes']}
    open(f'{ROOT}/site/data/profiles.json', 'w').write(json.dumps(pj, separators=(',', ':')))
    print('published downloads for', ', '.join(vs)); sys.exit(0)
ver = open(f'{ROOT}/VERSION').read().strip()
meta = json.load(open(f'{ROOT}/src/profiles.meta.json'))
if a.write_stats:
    import derive_stats
    for q in meta['profiles']: q['stats'].update(derive_stats.derive(f'{ROOT}/src/profiles/{q["id"]}', q))
    open(f'{ROOT}/src/profiles.meta.json', 'w', encoding='utf-8').write(json.dumps(meta, separators=(',', ':'))); print('stats written to src/profiles.meta.json')
rel = a.out or f'{ROOT}/releases/{ver}'
if os.path.exists(f'{rel}/FROZEN') and not a.out: sys.exit(f'{ver} is FROZEN; bump VERSION or use --out')
shutil.rmtree(rel, ignore_errors=True); os.makedirs(rel)
date = meta['released']; ts = tuple(int(x) for x in date.split('-')) + (0, 0, 0)

def zipit(path, items):
    with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as z:
        for arc, data in sorted(items):
            zi = zipfile.ZipInfo(arc, ts); zi.compress_type = zipfile.ZIP_DEFLATED; zi.external_attr = 0o644 << 16; z.writestr(zi, data)
    return dict(name=os.path.basename(path), bytes=os.path.getsize(path), sha256=sha(path), path=f'downloads/{ver}/{os.path.basename(path)}')

sums, all_items, acc, profs = [], [], {}, []
for p in meta['profiles']:
    pid = p['id']; src = f'{ROOT}/src/profiles/{pid}'; dst = f'{rel}/{pid}'; os.makedirs(dst)
    files, items = [], []
    for n in p['file_order']:
        shutil.copy(f'{src}/{n}', f'{dst}/{n}'); h = sha(f'{dst}/{n}')
        files.append(dict(kind=n.rsplit('.', 1)[1], name=n, bytes=os.path.getsize(f'{dst}/{n}'), sha256=h, path=f'downloads/{ver}/{pid}/{n}'))
        sums.append(f'{h}  {ver}/{pid}/{n}'); items.append((n, open(f'{dst}/{n}', 'rb').read()))
    setup = open(f'{src}/SETUP.txt', encoding='utf-8').read().replace('{{VERSION}}', ver).encode()
    open(f'{dst}/SETUP.txt', 'wb').write(setup); sums.append(f'{sha(dst + "/SETUP.txt")}  {ver}/{pid}/SETUP.txt')
    bundle = zipit(f'{rel}/HyperAudio_{ver}_{pid}.zip', items + [('SETUP.txt', setup)])
    all_items += [(f'{pid}/{n}', d) for n, d in items]
    q = {k: v for k, v in p.items() if k != 'file_order'}; q['files'] = files; q['bundle'] = bundle; profs.append(q)
    acc[pid] = acceptance(dst, p, not a.no_runtime)
allz = zipit(f'{rel}/HyperAudio_{ver}_all.zip', all_items)
data = {k: meta[k] for k in ('released', 'status', 'freq')}; data = {'version': ver, **data, 'all': allz, 'profiles': profs}
sums.sort(key=lambda s: s.split('  ')[1])
open(f'{rel}/SHA256SUMS.txt', 'w').write('\n'.join(sums) + '\n')
json.dump(data, open(f'{rel}/profiles.json', 'w'), separators=(',', ':'))
OK_NOT_RUN = {'cpu'} | ({'eel.compile', 'limiter.ceiling', 'limiter.true_peak', 'tail', 'nan_soak'} if a.no_runtime else set())
bad = [(k, c) for k, v in acc.items() for c in v if c['status'] == 'fail' or (c['status'] == 'not_run' and c['check'] not in OK_NOT_RUN)]
json.dump(dict(version=ver, results=acc), open(f'{rel}/acceptance.json', 'w'), indent=1)

# diff vs previous release
prevs = sorted(d for d in os.listdir(f'{ROOT}/releases') if d != ver and os.path.exists(f'{ROOT}/releases/{d}/profiles.json'))
if prevs:
    pv = prevs[-1]; old = {p['id']: p for p in json.load(open(f'{ROOT}/releases/{pv}/profiles.json'))['profiles']}
    L = [f'# profiles.json diff {pv} -> {ver}', '']
    for p in profs:
        o = old.get(p['id'])
        if not o: L.append(f'- **{p["id"]}**: new profile'); continue
        ch = [f['name'] + ' changed' for f, g in zip(p['files'], o['files']) if f['sha256'] != g['sha256']]
        ch += [f'stats.{k}: {o["stats"].get(k)} -> {v}' for k, v in p['stats'].items() if o['stats'].get(k) != v]
        cv = max(abs(x - y) for x, y in zip(p['curves']['predicted'], o['curves']['predicted']))
        if cv > 0.05: ch.append(f'predicted curve max delta {cv:.2f} dB')
        L.append(f'- **{p["id"]}**: ' + ('; '.join(ch) if ch else 'unchanged'))
    L += [f'- removed: {k}' for k in old if k not in {p["id"] for p in profs}]
    open(f'{rel}/DIFF.md', 'w').write('\n'.join(L) + '\n')

print(f'built {ver}: {len(profs)} profiles, {len(sums)} files, {sum(len(v) for v in acc.values())} checks, {len(bad)} failed')
for k, c in bad: print('FAIL', k, c['check'], c['detail'])
sys.exit(1 if bad else 0)
