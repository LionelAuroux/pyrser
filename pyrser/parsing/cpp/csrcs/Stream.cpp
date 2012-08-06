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

#include "asciiParseContext.h"
#include "Stream.h"

Stream::Stream(const char* string, const char* name, char* ignore)
  : _neofpos(::strlen(string)),
    _ct(0),
    _pyObject(PyString_FromString(string)),
    _sstream(PyString_AsString(_pyObject)),
    _sname(name)
{
  ctxt		first;

  first._nIndex = 0;
  first._nCol = 1;
  first._nLine = 1;
  first._swslist = ignore;

  _aContext.push_back(first);
  _ct = &(_aContext.back());
}

Stream::~Stream()
{
  ;
}

Stream::Stream(const Stream& src)
  : _neofpos(src._neofpos),
  _sstream(src._sstream),
  _sname(src._sname),
  _aContext(src._aContext)
{
  _ct = &(_aContext.back());
}

Stream&	Stream::operator=(const Stream& src)
{
  if (this != &src)
    {
      _neofpos = src._neofpos;
      _sstream = src._sstream;
      _sname = src._sname;
      _aContext = src._aContext;
      _ct = &(_aContext.back());
    }
  return (*this);
}
