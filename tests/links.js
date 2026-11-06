#!/usr/bin/env node
// Every local href/src must exist, none may be root-absolute (breaks under /HyperAudio/), 404.html must exist.
const fs = require("fs"),
  path = require("path");
const SITE = path.join(__dirname, "..", "site"),
  errs = [];
const walk = (d) =>
  fs
    .readdirSync(d, { withFileTypes: true })
    .flatMap((e) =>
      e.isDirectory()
        ? e.name === "downloads"
          ? []
          : walk(path.join(d, e.name))
        : [path.join(d, e.name)],
    );
for (const f of walk(SITE).filter((f) => f.endsWith(".html"))) {
  const rel = path.relative(SITE, f),
    html = fs.readFileSync(f, "utf8");
  if (rel === "404.html") continue; // served at any depth; its links are built by script from /HyperAudio/
  for (const m of html.matchAll(/\b(?:href|src)\s*=\s*["']([^"']+)["']/g)) {
    const u = m[1];
    if (/^(https?:|mailto:|tel:|data:|javascript:|#)/.test(u)) continue;
    if (u.startsWith("/")) {
      errs.push(`${rel}: root-absolute "${u}"`);
      continue;
    }
    const p = path.join(
      path.dirname(f),
      decodeURIComponent(u.split(/[?#]/)[0]),
    );
    const rp = path.resolve(p);
    if (rp !== SITE && !rp.startsWith(SITE + path.sep)) {
      errs.push(`${rel}: "${u}" points outside site/ (not published)`);
      continue;
    }
    if (
      !(
        fs.existsSync(p) &&
        (!fs.statSync(p).isDirectory() ||
          fs.existsSync(path.join(p, "index.html")))
      )
    )
      errs.push(`${rel}: missing target "${u}"`);
  }
}
if (!fs.existsSync(path.join(SITE, "404.html")))
  errs.push("site/404.html missing");
console.log(errs.length ? errs.map((e) => "FAIL " + e).join("\n") : "links ok");
process.exit(errs.length ? 1 : 0);
