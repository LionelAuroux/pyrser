# Copyright (C) 2012 Candiotti Adrien
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
from os.path import abspath
from os import chdir

compilePath = abspath('.') + "/pyrser/parsing/cpp/"

asciiParse = Extension('asciiParse',
                       include_dirs=['/usr/include', '/usr/local/include',
                                     compilePath, compilePath + "csrcs"],
                       sources=
                       [
                       compilePath + 'asciiParse.pyx',
                       compilePath + 'csrcs/asciiParsePrimitives.cpp',
                       compilePath + 'csrcs/Stream.cpp'
                       ],
                       # Uncomment to add GDB debug symbols.
                       extra_compile_args=["-g3"],
                       extra_link_args=["-g3"],
                       language="c++")

setup(
    cmdclass={'build_ext': build_ext},
    ext_modules=[
        asciiParse
    ]
)
