"""
exodide.build module

This module provides functionalities
to build C/C++ extension package for Pyodide.
"""

import os
import sys
from typing import Dict, List
from unittest import mock

from distutils.cmd import Command
from distutils.command.build import build as _build
from setuptools.command.build_ext import build_ext as _build_ext
from wheel.bdist_wheel import bdist_wheel as _bdist_wheel

def system_include() -> str:
    """
    Get system include directory

    Returns
    -------
    str
        Include directory of host Python
    """
    return os.path.join(sys.prefix, "include", "python")


def exodide_include() -> List[str]:
    """
    Get exodide include directories

    Returns
    -------
    list of str
        Include directories in exodide package
    """
    dirname = os.path.dirname(__file__)
    return [os.path.join(dirname, "cpython"),
            os.path.join(dirname, "numpy")]


def adjust_include(include: List[str]) -> List[str]:
    """
    Adjust include list

    Parameters
    ----------
    include : list of str
        Original include directories

    Returns
    -------
    list of str
        Adjusted include directories
    """
    s = system_include()
    return exodide_include() + [I for I in include if (s not in I)]


def exodide_links() -> List[str]:
    """
    Get exodide link args

    Returns
    -------
    list of str
        Link arguments for exodide
    """
    return ["-s", "MODULARIZE=1",
            "-s", "LINKABLE=1",
            "-s", "EXPORT_ALL=1",
            "-s", "WASM=1",
            "-s", "LZ4=1",
            "-s", "WASM_BIGINT",
            "-s", "SIDE_MODULE=1"]


def exodide_prohibited_links() -> List[str]:
    """
    Get exodide prohibit link args

    Returns
    -------
    list of str
        Prohibited link arguments for exodide
    """
    return ["-shared", "-pthread"]


def plat_name() -> str:
    """
    Platform name tag for wheel

    Returns
    -------
    str
        platform tag
    """
    return "emscripten-wasm32"


class build(_build):
    def finalize_options(self):
        with mock.patch("distutils.command.build.get_platform") as get_platform:
            get_platform.return_value = plat_name()
            return super().finalize_options()


class build_ext(_build_ext):
    def run(self):
        self.include_dirs = adjust_include(self.include_dirs)

        for ext in self.extensions:
            ext.extra_link_args = ext.extra_link_args + exodide_links()
        return super().run()

    def build_extensions(self):
        self.compiler.linker_so = [so for so in self.compiler.linker_so
                                   if (so not in ["-shared", "-pthread"])]
        return super().build_extensions()

    def get_ext_filename(self, ext_name):
        ext_path = ext_name.split('.')
        return os.path.join(*ext_path) + ".cpython-310-wasm32-emscripten.so"


def cmdclass() -> Dict[str, Command]:
    return {"build": build,
            "build_ext": build_ext}
