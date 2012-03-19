"""
    TEMOA (Tools for Energy Model Optimization and Analysis) 
    Copyright (C) 2010 TEMOA Developer Team 

    This file is part of TEMOA.
    TEMOA is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    any later version.

    TEMOA is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with TEMOA.  If not, see <http://www.gnu.org/licenses/>.
"""


def SliceSet_Init ( model ):
	ans = []
	ans.extend( [ i for i in model.b_slice ] ) # base
	ans.extend( [ i for i in model.s_slice ] ) # shoulder
	ans.extend( [ i for i in model.p_slice ] ) # peak

	return ans

