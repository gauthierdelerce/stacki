# @rocks@
# Copyright (c) 2000 - 2010 The Regents of the University of California
# All rights reserved. Rocks(r) v5.4 www.rocksclusters.org
# https://github.com/Teradata/stacki/blob/master/LICENSE-ROCKS.txt
# @rocks@

import stack.commands


class Command(stack.commands.list.command):
	"""
	List the global routes.

	<example cmd='list route'>
	Lists all the global routes for this cluster.
	</example>
	"""

	def run(self, params, args):

		self.beginOutput()
		
		routes = self.db.select("""network, netmask, gateway, subnet, environment
			from global_routes""")
		for network, netmask, gateway, subnet, environment in routes:
			if subnet:
				rows = self.db.execute("""select name from
					subnets where id = %s""" % subnet)
				if rows == 1:
					gateway, = self.db.fetchone()
			if environment:
				environment, = self.db.select("""name from environments
								where id = %s""", ([environment]))
				environment = ', '.join(environment)

			self.addOutput(network, (netmask, gateway, environment))

		self.endOutput(header=['network', 'netmask', 'gateway', 'environment'],
			trimOwner=0)

