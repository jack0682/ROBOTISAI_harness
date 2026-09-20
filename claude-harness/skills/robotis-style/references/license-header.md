# ROBOTIS AI licence header — mandatory, every source file

**All code in this organisation is Apache License 2.0.** Every source file
carries the header below, verbatim, at the very top.

> **This diverges from the ROBOTIS Programming Style Guide on two points, by
> team decision.** The published guide specifies `Copyright <year> ROBOTIS CO.,
> LTD.` and defines no `Author:` line; the JavaScript guide keeps the notice in
> `LICENSE` rather than per file. This team's rule is the one below and
> overrides all three. The rest of the guide's file-comment rules still hold —
> in particular the year is the **first-authored year and is never bumped**, and
> a description of the file's contents follows the header.

## The header

```
Copyright 2026 ROBOTIS AI

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Author: <name> <<email>>
```

**`Author:` is the person who wrote the file — the *current* author, not a
copied name.** Take it from the repository's configured identity, which is the
same identity that signs the commit:

```sh
git config --local user.name    # → the <name>
git config --local user.email   # → the <email>
```

Never hardcode someone else's name, never carry an author line over from a file
you copied, and never guess. If the local identity is unset, stop and ask —
`commit_guard` will block the commit anyway.

## Per-language form

The comment marker changes; nothing else does.

### Python, shell, YAML, CMake, `package.xml`-adjacent scripts — `#`
A Python file puts the shebang **above** the header.

```python
#!/usr/bin/env python3
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
# Author: <name> <<email>>
```

### C, C++, JavaScript, TypeScript — `//`

```cpp
// Copyright 2026 ROBOTIS AI
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.
//
// Author: <name> <<email>>
```

### XML, HTML — `<!-- -->`
One block comment wrapping the same lines. In `package.xml` the header goes
**after** the `<?xml?>` and `<?xml-model?>` declarations.

### CSS / Sass — `/* */`

## Where the header does **not** go

Per the ROBOTIS ROS Style Guide §3-2 / §4.7, unchanged:

- ROS interface files: **`.msg`, `.srv`, `.action`** — no licence.
- **`.launch.py`** — no licence. (It is the one Python file with no header.)
- Generated files, and vendored third-party code, keep whatever they came with.

`package.xml` declares the licence as a tag, not a header:

```xml
<license>Apache 2.0</license>
```

And the repository root carries the full `LICENSE` file (single licence → one
file named `LICENSE`, no extension).

## Inherited files carry no `Author:`

Code this team did not write but now owns gets the copyright line and the
Apache grant, and **stops there**. Putting the current user in `Author:` on a
file they did not write is a false statement, and a licence header is the
last place to make one.

The 97 harness files this deployment inherited were backfilled that way
(`--no-author`). Every file created from here on carries the full three-part
header.

The gate matches that rule: `--staged` requires the header on every staged
file, and the `Author:` line only on files the commit **adds**.

## Checking it

```sh
python3 claude-harness/scripts/check_license_header.py            # report
python3 claude-harness/scripts/check_license_header.py --fix      # insert
python3 claude-harness/scripts/check_license_header.py --staged   # pre-commit
```

`--fix` derives `Author:` from the local git identity and refuses to run
without one. The pre-commit hook runs `--staged`, so a file missing its header
cannot reach a commit.
