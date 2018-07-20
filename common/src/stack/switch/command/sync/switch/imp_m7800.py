# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

from operator import itemgetter
from collections import namedtuple

IfInfo = namedtuple('IfInfo', ['host', 'interface', 'network', 'mac', 'ip', 'vlan'])

import stack.commands
from stack.exception import CommandError
from stack.switch import SwitchException
from stack.switch.m7800 import SwitchMellanoxM7800


class Implementation(stack.commands.Implementation):
	def run(self, args):
		switch = args[0]['host']

		switch_attrs = self.owner.getHostAttrDict(switch)

		kwargs = {
			'username': switch_attrs[switch].get('username'),
			'password': switch_attrs[switch].get('password'),
		}

		# remove username and pass attrs (aka use any pylib defaults) if they aren't host attrs
		kwargs = {k:v for k, v in kwargs.items() if v is not None}

		s = SwitchMellanoxM7800(switch, **kwargs)
		s.connect()
		if not s.subnet_manager:
			return

		for attr, val in switch_attrs[switch].items():
			if not attr.startswith('partition.name.'):
				continue

			partition = attr.lstrip('partition.name.')
			if partition in s.partitions:
				continue
			s.add_partition(partition, val)

		# assume an ibN iface with a VLAN is its partition, unless it has an IP addr, too?
		# which guid gets added?
		lst_host_iface = self.owner.call('list.host.interface')

		iface_getter = itemgetter('host', 'interface', 'network', 'mac', 'ip', 'vlan')

		for row in lst_host_iface:
			iface = IfInfo(*iface_getter(row))
			print(iface)

			if iface.vlan is None:
				# no partition info set
				continue
			if not iface.interface.startswith('ib'):
				# not an ib iface
				continue
			if iface.ip:
				# you're using ipoib...
				continue
			if not iface.mac:
				# no guid
				continue

			partition = '0x%04d' % iface.vlan
			print(partition)
			print(s.partitions)
			if partition not in s.partitions:
				print('not in partitions')
				# partition specified but doesn't exist on switch
				continue

			print('yay')
			s.add_partition_member(partition, iface.mac)


