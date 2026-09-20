---
paths:
  - "**/*.{c,h,cc,cpp,hpp,cxx,hxx,py,js,jsx,ts,tsx,css,scss,html}"
  - "**/package.xml"
  - "**/CMakeLists.txt"
  - "**/setup.py"
  - "**/setup.cfg"
  - "**/plugin.xml"
  - "**/CHANGELOG.rst"
  - "**/*.{msg,srv,action}"
  - "**/*.launch.py"
---

# This file is governed by the ROBOTIS Programming Style Guide

**Load `claude-harness/skills/robotis-style/SKILL.md` before writing, editing or
reviewing this file, and the matching `references/` document for its language.**
This is a team standard, not a preference: code that does not follow it does not
pass review.

The four that are wrong most often, and are wrong silently:

| | C / C++ | Python | JS / TS |
|---|---:|---:|---|
| indent | **2** spaces | **4** spaces | **2** spaces |
| line limit | **100** | **99** | **100** |
| quotes | `"` double | `'` single | `'` single |

Plus: **never a tab**, comments in **English** (no Korean in source), a
`Copyright <first-year> ROBOTIS CO., LTD.` header, and **every file ends with a
blank line**.

Style is checked by a linter — `ament_cpplint`, `ament_flake8`, `ESLint` — and
a compliance claim is the linter's output, not your assertion
(`claude-harness/kernel/anti_patterns.md`).

> This rule fires on the file, not on how the request was worded. The skill is
> the authority; this rule only names it.
