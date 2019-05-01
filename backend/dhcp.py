from hashlib import sha512
from os import urandom
from ast import literal_eval
import json

class parser():
	def parse(client, data, headers, fileno, addr, *args, **kwargs):
		if set(('action', 'resource')) <= data.keys():
			if data['resource'] == 'dhcp':
				if data['action'] == 'toggle':
					if datastore['dhcp']['state'] == 'on': datastore['dhcp']['state'] = 'off'
					elif datastore['dhcp']['state'] == 'off': datastore['dhcp']['state'] = 'on'
					
				return {**data, 'state' : datastore['dhcp']['state']}