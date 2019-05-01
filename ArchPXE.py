import signal, time, importlib
from os import walk
from os.path import splitext, basename

from hashlib import sha512
from os import urandom

def _gen_uid():
	return sha512(urandom(256)).hexdigest()

__builtins__.__dict__['LEVEL'] = 5
__builtins__.__dict__['gen_uid'] = _gen_uid

__builtins__.__dict__['datastore'] = {
	'dhcp' : {
		'state' : 'off'
	},
	'machines' : {
		'default' : {
			'iso' : 'archlinux-2019.05.01.iso',
			'template' : 'awesome workstation',
			'desktop' : 'awesome',
			'web_browser' : 'chromium',
			'applications' : ['nemo', 'git', 'openssh']
		},
		'00:11:22:33:44:55' : {
			'iso' : 'CentOS-8-x86_64-DVD-1810.iso',
			'template' : 'kde workstation',
			'desktop' : 'kde',
			'web_browser' : 'firefox',
			'applications' : []
		},
		'00:22:33:44:55:66' : {
			'iso' : 'none'
		}
	},
	'configs' : {
		'iso' : {
			'none' : 'No ISO (PXE Off)',
			'archlinux-2019.05.01.iso' : 'ArchLinux 2019.05.01',
			'archlinux_unattended-08.04.2019.iso' : 'Arch Linux Unattended 08.04.2019',
			'CentOS-8-x86_64-DVD-1810.iso' : 'CentOS 8'
		},
		'template' : {
			'none' : 'No Template',
			'gnome workstation' : 'Gnome Workstaion',
			'kde workstation' : 'KDE Workstation',
			'awesome workstation' : 'Awesome Workstation'
		},
		'desktop' : {
			'awesome' : 'Awesome',
			'kde' : 'KDE',
			'gnome' : 'Gnome'
		},
		'web_browser' : {
			'chromium' : 'Chromium',
			'chrome' : 'Chrome',
			'firefox' : 'FireFox',
			'opera' : 'Opera'
		},
		'applications' : {
			'lollypop' : 'lollypop',
			'qemu' : 'Qemu',
			'git' : 'Git',
			'openssh' : 'OpenSSH',
			'nano' : 'nano',
			'nemo' : 'nemo',
			'wget' : 'wget',
			'sublime-text-dev' : 'Sublime'
		}
	}
}
__builtins__.__dict__['sockets'] = {}
__builtins__.__dict__['sessions'] = {}

__builtins__.__dict__['config'] = {
	'slimhttp' : {
		'web_root' : './web_content',
		'index' : 'index.html',
		'vhosts' : {
			'deployment.messages2.me' : {
				'web_root' : './depdendencies/archinstall/deployments',
				'index' : 'index.html'
			}
		}
	}
}

## Import sub-modules after configuration setup.
from dependencies.slimHTTP import slimhttpd
from dependencies.spiderWeb import spiderWeb

#openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365

def sig_handler(signal, frame):
	http.close()
	https.close()
	exit(0)

signal.signal(signal.SIGINT, sig_handler)

class pre_parser():
	def __init__(self, *args, **kwargs):
		self.parsers = {}

	def parse(self, client, data, headers, fileno, addr, *args, **kwargs):
		## This little bundle of joy just flushes the Python cache, imports a library by string and then reloads it just in case.
		## That library is then in charge of parsing all the incoming websocket data. Meaning, no need to restart the entire server
		## if the code changes in the websocket-parser.
		importlib.invalidate_caches()
		for root, folders, files in walk('./backend/'):
			for filename in files:
				filename = splitext(basename(filename))[0]
				if not filename in self.parsers:
					log('GH', 'core', f'Loading parser: backend.{filename}', level=5)
					self.parsers[filename] = importlib.__import__(f'backend.{filename}')
				log('GH', 'core', f'Reloading parser: backend.{filename}', level=10)
				importlib.reload(self.parsers[filename])
				yield self.parsers[filename].__dict__[filename].parser.parse(client, data, headers, fileno, addr, *args, **kwargs)
			break

websocket = spiderWeb.upgrader({'default' : pre_parser()})
http = slimhttpd.http_serve(upgrades={b'websocket' : websocket})
https = slimhttpd.https_serve(upgrades={b'websocket' : websocket}, cert='cert.pem', key='key.pem')

while 1:
	for handler in [http, https]:
		client = handler.accept()

		#for fileno, client in handler.sockets.items():
		for fileno, event in handler.poll().items():
			if fileno in handler.sockets: # If not, it's a main-socket-accept and that will occur next loop
				sockets[fileno] = handler.sockets[fileno]
				client = handler.sockets[fileno]
				if client.recv():
					resposne = client.parse()
					if resposne:
						try:
							client.send(resposne)
						except BrokenPipeError:
							pass
						client.close()