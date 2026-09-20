#!/bin/sh
# Copyright 2026 ROBOTIS AI
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Jaehong Oh <jaehongoh1554@gmail.com>

# Regenerate assets/social-card.png — the GitHub social preview image.
#
#   ./assets/make_social_card.sh
#
# 1280x640, which is what GitHub's Settings -> Social preview expects, with
# every piece of text kept at least 40pt from the edge so nothing is cropped
# when the card is re-framed for a link unfurl.
#
# Drawn with ImageMagick primitives rather than rendered from SVG: this
# machine has no librsvg delegate, so ImageMagick would fall back to its
# internal renderer and the text would come out wrong.
#
# The numbers in the chips are facts about the repository. If they change,
# change them here -- a card that overstates the test count is the same class
# of error as a README that does.
#
# Output is byte-reproducible: PNG timestamp and text chunks are excluded, so
# re-running this without changing anything produces no diff and does not churn
# the repository.

set -eu

cd "$(dirname "$0")/.."
OUT="assets/social-card.png"

HN=/System/Library/Fonts/HelveticaNeue.ttc
MN=/System/Library/Fonts/Menlo.ttc

command -v magick >/dev/null 2>&1 || {
  echo "ImageMagick (magick) is required: brew install imagemagick" >&2
  exit 1
}
for f in "$HN" "$MN"; do
  [ -f "$f" ] || { echo "missing font: $f (this script assumes macOS)" >&2; exit 1; }
done

# Stat chips: label, accent colour. Laid out left to right from x=96.
CHIPS=$(python3 - <<'PY'
chips = [("68",  "SKILLS",      "#6E56CF"),
         ("7",   "HOOKS",       "#1A7F37"),
         ("156", "TESTS",       "#1A7F37"),
         ("5",   "LANG GUIDES", "#2F81F7"),
         ("GPG", "+ DCO",       "#D97757")]
x, y, h, gap, pad, cw = 96, 448, 52, 18, 26, 11.6
out = []
for num, label, color in chips:
    text = f"{num} {label}"
    w = int(len(text) * cw) + pad * 2 + 22
    out.append(f'-fill "#161B22" -stroke "#30363D" -strokewidth 1 '
               f'-draw "roundrectangle {x},{y} {x+w},{y+h} 10,10" '
               f'-stroke none -fill "{color}" '
               f'-draw "circle {x+pad+3},{y+h//2} {x+pad+3},{y+h//2-4}" '
               f'-fill "#C9D1D9" -gravity NorthWest '
               f'-annotate +{x+pad+18}+{y+16} "{text}"')
    x += w + gap
print(" ".join(out))
PY
)

eval magick -size 1280x640 xc:"'#0D1117'" \
  -fill "'#2F81F7'" -draw "'rectangle 0,0 430,6'" \
  -fill "'#D97757'" -draw "'rectangle 430,0 740,6'" \
  -fill "'#6E56CF'" -draw "'rectangle 740,0 940,6'" \
  -fill "'#21262D'" -draw "'rectangle 940,0 1280,6'" \
  -font "$MN" -pointsize 21 -fill "'#2F81F7'" \
    -gravity NorthWest -annotate +96+112 "'ROBOTIS AI   ·   TEAM HARNESS'" \
  -font "$HN" -pointsize 86 -fill "'#F0F6FC'" \
    -gravity NorthWest -annotate +94+166 "'ROBOTIS AI Harness'" \
  -font "$HN" -pointsize 33 -fill "'#8B949E'" \
    -gravity NorthWest -annotate +96+292 "'Claude Code governance layer — style, commits and'" \
  -font "$HN" -pointsize 33 -fill "'#8B949E'" \
    -gravity NorthWest -annotate +96+336 "'method enforced by hooks, not left to memory.'" \
  -font "$MN" -pointsize 17 -fill "'#484F58'" \
    -gravity NorthEast -annotate +96+150 "'ONE COMMAND'" \
  -font "$MN" -pointsize 42 -fill "'#2F81F7'" \
    -gravity NorthEast -annotate +96+182 "'/harness'" \
  -font "$MN" -pointsize 21 \
  "$CHIPS" \
  -fill "'#21262D'" -draw "'rectangle 96,532 1184,533'" \
  -font "$MN" -pointsize 19 -fill "'#484F58'" \
    -gravity NorthWest -annotate +96+556 "'github.com/jack0682/ROBOTISAI_harness'" \
  -font "$MN" -pointsize 19 -fill "'#484F58'" \
    -gravity NorthEast -annotate +96+556 "'Apache-2.0'" \
  -depth 8 -strip \
  -define png:exclude-chunk=time,tEXt,zTXt,iTXt \
  "$OUT"

magick identify -format "wrote %f  %wx%h  %b\n" "$OUT"
