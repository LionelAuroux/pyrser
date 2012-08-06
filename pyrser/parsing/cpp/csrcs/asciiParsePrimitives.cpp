/*
** Copyright (C) 2012 Candiotti Adrien 
**
** This program is free software: you can redistribute it and/or modify
** it under the terms of the GNU General Public License as published by
** the Free Software Foundation, either version 3 of the License, or
** (at your option) any later version.
**
** This program is distributed in the hope that it will be useful,
** but WITHOUT ANY WARRANTY; without even the implied warranty of
** MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
**
** See the GNU General Public License for more details.
**
** You should have received a copy of the GNU General Public License
** along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <string.h>
#include <ctype.h>
#include "Stream.h"
#include "asciiParsePrimitives.h"

AsciiParse::AsciiParse\
  (char* stream, char* ignore, char* c_line, char* c_begin, char* c_end)
  : _c_line(c_line), _c_begin(c_begin), _c_end(c_end)
{
  _lstream.push_back(Stream(stream, "root", ignore));
  _cur = &(_lstream.back());
}

AsciiParse::~AsciiParse(void)
{
}

AsciiParse::AsciiParse(const AsciiParse& src)
  : _lstream(src._lstream)
{
  _cur = &(_lstream.back());
}

AsciiParse&	AsciiParse::operator=(const AsciiParse& src)
{
  if (this != &src)
    {
      _lstream = src._lstream;
      _cur = &(_lstream.back());
    }
  return (*this);
}

