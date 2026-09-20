# ROBOTIS JavaScript Style Guide — reference

Source: *ROBOTIS JavaScript Style Guide*, 2020-03-10 first edition, **Revision 9
(2022-07-28)**. Baseline **ES2015 (ES6)**, HTML5, CSS3. Covers JavaScript,
TypeScript, HTML and CSS/Sass.

This guide states **only** what must stay consistent with the other ROBOTIS
languages, or what is worth contrasting with them. Everything else defers:

| | defers to |
|---|---|
| JavaScript | **Airbnb JavaScript Style Guide** (then Google JavaScript) |
| TypeScript | ROBOTIS JavaScript Style, then **Google TypeScript Style Guide** |
| HTML | **Google HTML/CSS Style Guide** |
| CSS / Sass | **Airbnb CSS / Sass Styleguide** |

---

## Naming

Four forms are in play — note that Airbnb's names differ from ROBOTIS's:

| ROBOTIS | Airbnb |
|---|---|
| `CamelCased` | `PascalCase` |
| `lowerCamelCased` | `camelCase` |
| `ALL_CAPITALS` | — |
| `kebab-case` | — |

| kind | convention |
|---|---|
| package | `kebab-case` |
| file | `CamelCased` **or** `lowerCamelCased` |
| class, constructor, type, interface, namespace, enum | `CamelCased` |
| variable, object, function, instance | `lowerCamelCased` |
| constant | `ALL_CAPITALS` |

**A file's name matches its `export default`.** Anything without a default
export is `lowerCamelCased`.

Variables are **nouns**; functions are **imperative verbs**. No
readability-harming abbreviations.

### Enums

```jsx
export const enum DriveMode {
  ASSISTANCE_MODE = 0,
  AUTONOMOUS_MODE = 1,
  MANUAL_MODE = 2,
  EMERGENCY_MODE = 3,
}
```

---

## Comments

English, complete sentences, first word capitalised. **No Korean in source.**
Documentation comment `/** */` (JSDoc); implementation comment `//` or `/* */`.

### File comments — different from C++/Python
**JavaScript does not put the copyright/licence block in each file.** It lives in
`LICENSE` or `LICENSE.md`. Where a header is used, the order is copyright then
licence, year = first-authored year, never bumped; multiple licences go in a
top-level `LICENSES/` folder.

```jsx
// Copyright 2018 ROBOTIS CO., LTD.
```

---

## Formatting

- **Line length: 100** characters (Airbnb / ROS 2 Developer Guide).
- **UTF-8** only (Google JS §2.2).
- **Indent: 2 spaces.** Tabs forbidden, always.
- Every file ends with a blank line.

## Modules (import / export)

Three groups, one blank line between each, **alphabetised** within a group:

1. Standard library modules
2. Third-party library modules
3. Local library modules

**One module per line** — break `import` per module to keep diffs minimal.
One blank line between the module block and the body.

## References — `const` by default

**Never `var`.** It is function-scoped, hoisted, re-assignable and
re-declarable, which is four ways to create a bug.

| keyword | scope | hoisting | re-assign | re-declare |
|---|---|---|---|---|
| `var` | function | yes | yes | yes |
| `let` | block | no | yes | no |
| `const` | block | no | no | no |

Use `const` for every reference; reach for `let` only when reassignment is
genuinely required.

## Strings — **single quotes**

`'single'`, not `"double"` — matching Python, contrasting with C/C++/Go which
use `"`. The split is deliberate: it preserves each language's idiom while
removing the choice, per the ROS 2 Developer Guide.

Mixing is allowed when the string itself contains a quote. Use backtick
template strings for interpolation (`` `${expression}` ``) or long strings.

## Comparison — **always `===` / `!==`**

Never `==` / `!=`: they coerce types.

```jsx
5 == '5'   // true   ← the bug
5 != '5'   // false

5 === '5'  // false  ← correct
5 !== '5'  // true
```

## Units
Same as `cpp.md` §2-8 — REP 103. `x: forward`, `y: left`, `z: up`; radians.

---

## Lint and tooling

- **ESLint** for syntax and style, with configs `eslint:recommended` and
  `airbnb-base`.
- **Prettier** for formatting.
- VS Code: the *ESLint* and *Prettier* extensions.

## EOF
Every file ends with a blank line.
