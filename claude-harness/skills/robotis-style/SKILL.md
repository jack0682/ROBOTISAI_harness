---
name: robotis-style
description: "MANDATORY for any ROBOTIS code. The ROBOTIS Programming Style Guides (C++ Rev35, C Rev18, Python Rev18, ROS Rev10, JavaScript Rev9) — naming, formatting, comments, headers, file layout, lint. Load BEFORE writing, editing or reviewing any .c/.h/.cpp/.hpp/.py/.js/.ts/.jsx/.tsx/.css/.html file, any ROS 2 package file (package.xml, CMakeLists.txt, setup.py, .msg/.srv/.action/.launch.py), or when the user says \"스타일 가이드\", \"코딩 컨벤션\", \"style guide\", \"coding standard\", \"코드 리뷰\", \"lint\", \"네이밍\", \"naming convention\"."
---

# ROBOTIS Programming Style Guide

**This is not advisory.** Code written for ROBOTIS follows these guides. When
a rule here conflicts with your default habits, the guide wins. When it
conflicts with the surrounding file, see *Which guide applies* below.

## Step 0 — which guide applies

| situation | guide |
|---|---|
| Code we own | **ROBOTIS Style Guide (this skill)** |
| Modifying third-party / open source | **that project's own style guide** — do not impose ours |
| Rule absent from the ROBOTIS guide | C++→Google C++, Python→PEP 8 then Google Python, JS→Airbnb, TS→Google TS, HTML/CSS→Google HTML/CSS, Sass→Airbnb |
| ROS 2 specifics on top of a language | **also** load `references/ros.md` |

Then load the language reference:

- `references/cpp.md` — C++14. Also the base document the others defer to.
- `references/c.md` — C99, microcontroller firmware.
- `references/python.md` — Python ≥3.5.
- `references/ros.md` — ROS 2 package/message/launch/doc files.
- `references/javascript.md` — ES2015+, TypeScript, HTML, CSS/Sass.
- **`references/license-header.md`** — the mandatory Apache 2.0 /
  ROBOTIS AI header with the `Author:` line. Applies to **every**
  language; overrides the published guide. Read it before creating any
  new file.

## The rules that hold in every language

These repeat across all five guides. They are the ones most often violated.

1. **Never a tab character.** Not in any file, under any circumstance. Set the
   editor to emit spaces.
2. **UTF-8 only.**
3. **No Korean in source.** Comments are written in **English**, as complete
   sentences, first word capitalised (unless it is a lowercase identifier).
4. **Every file ends with one blank line** (EOF marker).
5. **No trailing whitespace** at end of line.
6. **Apache 2.0 licence header at the top of every source file**, before
   anything but a shebang — `Copyright <first-authored-year> ROBOTIS AI`, the
   Apache grant, then `Author: <name> <email>` taken from the repository's local
   git identity. **All code in this organisation is Apache License 2.0.**
   Full templates per language: **`references/license-header.md`** — read it,
   this team's header **overrides** the published ROBOTIS guide on the holder
   name and adds the `Author:` line. Check with
   `python3 claude-harness/scripts/check_license_header.py`.
   The year is the year the file was first written and is never bumped.
   Exceptions: ROS `.msg`, `.srv`, `.action`, `.launch.py` carry no licence.
7. **Types and variables are nouns. Functions are imperative verbs.**
   `FileOpener`, `num_errors`; `open_file()`, `set_num_errors()`.
8. **No readability-harming abbreviations.** `error_count`, not `error_cnt`.
   Conventional ones (`num`, `dns`, `SDK`, `API`) are allowed by team consent.
9. **Self-explanatory code beats a comment.** Comment for the reader who will
   not understand it later — including you.
10. **Run the linter.** Style is checked by a tool, not by eye. See each
    reference's lint section.
11. **Sort alphabetically, not by purpose** — include/import groups, package.xml
    entries, CMakeLists entries. Ordering is by Unicode codepoint, case-insensitive.

## The per-language table you will get wrong if you guess

| | indent | line limit | string quotes | source / header |
|---|---:|---:|---|---|
| **C++** | **2** spaces | **100** | `"` double | `.cpp` / `.hpp` |
| **C** | **2** spaces | **100** | `"` double | `.c` / `.h` |
| **Python** | **4** spaces | **99** | `'` **single** | `.py` |
| **JavaScript / TS** | **2** spaces | **100** | `'` **single** | `.js` / `.ts` |

The quote rule is deliberate and easy to get backwards: **C/C++ use double
quotes, Python and JavaScript use single quotes.** Python docstrings use `"""`.

## Naming, at a glance

| | C / C++ | Python | JavaScript / TS |
|---|---|---|---|
| package | `snake_case` | `snake_case` | `kebab-case` |
| file | `snake_case` | `snake_case` | `CamelCased` or `lowerCamelCased` |
| namespace | `snake_case` | — | `CamelCased` |
| class / type / enum | `CamelCased` | `CamelCased` | `CamelCased` |
| function / method | `snake_case` | `snake_case` | `lowerCamelCased` |
| variable | `snake_case` | `snake_case` | `lowerCamelCased` |
| constant / macro | `ALL_CAPITALS` | `ALL_CAPITALS` | `ALL_CAPITALS` |

**ROS `.msg` / `.srv` / `.action` filenames are `CamelCased`** in every language,
because they become types after generation. This is the one exception to
`snake_case` filenames.

## Units — REP 103, non-negotiable

`x: forward`, `y: left`, `z: up`; right-hand rule for positive rotation.
metre · kilogram · second · ampere · **radian** · hertz · newton · watt · volt ·
celsius · tesla. Never degrees in an interface.

## Before you claim the work is done

- [ ] Linter run and clean (`ament_cpplint` / `ament_flake8` / `ESLint`)
- [ ] No tabs, no trailing whitespace, file ends with a blank line
- [ ] Copyright header present, year = first-authored year
- [ ] Comments in English, complete sentences
- [ ] Naming table above actually applied — check functions vs. variables
- [ ] Include/import groups separated and alphabetised

Style is verifiable. Run the linter and report its output; do not assert
compliance (`kernel/anti_patterns.md`).

## Revising the guide

These documents are owned by the **프로그래밍 스타일 가이드 협의체**. Do not
edit the reference files to match code you have already written — a deviation is
resolved by changing the code, or by taking the case to the 협의체. A change to
the C++ guide must be mirrored into the C guide at the same level, and vice versa.
