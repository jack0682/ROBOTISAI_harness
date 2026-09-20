# ROBOTIS C Style Guide — reference

Source: *ROBOTIS C Style Guide*, 2016-12-20 first edition, **Revision 18
(2020-06-19)**. Baseline **C99**. Written for **microcontroller firmware**.

**This guide is a delta on the C++ guide.** Everything not restated here is
identical to `cpp.md` — read that first. Anything changed in one guide must be
mirrored into the other at the same level.

---

## Identical to C++ (`cpp.md`)

Naming kinds (1, 2-1, 2-2, 2-3), units (2-8), type names minus `class` (2-9),
function names minus `class` (2-11), macro names (2-13), naming exceptions
(2-14), Unicode (2-16), **all of comments (3)**, line length / UTF-8 / tabs
(4-1…4-3), braces minus `class` and `namespace` (4-4), conditionals (4-6),
loops and switch (4-7), pointers (4-8), horizontal and vertical whitespace
(4-12, 4-13), include guard (6-1), local variables (7-2), static/global minus
`class` (7-3), and miscellaneous 9-1, 9-2, 9-3, 9-4, 9-6, 9-7, 9-8, 9-9, 9-10,
9-98, 9-99.

---

## Where C differs

### 2-4 Files
Source `.c`, header `.h` (C++ uses `.cpp` / `.hpp`).
`snake_case`, descriptive — `laser_distance_sensor.c`, not `lds.c`.
Library prefix binds: `libmy_great_thing` (good), `lib_my_great_thing` (bad).

### 2-6 Variables
As C++, minus everything about class members. The trailing-underscore rule
does not apply — there are no class data members.

### 2-7 Variable types
Use the `<stdint.h>` fixed-width types so that porting across microcontrollers
and compilers cannot silently change a width:

`int8_t` · `uint8_t` · `int16_t` · `uint16_t` · `int32_t` · `uint32_t` ·
`int64_t` · `uint64_t` · `float` · `double`

### 2-10 Enums
`CamelCased`, constants `ALL_CAPITALS`. Pair with a `typedef` — there is no
`namespace` in C.

```c
enum SensingErrors
{
  NONE = 0,
  OUT_OF_MEMORY = 1,
  UNKNOWN_INPUT = 2,
};
typedef enum SensingErrors SensingErrors;
```

### 2-12 Constants
`ALL_CAPITALS`. `const`, not `constexpr` — C99 has no `constexpr`.

```c
const uint8_t DAYS_IN_A_WEEK = 7;
```

### 4-5 Function declarations and definitions
Same shape as C++ without the class qualifier. Return type on the name's line;
break and indent **2 spaces** when it does not fit.

```c
ReturnType really_long_function_name(Type param_name1, Type param_name2)
{
  do_something();
}

ReturnType really_really_really_long_function_name(
  Type param_name1,  // 2 space indent
  Type param_name2,
  Type param_name3)
{
  do_something();  // 2 space indent
}
```

### 6-6 Include order
Same three groups as C++, but the first group is the **C Standard Library**
(`<stdint.h>`, `<string.h>`, …). Prefer `.h` for C, `.hpp` for C++.

### 6-7 Header contents
Declarations only. **No implementation of any kind in a header** — C has no
templates, so the C++ template exception does not apply.

### 9-5 Casting — **the one place C is allowed to differ**
C uses the C-style cast:

```c
int32_t y = (int32_t)x;   /* C — correct */
```

C++ must use `static_cast<>()`. Do not carry the C form into `.cpp`.

---

## Sections that do not exist in C

**5. Classes** — not applicable.
**7-1 Namespaces** — not applicable; use a `snake_case` file-scope prefix and
`static` for internal linkage instead.
