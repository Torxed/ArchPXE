from hashlib import sha512
from os import urandom
from ast import literal_eval
import json
class parser():
	def parse(client, data, headers, fileno, addr, *args, **kwargs):
		if set(('action', 'resource')) <= data.keys():
			if data['action'] == 'retrieve' and data['resource'] == 'machinelist':
				return {**data, 'result' : datastore['machines']}