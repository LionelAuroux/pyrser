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

#ifndef __ASCIIPARSER__
#define __ASCIIPARSER__

#include <map>
#include <list>
#include <cstring>
#include "asciiParsePrimitives.h"

class AsciiParser : public AsciiParse
{
public:
	AsciiParser(const char* stream, const char* ignore = " \r\n\t")
	  : AsciiParse(stream, ignore)
	  {}

	~AsciiParser(void)
	  {}

	AsciiParser(const AsciiParser& src)
	  : __dTag(src.__dTag)
	  {}

	AsciiParser& operator=(const AsciiParser& src)
	  {
	    if (this != &src)
	      this->__dTag = src.__dTag;
	    return (*this);
	  }

	const char*	getStream(void) const
	  {
	    return _lstream.last().getStream();
	  }

	void		setTag(const char* tagName)
	  {
	    __dTag[tagName] = getIndex();
	  }

	const char*	getTag(const char* tagName) const
	  {
	    if (__dTag.find(tagName) != __dTag.end())
	      return strndup(&getStream()[getIndex()], __dTag[tagName]);
	    throw "unknown tag required.";
	  }

	const char*	getCTag(const char* tagName) const
	  {
	    if (__dTag.find(tagName) != __dTag.end())
	      return strndup(&getStream()[getIndex() + 1], __dTag[tagName] - 1);
	    throw "unknown tag required.";
	  }

private:
	std::map<const char*, int>	__dTag;
};

#endif /* __ASCIIPARSER__ */
