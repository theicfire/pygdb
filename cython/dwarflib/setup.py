from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

setup(
    ext_modules = cythonize([
        Extension("use_dwarf", ["use_dwarf.pyx"],
            # Eww, ordering of libs not arbitrary!
            libraries=["dwarf_get_func_addr", "dwarf", "elf"])])
)
