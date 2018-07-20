# @copyright@
# Copyright (c) 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from itertools import groupby
from operator import itemgetter

import stack.commands
from stack.exception import CommandError

class Command(stack.commands.SwitchArgumentProcessor,
	      stack.commands.add.switch.command):
	"""
	Add an infiniband partition to a switch

	<arg type='string' name='switch'>
	Name of the switch
	</arg>

	<param type='string' name='partition' optional='0'>
	The name of the infiniband partition
	</param>

	<param type='string' name='key' optional='0'>
	The key of the infiniband partition
	</param>

	<example cmd='add switch partition infiniband-3-12 partition=0017 key=0x0017'>
	Add partition '0017' with partition key '0x0017' to switch 'infiniband-3-12'
	</example>
	"""

	def run(self, params, args):

		partition, key = self.fillParams([
			('partition', None, True),
			('key', None, True),
		])

		switches = self.getSwitchNames(args)

		# TODO ignore fabrics for now.
#		lst_host_iface = stack.api.Call('list.host.interface', ['a:switch']
#		switch_ifaces = {sw: list(ifaces) for sw, ifaces in groupby(lst_host_iface, itemgetter('host'))}

		mlnx_sm_matcher = itemgetter('ib subnet manager', 'make', 'model')
		lst_switch = self.call('list.switch', [*switches, 'expanded=True'])
		subnet_managers = [sw['switch'] for sw in lst_switch if mlnx_sm_matcher(sw) == (True, 'Mellanox', 'm7800')]

		for sm in subnet_managers:
			# fake database table for now
			self.call('set.host.attr', [sm, f'attr=partition.name.{key}', f'value={partition}'])
