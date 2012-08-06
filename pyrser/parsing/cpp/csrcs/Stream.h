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

#ifndef __STREAM__
#define __STREAM__

#include <vector>
#include <iostream>
#include "Python.h"
#include "asciiParseContext.h"

class Stream
{
public:
	Stream(const char*, const char*, char*);
	~Stream();
	Stream(const Stream&);
	Stream& operator=(const Stream&);
	inline void	saveContext(void)
	  {
	    _aContext.push_back(*_ct);
	    _ct = &(_aContext.back());
	  }

	inline void		restoreContext(void)
	  {
	    _aContext.pop_back();
	    _ct = &(_aContext.back());
	  }

	inline void		validContext(void)
	  {
	    size_t nElem = _aContext.size();

	    if (nElem < 2)
	      std::cerr << "CONTEXT ERROR" << std::endl;

	    // copy the last wsList
	    _aContext.back()._swslist =\
	      _aContext[nElem - 2]._swslist;

	    _aContext[nElem - 2] = _aContext.back();
	    _aContext.pop_back();
	    if (_aContext.size() == 0)
	      std::cerr << "CONTEXT ERROR" << std::endl;
	    _ct = &(_aContext.back());
	  }

	inline void		setWsList(char* newWsList)
	  {
	    _ct->_swslist = newWsList;
	  }

	inline char*		getWsList(void) const
	  {
	    return _ct->_swslist;
	  }

	inline unsigned int	getIndex(void) const
	  {
	    return this->_ct->_nIndex;
	  }

	inline void		incPos(void)
	  {
	    if (getChar() == '\n')
	      {
		_ct->_nLine = _ct->_nLine + 1;
		_ct->_nCol = 0;
	      }
	    _ct->_nCol = _ct->_nCol + 1;
	    _ct->_nIndex = _ct->_nIndex + 1;
	  }

	inline void		incPos(unsigned int inc)
	  {
	    unsigned int	index;

	    index = 0;
	    while (index < inc)
	      {
		incPos();
		++index;
	      }
	  }

	inline char		getChar(void) const
	  {
	    return _sstream[_ct->_nIndex];
	  }

	inline char		getCharAt(unsigned int index) const
	  {
	    return _sstream[index];
	  }

	inline unsigned int	eofPos(void) const
	  {
	    return _neofpos;
	  }

	inline unsigned int	getColumnNbr(void) const
	  {
	    return _ct->_nCol;
	  }

	inline unsigned int	getLineNbr(void) const
	  {
	    return _ct->_nLine;
	  }

	inline const char* 	getName(void) const
	  {
	    return _sname;
	  }

	inline char 		lastRead(void) const
	  {
	    if (_ct->_nIndex > 0)
	      return _sstream[_ct->_nIndex - 1];
	    return _sstream[0];
	  }

	inline const char* 	getStream(void) const
	  {
	    return _sstream;
	  }

	inline void		printStream(void) const
	  {
	    for (unsigned int nIndex = 0; _sstream[nIndex] != '\0'; ++nIndex)
	      {
		if (_sstream[nIndex] >= 0 && _sstream[nIndex] <= 32)
		  printf("0x%x", _sstream[nIndex]);
		else
		  printf("%c", _sstream[nIndex]);
	      }
	    printf("\n");
	  }

private:
	unsigned int		_neofpos;
	ctxt*			_ct;
	PyObject*		_pyObject;
	const char*		_sstream;
	const char*		_sname;
	std::vector<ctxt>	_aContext;
};


#endif /* __STREAM__ */
