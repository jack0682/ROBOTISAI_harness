# ROBOTIS ROS Style Guide — reference

Source: *ROBOTIS ROS Style Guide*, 2019-07-25 first edition, **Revision 10
(2020-06-16)**. Baseline **ROS 2**. This guide **supplements** the language
guides — it covers what a language style guide cannot: package layout, package
files, message files, launch files, docs. Anything unspecified falls back to the
*ROS 2 Developer Guide* and the *REPs*.

Load this **in addition to** `cpp.md` / `python.md`, never instead of them.

> Example contact addresses and contributor names from the source document have
> been replaced with placeholders here.

---

## 2. Naming

| kind | convention |
|---|---|
| file | `snake_case` |
| `.msg`, `.srv`, `.action` | **`CamelCased`** |

Extensions are always lowercase. `.msg`/`.srv` become generated types after
conversion, which is why they alone are `CamelCased`:

```
TransformStamped.msg
SetSpeed.srv
```

These filenames are fixed and keep their own spelling:
`package.xml`, `CMakeLists.txt`, `README.md`, `LICENSE`, `CHANGELOG.rst`,
`.gitignore`, `.travis.yml`, `.repos`

---

## 3. Filesystem

Files over **10 MB** — maps, bags, meshes — live in a separate repository and
are pulled in, never committed here.

```
├── ros2_examples/                    (meta-package)
│   ├── package.xml
│   ├── CMakeLists.txt
│   └── CHANGELOG.rst
│
├── example_cpp_package/              (C++ package)
│   ├── package.xml
│   ├── CMakeLists.txt
│   ├── CHANGELOG.rst
│   ├── LICENSE
│   ├── doc/manual.md
│   ├── maps/ · worlds/ · meshes/ · urdf/ · rviz/ · param/
│   ├── launch/
│   │   ├── demo.launch.py
│   │   └── robot.launch.py
│   ├── include/
│   │   └── example_cpp_package/      ← note: <package name>
│   │       ├── diff_drive_controller.hpp
│   │       └── devices/buzzer.hpp
│   ├── src/
│   │   ├── main.cpp
│   │   └── diff_drive_controller.cpp
│   └── test/
│       ├── CMakeLists.txt
│       └── TEST_control_table_parser.cpp
│
├── example_python_package/           (Python package)
│   ├── package.xml
│   ├── setup.py
│   ├── setup.cfg
│   ├── CHANGELOG.rst
│   ├── LICENSE
│   ├── example_python_package/       ← note: <package name>
│   │   ├── __init__.py
│   │   └── publisher/{__init__,counter,main}.py
│   ├── launch/ · param/
│   └── resource/examples_rclpy
│
├── example_rqt_package/              (Python rqt package)
│   ├── package.xml · CMakeLists.txt · plugin.xml
│   ├── CHANGELOG.rst · LICENSE
│   ├── launch/ · param/
│   ├── resource/{images/, resouce.qrc, example.ui}
│   ├── scripts/example_rqt_package
│   └── src/example_rqt_package/*.py
│
└── example_msgs/                     (msgs package)
    ├── package.xml · CMakeLists.txt
    ├── CHANGELOG.rst · LICENSE
    ├── msg/{Battery.msg, Temperature.msg}
    └── srv/{Buzzer.srv, Sound.srv}
```

The C++ include path repeats the package name (`include/<package_name>/…`), and
the Python package directory repeats it too. Both are easy to get wrong.

---

## 4. Package files

### 4.1 `package.xml`
**Package Format 3** (REP 149). No blank lines anywhere in the file. Items in a
repeated group are sorted **alphabetically**, not by purpose.

```xml
<?xml version="1.0"?>
<?xml-model href="http://download.ros.org/schema/package_format3.xsd" schematypens="http://www.w3.org/2001/XMLSchema"?>
<package format="3">
```

Tag order under `<package>`:
1. `name`, `version`, `description`, `maintainer`, `license`, `url`, `author`
2. `buildtool_depend`, `buildtool_export_depend`
3. `depend`, `build_depend`, `build_export_depend`, `exec_depend`, `doc_depend`,
   `test_depend`, `group_depend`
4. `conflict`, `replace`, `member_of_group`, `export`

Order under `<export>`: `build_type`, `rviz`, `rqt_gui`, `deprecated`.

Dependency tags:

| tag | use |
|---|---|
| `depend` | the default — covers build, build-export and exec |
| `build_depend` | needed to build; ROBOTIS packages, libraries |
| `build_export_depend` | needed to build a library this package exports |
| `exec_depend` | shared libs, Python modules, executables, launch scripts |

`license` uses exactly one of: `Proprietary`, `Apache 2.0`, `BSD`, `MIT`,
`Boost Software License`, `GPLv2`, `GPLv3`, `LGPLv2.1`, `LGPLv3`.

### 4.2 `CMakeLists.txt`
Build options, dependencies, messages, includes, executables, libraries,
install, test. Repeated groups **alphabetised**. Pure Python packages use
`setup.py` instead. Reference: *ament_cmake User Documentation*.

### 4.3 / 4.4 `setup.py`, `setup.cfg` — pure Python packages only
`setup.py` plays the role of `CMakeLists.txt` + part of `package.xml`;
`package.xml` is still **required** because it is a mandatory ROS package
component. Keys: `name`, `version`, `packages` (`find_packages()`), `data_files`
(resource index, `package.xml`, `.launch.py`, `.yaml`), `install_requires`
(ROS installs nothing via pip — list only `setuptools`, `launch`),
`tests_require` (`pytest`), `zip_safe`, `author`/`author_email`/`maintainer`/
`maintainer_email`, `keywords`, `classifiers`, `description`, `license`,
`entry_points`. `setup.cfg` carries `[develop]` / `[install]` script locations.

### 4.5 `plugin.xml` — required for an RQT plugin package.

### 4.6 `CHANGELOG.rst`

```
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
Changelog for package new_pkg
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

0.0.1 (2019-07-05)
------------------
* Added example_rqt_package as rqt plugin for visualizing messages and services
* Contributors: <name>
```

**This is why commit subjects start with a capitalised verb** — the changelog is
generated from them at release time:

```
git commit -m "Added new features for safety of robot"
git commit -m "Deleted old parameters for test"
```

### 4.7 `LICENSE`
Single licence → a file named `LICENSE`, no extension. Multiple → a `LICENSE/`
folder with one file per licence. **Proprietary code declares the licence in the
code header and `package.xml` only — it adds no `LICENSE` file.**

### 4.8 `README.md`
Open-source facing: full documentation. Internal: package name, dependency
install, how to run the node, how to launch, parameters.

---

## 5. Message files

`CamelCased` filenames. Fields are `type name`, one per line.

```
# Count.msg
std_msgs/Header header
int32 count
```

```
# Calculation.srv — request above, response below, separated by ---
int32 a
int32 b
string arithmetic_operator
---
int32 result
```

```
# Led.action — goal / result / feedback
int32 numbers
---
int32[] result
---
int32[] process
```

---

## 6. Launch files

- **`.launch.py`** — Python-based, the ROS 2 form. Preferred: it can branch,
  monitor process state, and drive node lifecycles.
- **`.xml`** — the ROS 1-style tag form. Still in development; avoid for new work.

---

## 7. Documentation

Source-code documentation lives in `docs/`.

- **C++** → Doxygen, `/** ... */`. See `cpp.md` §3-3.
- **Python** → Sphinx, `""" ... """`, PEP 257. The closing `"""` sits alone on
  its own line with a blank line above it. See `python.md` §3-3.

```cpp
/// Get the value of a parameter by the given name, and return true if it was set.
/**
 * \param[in] name The name of the parameter to get.
 * \param[out] parameter The output storage for the parameter being retrieved.
 * \return true if the parameter was previously declared, otherwise false.
 */
RCLCPP_PUBLIC
bool
get_parameter(const std::string & name, rclcpp::Parameter & parameter) const;
```

---

## 8. Non-package files

- **`.gitignore`** — at the repository root; the ROBOTIS example covers C, C++,
  Python, Java, Android, CUDA, CMake, Qt.
- **`*.repos`** — ROS 2 uses `vcstool` with `.repos` (ROS 1 used `wstool` with
  `.rosinstall`). Also how CI resolves dependency packages.
- **`.travis.yml`** — CI configuration.

```yaml
services:
  - docker

language:
  - none

notifications:
  email:
    on_success: change
    on_failure: always
    recipients:
      - <maintainer>@robotis.com

branches:
  only:
    - master
    - develop

install:
  - git clone --quiet --depth 1 https://github.com/ROBOTIS-move/ros2ci.git .ros2ci
  - cp example.repos .ros2ci/additional_repos.repos

matrix:
  include:
    - script: .ros2ci/travis.bash nightly
```

---

## 9. Miscellaneous

- **9-1** ROS targets Linux, macOS **and** Windows. **Never call an OS-specific
  function.**
- **9-98** Lint: `ament_cpplint` for C++ packages, `ament_flake8` for Python
  packages, plus the rest of `ament_lint`.
- **9-99** Every file ends with a blank line.
