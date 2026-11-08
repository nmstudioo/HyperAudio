#!/bin/sh
# Fetch the self-hosted fonts (latin subset, Fontsource via jsDelivr) into site/assets/fonts/.
# Plus Jakarta Sans 400, 600, 800 and JetBrains Mono 400, 700. Safe to rerun.
set -eu
cd "$(dirname "$0")/.."
D=site/assets/fonts
B=https://cdn.jsdelivr.net/fontsource/fonts
mkdir -p "$D"
for spec in plus-jakarta-sans:400 plus-jakarta-sans:600 plus-jakarta-sans:800 jetbrains-mono:400 jetbrains-mono:700; do
  fam=${spec%%:*}; w=${spec##*:}
  out="$D/$fam-latin-$w-normal.woff2"
  if [ -s "$out" ] && [ "$(head -c4 "$out")" = "wOF2" ] && [ "$(wc -c <"$out")" -gt 4000 ]; then echo "have $out"; continue; fi
  echo "get  $out"
  curl -fsSL --retry 3 -o "$out.tmp" "$B/$fam@latest/latin-$w-normal.woff2"
  [ "$(head -c4 "$out.tmp")" = "wOF2" ] && [ "$(wc -c <"$out.tmp")" -gt 4000 ] || { rm -f "$out.tmp"; echo "bad download: $out" >&2; exit 1; }
  mv "$out.tmp" "$out"
done
echo "fonts ok"
