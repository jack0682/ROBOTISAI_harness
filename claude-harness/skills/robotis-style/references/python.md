# ROBOTIS Python Style Guide — reference

Source: *ROBOTIS Python Style Guide*, 2018-03-19 first edition, **Revision 18
(2025-01-10)**. Baseline **Python ≥ 3.5**. Follows PEP 8, the *ROS 2 Developer
Guide*, *ROS 2 Code style* and the *ROS 1 Python Style Guide*; anything
unspecified falls back to the *Google Python Style Guide* and the *numpy
Docstring Guide*.

---

## 2. Naming

| kind | convention |
|---|---|
| package, module, topic/service, file, variable, function, method | `snake_case` |
| class / type | `CamelCased` |
| constant | `ALL_CAPITALS` |

Types and variables are **nouns**; functions are **imperative verbs**.

### 2-2 Packages
`snake_case`. Repository name == meta-package name. *project + area*
(`gaemi_navigation`); *project + package* (`gaemi_map_server`).
Note the tension: ROS conventionally uses `_` in package names while PEP 8
discourages it. ROS wins here.

### 2-4 Files
`snake_case`, descriptive — `laser_distance_sensor.py`, not `lds.py`.
**A ROS package's main script is named after the node.**
Exception: `/msg` and `/srv` files are `CamelCased`.

### 2-5 Modules
`snake_case`. An underscore inside is allowed but prefer a **single word**.
C/C++ extension modules start with `_`.

### 2-9 Types
`CamelCased`. An acronym is written **fully uppercase**: `HTTPServerError`,
not `HttpServerError`. An internal class is prefixed with one `_`.

### 2-15 Underscore — it carries meaning in Python

| form | meaning |
|---|---|
| `_single_leading` | internal use; not imported by `from M import *`. Protected. |
| `single_trailing_` | avoids collision with a Python keyword |
| `__double_leading` | name mangling inside a class (`__boo` → `_FooBar__boo`). Private. |
| `__double_both__` | magic object (`__init__`, `__file__`) — do not invent new ones |

### 2-17 String quotes — **single quotes**
All strings use `'single quotes'`, not `"double"`. Docstrings use `"""`.
This deliberately departs from PEP 8 to reduce choices, per the ROS 2 Developer
Guide. (Team-wide: C/C++/Go use `"`; Python/JavaScript use `'`.)

---

## 3. Comments

- English, complete sentences, first word capitalised. **No Korean in source.**
- `# ` — hash then **one** space.
- Inline comment: **two spaces** before the `#`.
- **Every Python file starts with the shebang** `#!/usr/bin/env python3`.

### 3-2 File comments
Order: **shebang → copyright → licence**. Year = first-authored year, never
bumped. ROS `.msg`/`.srv`/`.action`/`.launch.py` carry no licence.

```python
#!/usr/bin/env python3
# Copyright 2019 ROBOTIS CO., LTD.
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
```

### 3-3 Docstring (PEP 257)
The closing `"""` sits alone on its own line, with a blank line directly above it.

```python
def add_two_numbers(number1, number2):
    """Returns the sum of two numbers
    Args:
        number1 (int): First number to add
        number2 (int): Second number to add
    Returns:
        int: Sum of `number1` and `number2`

   """
```

---

## 4. Formatting

### 4-1 Line length — **99 characters**
Not PEP 8's 79, and not 100: 99 is `ament_flake8`'s default and lint must pass.

### 4-2 UTF-8 (PEP 3120). 4-3 Indent = **4 spaces**, tabs forbidden

### 4-4 Brackets
`list = [1, 2, 3]`, `dictionary = {'age': 30}`, `tuple = (1, 2, 3)`.

### 4-5 Hanging indent

```python
# Good — fits on one line
foo = function_name(var_one, var_two, var_three, var_four)

# Good — does not fit: break after '(' and indent the body an extra level
#        so the arguments are visually distinct from the function body
def long_long_long_long_function_name(
        var_one,
        var_two,
        var_three,
        var_four):
    print(var_one)
```

```python
# Bad — arguments aligned to the opening paren
foo = long_function_name(var_one, var_two,
                         var_three, var_four)

# Bad — first argument left on the opening line without vertical alignment
foo = long_function_name(var_one, var_two,
    var_three, var_four)

# Bad — arguments indistinguishable from the body
def long_function_name(
    var_one, var_two, var_three,
    var_four):
    print(var_one)
```

### 4-6 Conditionals
- Compare to `None` with `is` / `is not` **only**.
- Never compare a boolean with `==`, `is`, or `is not`.
- An empty string/list/tuple is already falsy — use it.
- No compound statements: one statement per line.

```python
# Good              # Bad                    # Worst
if greeting:        if greeting == True:     if greeting is True:
if not seq:         if not len(seq):
if seq:             if len(seq):

# Good                        # Bad
if foo == 'blah':             if foo == 'blah': do_blah_thing()
    do_blah_thing()           do_one(); do_two(); do_three()
do_one()
```

### 4-12 Horizontal whitespace
No space inside `[]`, `{}`, `()`; no space before `,` `:` `;`; no space before a
call's `(` or an index's `[`. No alignment padding. No trailing whitespace.

```python
spam(ham[1], {eggs: 2})        # Good
spam( ham[ 1 ], { eggs: 2 } )  # Bad

dict['key'] = list[index]      # Good
dict ['key'] = list [index]    # Bad
```

One space around binary operators — but **drop the spaces around the
lower-precedence operator's neighbours to show grouping**:

```python
# Good                     # Bad
i = i + 1                  i=i+1
submitted += 1             submitted +=1
x = x*2 - 1                x = x * 2 - 1
hypot2 = x*x + y*y         hypot2 = x * x + y * y
c = (a+b) * (a-b)          c = (a + b) * (a - b)
```

**No spaces around `=` for a keyword argument or a default value:**

```python
def complex(real, imag=0.0):        # Good
    return magic(r=real, i=imag)

def complex(real, imag = 0.0):      # Bad
    return magic(r = real, i = imag)
```

### 4-13 Vertical whitespace
1 blank line between the file comment and the imports; **2** between the imports
and the body; **2** between top-level functions and class definitions; 1 between
methods. A function never starts with a blank line. **File ends with one blank
line.**

### 4-14 Console output
Use `str.format` with **numbered** placeholders.

```python
print('name: {0}, number: {1}'.format(self.name, self.num))

# ROS 2
self.node.get_logger().info('Result of service call: {0}'.format(response.success))
```

---

## 6. Imports

Three groups, one blank line between each, alphabetised (Unicode,
case-insensitive) within a group, **two** blank lines before the body:

1. Standard library
2. Third-party
3. Local application / library

**One import per line.** `import os, sys` is forbidden.

```python
import os
from threading import Lock

import cv2
import numpy as np
from rclpy.action import ActionClient
from sensor_msgs.msg import BatteryState
from std_msgs.msg import Bool

from tote_db.db_manager.db_container import DbContainer
from tote_msgs.msg import Cargo
```

Import a class as `from myclass import MyClass`; on a name collision, import the
module instead (`import myclass`) and qualify at the use site.

---

## 9. Miscellaneous

- **9-98** Lint with `flake8` or `pylint`; for ROS 2 packages, **`ament_flake8`**.
- **9-99** Every file ends with a blank line.
