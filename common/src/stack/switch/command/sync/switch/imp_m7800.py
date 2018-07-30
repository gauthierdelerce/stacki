# @copyright@
# Copyright (c) 2006 - 2018 Teradata
# All rights reserved. Stacki(r) v5.x stacki.com
# https://github.com/Teradata/stacki/blob/master/LICENSE.txt
# @copyright@

import shlex
from operator import itemgetter
from collections import namedtuple

IfInfo = namedtuple('IfInfo', ['host', 'interface', 'network', 'mac', 'ip', 'options'])

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
			try:
				s.add_partition(partition, val)
			except SwitchException as e:
				msg = f'Error while attempting to add partition "{partition}" to {switch} with pkey "{val}":\n{e}'
				raise CommandError(self.owner, msg)

		lst_host_iface = self.owner.call('list.host.interface')

		iface_getter = itemgetter('host', 'interface', 'network', 'mac', 'ip', 'options')

		# for backend nodes, we're looking for 'ibpartition' specified in the 'options' field of ibN ifaces
		for row in lst_host_iface:
			iface = IfInfo(*iface_getter(row))

			if iface.options is None:
				# no partition info set
				continue
			if 'ibpartition=' not in iface.options:
				# no partition info set
				continue
			if not iface.interface.startswith('ib'):
				# not an ib iface
				continue
			if not iface.mac:
				# no guid
				continue

			opts = shlex.split(iface.options)
			part_info = next(opt.split('=') for opt in opts if opt.startswith('ibpartition='))
			try:
				# error or ignore?
				partition = '0x%04d' % int(part_info[1])
			except:
				continue

			if partition not in s.partitions:
				# partition specified but doesn't exist on switch
				continue

			s.add_partition_member(partition, iface.mac)
			s.add_partition_member('Default', iface.mac)


