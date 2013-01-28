"""
Temoa - Tools for Energy Model Optimization and Analysis
  linear optimization; least cost; dynamic system visualization

Copyright (C) 2011-2012  Kevin Hunter, Joseph DeCarolis

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU Affero General Public License as published by the Free
Software Foundation, either version 3 of the License, or (at your option) any
later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY
WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

Developers of this script will check out a complete copy of the GNU Affero
General Public License in the file COPYING.txt.  Users uncompressing this from
an archive may not have received this license file.  If not, see
<http://www.gnu.org/licenses/>.
"""

__all__ = ('pformat_results',)

from collections import defaultdict
from cStringIO import StringIO
from sys import stderr as SE

def pformat_results ( pyomo_instance, pyomo_result ):
	from coopr.pyomo import Objective, Var, Constraint

	instance = pyomo_instance
	result = pyomo_result

	soln = result['Solution']
	solv = result['Solver']      # currently unused, but may want it later
	prob = result['Problem']     # currently unused, but may want it later

	optimal_solutions = (
	  'feasible', 'globallyOptimal', 'locallyOptimal', 'optimal'
	)
	if str(soln.Status) not in optimal_solutions:
		return "No solution found."

	objs = instance.active_components( Objective )
	if len( objs ) > 1:
		msg = '\nWarning: More than one objective.  Using first objective.\n'
		SE.write( msg )

	# This awkward workaround so as to be generic.  Unfortunately, I don't
	# know how else to automatically discover the objective name
	obj_name = objs.keys()[0]
	try:
		obj_value = getattr(soln.Objective, obj_name).Value
	except AttributeError, e:
		try:
			obj_value = soln.Objective['__default_objective__'].Value
		except:
			msg = ('Unknown error collecting objective function value.  A '
			   'solution exists, but Temoa is currently unable to parse it.  '
			   'If you are inclined, please send the dat file that creates the '
			   'error to the Temoa developers.  Meanwhile, pyomo will still be '
			   'able to extract the solution.\n')
			SE.write( msg )
			raise

	Vars = soln.Variable
	Cons = soln.Constraint

	def collect_result_data( cgroup, clist, epsilon):
		# ctype = "Component group"; i.e., Vars or Cons
		# clist = "Component list"; i.e., where to store the data
		# epsilon = absolute value below which to ignore a result
		results = defaultdict(list)
		for name, data in cgroup.iteritems():
			if not (abs( data['Value'] ) > epsilon ): continue

			# name looks like "Something[some,index]"
			group, index = name[:-1].split('[')
			results[ group ].append( (name.replace("'", ''), data['Value']) )
		clist.extend( t for i in sorted( results ) for t in sorted(results[i]))

	var_info = list()
	con_info = list()

	collect_result_data( Vars, var_info, epsilon=1e-9 )
	collect_result_data( Cons, con_info, epsilon=1e-9 )

	def get_int_padding ( obj ):
		val = obj[ 1 ]         # obj is 2-tuple, defined within var_info
		return len(str(int(val)))
	def get_dec_padding ( obj ):
		val = abs(obj[ 1 ])    # obj is 2-tuple defined within con_info
		return len(str(val - int(val)))

	run_output = StringIO()

	msg = ( 'Model name: %s\n'
	   'Objective function value (%s): %s\n'
	   'Non-zero variable values:\n'
	)
	run_output.write( msg % (instance.name, obj_name, obj_value) )

	if len( var_info ) > 0:
		# This padding code is what makes the display of the output values
		# line up on the decimal point.
		int_padding = max(map( get_int_padding, var_info ))
		dec_padding = max(map( get_dec_padding, var_info ))
		format = "  %%%ds%%-%ds  %%s\n" % (int_padding, dec_padding)
			# Works out to something like "%8d%-11s  %s"

		for key, val in var_info:
			int_part = int(abs(val))
			dec_part = str(abs(val) - int_part)[1:]  # remove (negative and) 0
			if val < 0: int_part = "-%d" % int_part
			run_output.write( format % (int_part, dec_part, key) )

	else:
		run_output.write( '\nAll variables have a zero (0) value.\n' )

	if 0 == len( con_info ):
		# Since not all Coopr solvers give constraint results, must check
		msg = '\nSelected Coopr solver plugin does not give constraint data.\n'
		run_output.write( msg )
	else:
		msg = '\nBinding constraint values:\n'
		run_output.write( msg )

		int_padding = max(map( get_int_padding, con_info ))
		dec_padding = max(map( get_dec_padding, con_info ))
		format = "  %%%ds%%-%ds  %%s\n" % (int_padding, dec_padding)
			# Works out to something like "%8s%-11s  %s"

		for key, val in con_info:
			int_part = int(abs(val))
			dec_part = str(abs(val) - int_part)[1:]
			if val < 0: int_part = "-%d" % int_part
			run_output.write( format % (int_part, dec_part, key) )

	return run_output.getvalue()

