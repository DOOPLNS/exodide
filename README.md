# exodide: build_ext for Pyodide

## 1. Overview

WARNING: This project is still under development, and doesn't work yet.

[Pyodide](https://pyodide.org/en/stable/index.html) is a WebAssembly
variant of [CPython](https://www.python.org/). By using it, we can run
Python code inside web browser.

Although we can run most of pure-Python packages on Pyodide, however,
C/C++-extension packages is limited to
[builtin packages](https://pyodide.org/en/stable/usage/packages-in-pyodide.html).

The motivation of this project (exodide) is providing C/C++-extension
builder for Pyodide, and enables users to run your own custom
C/C++-extension packages on Pyodide.

## 2. Usage

### 2.1 Prerequest
To build C/C++ to WebAssembly, you need
[Emscripten](https://emscripten.org/).

Since Pyodide is built with Python 3.10, we only prepare headers for
the version. Your custom package must run on Python 3.10.

### 2.2 Usage

```python:setup.py
from setuptools import setup
import exodide

# omit

setup(
    # omit
    cmdclass={"build_ext": exodide.build_ext},
)
```

then `CC=emcc CXX=em++ python setup.py bdist_wheel`.


Pyodide doesn't provide all the functionalities of CPython, so that
you might need to modify your package. You can detect Emscripten
compiler by `__EMSCRIPTEN__` macro ([ref](https://emscripten.org/docs/compiling/Building-Projects.html#detecting-emscripten-in-preprocessor)).

```cpp
#ifdef __EMSCRIPTEN__
// Code for Pyodide
#else
// Code for Others
#endif
```

## 3. LICENSEs

We utilize other projects and these codes obey their original lisences.
We distribute patched header files of CPython and NumPy, too.

* CPython: https://www.python.org/
  * `cpython` directory
  * [PYTHON SOFTWARE FOUNDATION LICENSE VERSION 2](https://github.com/python/cpython/blob/main/LICENSE)
* NumPy: https://numpy.org/
  * `numpy` directory and `script/code_generators` directory
  * [BSD 3-Clause](https://github.com/numpy/numpy/blob/main/LICENSE.txt)
* Pyodide: https://pyodide.org/en/stable/
  * `pyodide` directory
  * [MPL-2.0](https://github.com/pyodide/pyodide/blob/main/LICENSE)
* Others (exodide original codes)
  * MIT


## 4. Trial & Error

### `error: "LONG_BIT definition appears wrong for platform (bad gcc/glibc config?)."`


### `SIZEOF_VOID_P` is not equal to `sizeof(void*)`



### Solved: `__multiarray_api.h` and `__ufunc_api.h` are missing.

They are auto generated headers. We copied
`numpy/numpy/core/code_generators` codes and modified them to work
stand-alone.


### Solved: `NPY_API_VERSION` and `NPY_ABI_VERSION` are not defined.

In ordinary build, these are defined at `_numpyconfig.h`, but Pyodide
provides custom `_numpyconfig.h` without these definitions.

We manually extract the original definitions (aka. `C_API_VERSION` and
`C_ABI_VERSION`) from `numpy/numpy/core/setup_common.py` and append
them to `_numpyconfig.h`