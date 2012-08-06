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

class Singleton(type):
      """
      A (justified) singleton metaclass.
      """
      __dInstances = {}
      def __call__(oCls, *args, **kwargs):
	  if oCls.__name__ not in oCls.__dInstances.keys():
	    oCls.__dInstances[oCls.__name__]\
		= super(Singleton, oCls).__call__(*args, **kwargs)
	  return oCls.__dInstances[oCls.__name__]
