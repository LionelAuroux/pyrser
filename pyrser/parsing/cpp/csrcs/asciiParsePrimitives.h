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

#ifndef __ASCIIPARSEPRIMITIVES__
#define __ASCIIPARSEPRIMITIVES__

#include <list>
#include <iostream>
#include "Stream.h"
#include "asciiParseContext.h"

class AsciiParse
{
public:
	AsciiParse(char*, char*, char*, char*, char*);
	~AsciiParse(void);
	AsciiParse(const AsciiParse&);
	AsciiParse& operator=(const AsciiParse&);

	inline bool		peekTextFrom(char* text, unsigned int index) const
	  {
	    size_t		len;
	    unsigned int	text_index;

	    len = strlen(text);
	    text_index = 0;
	    while (index != _eofPos() && text_index < len)
	      {
		if (_getCharAt(index) != text[text_index])
		  return (false);
		++index;
		++text_index;
	      }
	    if (text_index == len)
	      return (true);
	    return (false);
	  }

	inline void		readWs(void) const
	  {
	    while (readEOF() == false)
	      {
		if (!::strchr(getWsList(), _getChar()))
		  return;
		incPos();
	      }
	  }

	inline void		readIgnored(void) const
	  {
	    readWs();
	    if (readComment() == true)
	      readWs();
	  }

	inline bool		lineComment(void) const
	  {
	    if (peekText(this->_c_line))
	      {
		while (readEOF() == false && _getChar() != '\n')
		  incPos();
		return (true);
	      }
	    return (false);
	  }

	inline unsigned int	peekComment(unsigned int index) const
	  {
	    unsigned int	inner;

	    inner = 0;
	    while (index != _eofPos() )
	      {
		if (_getCharAt(index) == this->_c_end[0]
		    && peekTextFrom(this->_c_end, index))
		  {
		    this->_cur->incPos(\
			(index - getIndex()) + (unsigned int)::strlen(this->_c_end));
		    return (index);
		  }

		if (_getCharAt(index) == this->_c_begin[0]
		    && peekTextFrom(this->_c_begin, index))
		  {
		    index += (unsigned int)::strlen(this->_c_begin);
		    if ((inner = peekComment(index)) != 0)
		      index = inner;
		  }

		++index;
	      }
	    return 0;
	  }

	inline bool		readComment(void) const
	  {
	    int			index;

	    if (lineComment() == true)
	      return true;
	    if (peekText(this->_c_begin) == false)
	      return false;
	    index = getIndex() + (unsigned int)::strlen(this->_c_begin);
	    if (peekComment(index) != 0)
	      return true;
    	    std::cerr << "No comment close tag found." << std::endl;
	    return false;
	  }

	inline bool		peekChar(char c) const
	  {
	    return (_getChar() == c);
	  }

	inline bool		readChar(char c) const
	  {
	    readIgnored();
	    if (peekChar(c) == true)
	      {
		incPos();
		return (true);
	      }
	    return (false);
	  }

	inline bool		readAChar(void) const
	  {
	    readIgnored();
	    if ((getIndex() + 1)  < _eofPos())
	      {
		incPos();
		return (true);
	      }
	    return (false);
	  }

	inline bool		peekText(char* text) const
	  {
	    size_t		len;
	    unsigned int	text_index;
	    unsigned int	index;

	    len = strlen(text);
	    index = getIndex();
	    text_index = 0;
	    while (index != _eofPos() && text_index < len)
	      {
		if (_getCharAt(index) != text[text_index])
		  return (false);
		++index;
		++text_index;
	      }
	    return (text_index == len);
	  }

	inline char		lastRead(void) const
	  {
	    return _cur->lastRead();
	  }

	inline bool		readEOF(void) const
	  {
	    return (getIndex() == _eofPos());
	  }

	inline bool		readEOL(void)
	  {
	    readChar('\r');
	    if (readChar('\n'))
	      return (validContext());
	    restoreContext();
	    return (false);
	  }

	inline bool		readUntil(char c, char inhibitor) const
	  {
	    saveContext();
	    while (readEOF() == false)
	      {
		if (readChar(inhibitor) == true)
		  incPos();
		if (readChar(c) == true)
		  return (validContext());
		incPos();
	      }
	    restoreContext();
	    return (false);
	  }

	inline bool		readUntilEOF(void)
	  {
	    while (getIndex() != _eofPos())
	      incPos();
	    return (true);
	  }

	inline bool		readText(char* text)
	  {
	    size_t		len;
	    unsigned int	index;

	    len = strlen(text);
	    readIgnored();
	    saveContext();
	    for (index = 0; readEOF() == false && index < len; ++index)
	      {
		if (_getChar() != text[index])
		  {
		    restoreContext();
		    return (false);
		  }
		incPos();
	      }
	    if (index == len)
	      return (validContext());
	    restoreContext();
	    return (false);
	  }

	inline bool		readInteger(void)
	  {
	    readIgnored();
	    if (readEOF() == false && ::isdigit(_getChar()))
	      {
		incPos();
		while (readEOF() == false && ::isdigit(_getChar()))
		  incPos();
		return (true);
	      }
	    return (false);
	  }

	inline bool		readIdentifier(void)
	  {
	    readIgnored();
	    if (readEOF() == false
		&& (::isalpha(_getChar()) || peekChar('_')))
	      {
		incPos();
		while (readEOF() == false &&
		    (::isdigit(_getChar())
		     || ::isalpha(_getChar())
		     || peekChar('_')))
		  incPos();
		return (true);
	      }
	    return (false);
	  }

	inline bool		readRange(char begin, char end)
	  {
	    char		c;
	    bool		res;

	    readIgnored();
	    c = _getChar();
	    res = (c >= begin && c <= end);
	    if (res == true)
	      incPos();
	    return (res);
	  }

	inline bool		readCString(void)
	  {
	    saveContext();
	    if (readChar('\"') == true
		&& readUntil('\"', '\\') == true)
	      return (validContext());
	    restoreContext();
	    return (false);
	  }

	inline bool		readCChar(void)
	  {
	    saveContext();
	    if (readChar('\'') == true
		&& readUntil('\'', '\\') == true)
	      return (validContext());
	    restoreContext();
	    return (false);
	  }

	inline void		saveContext(void) const
	  {
	    _cur->saveContext();
	  }

	inline bool		restoreContext(void) const
	  {
	    _cur->restoreContext();
	    return (false);
	  }

	inline bool		validContext(void) const
	  {
	    _cur->validContext();
	    return (true);
	  }

	inline void		parsedStream(char* newStream, char* name, char* ignore)
	  {
	    _lstream.push_back(Stream(newStream, name, ignore));
	    _cur = &(_lstream.back());
	  }

	inline void		popStream(void)
	  {
	    _lstream.pop_back();
	    _cur = &(_lstream.back());
	  }

	inline void		setWsList(char* newWsList)
	  {
	    _cur->setWsList(newWsList);
	  }

	inline unsigned int	getIndex(void) const
	  {
	    return _cur->getIndex();
	  }

	inline unsigned int	getColumnNbr(void) const
	  {

	    return _cur->getColumnNbr();
	  }

	inline unsigned int	getLineNbr(void) const
	  {

	    return _cur->getLineNbr();
	  }

	inline unsigned int	getStreamLen(void) const
	  {
	    return _eofPos();
	  }

	inline char		getCurrentByte(void) const
	  {
	    return _getChar();
	  }

	inline const char*	getWsList(void) const
	  {
	    return _cur->getWsList();
	  }

	inline const char*	getName(void) const
	  {
	    return _cur->getName();
	  }

	inline const char*	getStream(void) const
	  {
	    return _cur->getStream();
	  }

	inline void		printStream(void) const
	  {
	    _cur->printStream();
	  }

	inline void		incPos(void) const
	  {
	    _cur->incPos();
	  }
private:
	inline char		_getCharAt(unsigned int index) const
	  {
	    return _cur->getCharAt(index);
	  }
	
	inline char		_getChar(void) const
	  {
	    return _cur->getChar();
	  }

	inline unsigned int	_eofPos(void) const
	  {
	    return _cur->eofPos();
	  }

	char*			_c_line;
	char*			_c_begin;
	char*			_c_end;
	Stream*			_cur;
	std::list<Stream>	_lstream;
};


#endif /* __ASCIIPARSEPRIMITIVES__ */
