# ROBOTIS C++ Style Guide — reference

Source: *ROBOTIS C++ Style Guide*, 2016-05-03 first edition, **Revision 35
(2025-01-10)**. Baseline **C++14**. Targets 100% compliance with the *ROS 2
Developer Guide*, *ROS 2 Code style* and the *ROS C++ Style Guide*; anything
unspecified falls back to the *Google C++ Style Guide*.

Item numbering follows the ROBOTIS guides for cross-compatibility, so numbers
are skipped where the source skips them.

---

## 2. Naming

### 2-1 General

| kind | convention |
|---|---|
| package, topic/service, file, namespace, variable, function, method | `snake_case` |
| type, class, struct, enum | `CamelCased` |
| constant, macro | `ALL_CAPITALS` |

Types and variables are **nouns**; functions are **imperative verbs**.

```cpp
int8_t price_count_reader;    // Do not abbreviate
int32_t num_errors;           // 'num' is a well-known exception
int32_t num_dns_connections;  // 'dns' is standard; allowed

int32_t error_cnt;    // Bad
int32_t error_count;  // Good
```

### 2-2 Packages
`snake_case`. Repository name and meta-package name are identical. Prefer
*project + functional area* (`gaemi_navigation`) for meta-packages and
*project + package* (`gaemi_map_server`) for packages inside a repository.

### 2-4 Files
`snake_case`. Source `.cpp`, header `.hpp`.
Name files descriptively — `laser_distance_sensor.cpp`, not `lds.cpp`.
A file holding class `FooBar` is `foo_bar.hpp` / `foo_bar.cpp`; **the filename
must match the class it contains.** Library prefix `lib` binds to the next word:
`libmy_great_thing` (good), `lib_my_great_thing` (bad).

**Exception:** ROS `/msg` and `/srv` files are `CamelCased`
(`TransformStamped.msg`, `SetSpeed.srv`) — they become generated types.

### 2-6 Variables
- `snake_case`, nouns.
- **Global variables are forbidden.** Where unavoidable, prefix `g_`.
- **Class member variables end with a trailing underscore**, `public` or
  `private` alike: `table_name_`.
- **Struct data members do not** take the trailing underscore.
- Struct constructor arguments take a **leading** underscore to avoid collision.

```cpp
struct UrlTableProperties
{
  UrlTableProperties(string _name) : name(_name)
  string name;          // no trailing underscore
  int32_t num_entries;  // no trailing underscore
};

// class data member
string table_name_;
```

### 2-7 Variable types
Use the `<cstdint>` fixed-width types. ROS message primitives map as:

| msg | C++ | | msg | C++ |
|---|---|---|---|---|
| bool | `uint8_t` | | int32 / uint32 | `int32_t` / `uint32_t` |
| int8 / uint8 | `int8_t` / `uint8_t` | | int64 / uint64 | `int64_t` / `uint64_t` |
| int16 / uint16 | `int16_t` / `uint16_t` | | float32 / float64 | `float` / `double` |
| string | `std::string` | | time / duration | `ros::Time` / `ros::Duration` |

Arrays (fixed- and variable-length, `uint8[]`) all map to `std::vector<T>`;
`bool[]` maps to `std::vector<uint8_t>`.

### 2-8 Units — REP 103
`x: forward`, `y: left`, `z: up`. Right-hand rule for positive rotation.
metre, kilogram, second, ampere, **radian**, hertz, newton, watt, volt, celsius,
tesla.

### 2-9 / 2-10 Types and enums
`CamelCased`. An acronym inside a name may stay uppercase: `HokuyoURGLaser`.
Enum constants are `ALL_CAPITALS`; pair the enum with a `namespace` and a
`typedef`.

```cpp
namespace imu
{
enum SensingErrors
{
  NONE = 0,
  OUT_OF_MEMORY = 1,
  UNKNOWN_INPUT = 2,
};
}  // namespace imu
typedef imu::SensingErrors SensingErrors;
```

### 2-11 Functions and methods
`snake_case`. Accessors/mutators match the variable name they touch. Existing
`mixedCase` code is **not** forced to convert — but **ROS 2 and all new code
must use `snake_case`.**

### 2-12 / 2-13 Constants and macros
`ALL_CAPITALS`. Prefer `constexpr` over `const` (C++11+). Macros are generally
**forbidden**; where a macro stands in for a constant, give at least 10 decimal
places (`#define PI 3.1415926535`).

---

## 3. Comments

- English, complete sentences, first word capitalised. **No Korean in source.**
- Documentation comment `/** */` (Doxygen); implementation comment `//` or `/* */`.
- One space after the opener (`// Like this`).
- Inline comment on a code line: **two spaces** before `//`.
- Paragraphs inside a block comment are separated by a line holding one `*`.

### 3-2 File comments
Copyright then licence, at the very top of every source and header file.
**Year = first-authored year, never updated.** Multiple licences go in a
top-level `LICENSES/` folder. ROS `.msg`/`.srv`/`.action`/`.launch.py` carry none.

```cpp
// Copyright 2018 ROBOTIS CO., LTD.
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
```

Proprietary code carries only the copyright line, and `<license>Proprietary</license>`
in `package.xml`.

A `.hpp` describes *purpose and usage* of what it declares; a `.cpp` describes
*implementation and algorithm*.

### 3-3 Docstring (Doxygen)

```cpp
/** Get Status
  *
  * @param id The servo ID.
  * @return -1 is get_status failed. other is servo`s status error value.
  */
int8_t get_status(int8_t id);
```

---

## 4. Formatting

### 4-1 Line length — **100 characters**, including whitespace
(Deliberately not Google's 80; follows the ROS 2 Developer Guide.)

### 4-2 UTF-8 only. 4-3 Indent = **2 spaces**, tabs forbidden
`public:` / `protected:` / `private:` are **not** indented.

### 4-4 Braces — the trap

**Functions, classes, namespaces: `{` goes on its own line.
Control flow (`if`/`else`/`for`/`while`/`switch`): `{` stays on the same line.**

`}` occupies its own line. An empty body may be written `{}`. Braces may be
omitted only for a **single-line** body with no `else`; two or more lines
**require** braces.

```cpp
class Point
{
public:
  Point(double xc, double yc);
  ~Point() {}
  double distance(const Point & other) const;
  double x_;
};

double Point::distance(const Point & other) const
{
  double dx = x_ - other.x_;
  return sqrt(dx * dx);
}

namespace foo
{
int32_t foo(int32_t bar) const
{
  switch (bar) {
    case 0:
      ++bar;
      break;
    default:
      bar += bar;
      break;
  }
}
}  // namespace foo
```

### 4-5 Function declarations and definitions
Return type on the same line as the name. If arguments do not fit, break and
indent **2 spaces**. Constructor initialiser lists break with `:` at column 0
of the continuation and 2-space alignment.

```cpp
ReturnType LongClassName::really_really_long_function_name(
  Type param_name1,
  Type param_name2)
{
  do_something();
}

MyClass::MyClass(int var)
: some_var_(var),
  some_other_var_(var + 1)
{
  do_something();
}
```

### 4-6 Conditionals
One space between `if` and `(`, and between `)` and `{`. `else if` / `else` sit
on the same line as the closing brace. **Parenthesise every sub-condition.**

```cpp
if (x != a && x != b)      // Bad — operator precedence left implicit
if ((x != a) && (x != b))  // Good

if (condition) {
  ...
} else if (...) {
  ...
} else {
  ...
}

if (x == FOO) return new foo();  // allowed: single line, no else
```

### 4-7 Loops and switch
An empty loop body is `{}` or `continue` — **never a bare `;`**. `switch` always
has a `default`; where it must be unreachable use `ROS_ASSERT(false)`. Never use
`assert` directly.

### 4-8 Pointers and references
Where `*` or `&` could be misread, put one space on each side:
`uint8_t * c;`, `const string & str;`. No space around `.` or `->`.

### 4-9 Class format
Base class on the same line as the subclass, within 100 columns.
Order: `public:`, then `protected:`, then `private:`, none indented, each
preceded by one blank line except the first.

### 4-11 Namespace formatting
Contents are **not** indented. Nesting is *project* then *package*. Close with
a comment naming it: `}  // namespace gaemi`.

### 4-12 Horizontal whitespace
No alignment padding — it forces unrelated diffs when a name changes.

```cpp
// Good            // Bad
x = 1;             x             = 1;
long_variable = 3; long_variable = 3;
```

Two spaces before an inline `//`. No space inside `< >` in templates.
No trailing whitespace.

### 4-13 Vertical whitespace
Minimal. File never starts with a blank line. 1 blank line between the file
comment and the includes; **2** between the includes and the body; 1 between
functions; a function never starts with a blank line. **File ends with one
blank line.** Break **after** an operator, never before.

```cpp
if ((arg1 < 1) &&   // Good
  (arg2 < 1))

if ((arg1 < 1)      // Bad
  && (arg2 < 1)
```

### 4-14 Console output
ROS 2: never `printf` or `std::cout`. Use
`RCLCPP_DEBUG/INFO/WARN/ERROR/FATAL()`.

```cpp
RCLCPP_INFO(this->get_logger(), "[%s] Counting: '%d'", message.c_str(), msg_->count);
```

### 4-15 Lambda and bind
Preferred for ROS 2 topic subscribers and service servers.

### 4-16 Aliases
Prefer `using Bar = Foo;` over `typedef`. Use it for type redefinition only —
avoid `using namespace` for convenience.

---

## 5. Classes

- **5-1** Constructors initialise members only; complex setup goes in `Init()`.
- **5-3** Single-argument constructors are `explicit`.
- **5-4** Disable copy/assign with `DISALLOW_COPY_AND_ASSIGN`, called as the
  **last** entry of the `private:` section.
- **5-5** `struct` only for passive data carriers; otherwise `class`.
- **5-6/5-7** Inherit `public`. Multiple inheritance is discouraged; where used,
  at most one base carries implementation and the rest are pure interfaces with
  the `Interface` suffix.
- **5-9** Declaration order within a section: typedefs/enums → constants →
  constructors → destructor → methods → data members. `friend` always `private:`.
- **5-10** Functions stay short and do one thing. Past ~**40 lines**, look for a
  split.
- **5-11** **One class per file.** Small helper structs/classes used only by that
  class may share it. Bare enums/usings/typedefs/functions go in `common.hpp`.

---

## 6. Header files

### 6-1 Include guard
Path-based, `#define`-style. No `#pragma once`.
`foo/src/bar/baz.hpp` →

```cpp
#ifndef BAR__BAZ_HPP_
#define BAR__BAZ_HPP_
...
#endif  // BAR__BAZ_HPP_
```

### 6-2 Prefer a forward declaration to an `#include`.
### 6-3 Inline only when the body is **≤10 lines**.
### 6-5 Parameter order: **inputs, then outputs.**

### 6-6 Include order — three groups, blank line between each

1. System / standard library headers
2. Third-party library headers
3. This project's headers

Alphabetical (Unicode, case-insensitive) within a group. **Two** blank lines
between the last include and the body. Never `.` or `..` in an include path.

```cpp
#include <cmath>
#include <vector>

#include "rclcpp/logger.hpp"

#include "foo/bar.hpp"
#include "robotis/diagnostic.hpp"
```

### 6-7 No implementation in a header — templates excepted.

---

## 7. Scoping

- Unnamed namespaces **only** in `.cpp`.
- Never declare anything in `namespace std`.
- **Never `using namespace foo;`** — it pollutes. `using std::vector;` inside a
  function/method/class is fine.
- **7-2** Declare variables in the narrowest scope and initialise at declaration.
  Exception: hoist an object out of a hot loop to avoid repeated ctor/dtor.
- **7-3** No static or global variables of class type. Static-duration objects
  must be POD.

---

## 9. Miscellaneous

- **9-1** Format with `clang-format`; for ROS 2 use the `ament_lint` tools.
- **9-2** No Hungarian notation (only `g_` from 2-6 survives).
- **9-3** Plain C++: use `int`; otherwise the `<stdint.h>` sized types. Avoid
  unsigned types — **except** on microcontrollers, where `uint8_t`/`uint16_t`/
  `uint32_t` are permitted when genuinely needed.
- **9-4** Use `const` wherever it is true; `constexpr` in C++11+.
- **9-5** C++ casts only: `static_cast<>()`. Never `(int32_t)x` or `int32_t(x)`.
- **9-6** Prefix increment `++i`.
- **9-7** Prefer inline functions / enums / `const` over macros. No macros in
  `.hpp`. `#define` immediately before use and `#undef` immediately after. No
  `#ifdef` except the include guard. No `##` token pasting.
- **9-8** `0` for int, `0.0` for float, `NULL` for pointer, `""` for char.
- **9-9** `sizeof(variable)`, not `sizeof(type)`.
- **9-10** Ternary on one line only; parenthesise a comparison:
  `number = (count == 10) ? 100 : 200;`
- **9-20** `unique_ptr` for non-copyable ownership (`std::move` to transfer);
  `shared_ptr` where ownership is shared.
- **9-21** STL iterators are named `<name>_it` or `<type>_it`.
- **9-22** Never call `exit()` in a library.
- **9-23** Never `assert` — use `ROS_ASSERT()` / `ROS_BREAK()`.
- **9-98** Lint with `cpplint`; for ROS 2, `ament_cpplint`, `ament_cppcheck`,
  `ament_uncrustify`.
- **9-99** Every file ends with a blank line.
