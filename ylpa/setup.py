from distutils.core import setup
import py2exe
import sys
# dll_excludes = ['MSVCP90.dll']
#
# setup(
#     options={"py2exe": {"dll_excludes": dll_excludes}
#               },
#     windows=['ylpatest.py']
# )
from glob import glob
data_files = [("Microsoft.VC90.CRT", glob(r'i:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT\*.*'))]
sys.path.append(r'i:\Program Files\Microsoft Visual Studio 9.0\VC\redist\x86\Microsoft.VC90.CRT')

setup(
    data_files=data_files,
    windows=['ylpatest.py']
)
