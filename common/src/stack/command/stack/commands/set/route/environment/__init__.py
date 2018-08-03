# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import stack.commands
from stack.exception import ArgRequired, CommandError


class Command(stack.commands.EnvironmentArgumentProcessor,
	      stack.commands.set.command):
	"""
	Specifies an Environment for the given routes. Environments are
	used to add another level to attribute resolution. This is commonly
	used to partition a single Frontend into managing multiple clusters.
	
	<arg type='string' name='route' repeat='1'>
	One or more routes.
	</arg>

	<param type='string' name='environment' optional='0'>
	The environment name to assign to each route.
	</param>
	"""

	def run(self, params, args):

		(environment, ) = self.fillParams([
			('environment', None, True)
			])

		print('set route environment', environment)
		
		if not len(args):
			raise ArgRequired(self, 'route')

		if environment and environment not in self.getEnvironmentNames():
			raise CommandError(self, 'environment parameter not valid')

		for route in args:
			self.db.execute("""
				update global_routes set environment=
				(select id from environments where name=%s)
				where network=%s
				""", (environment, route))

