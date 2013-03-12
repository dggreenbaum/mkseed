class generator:
	''''
	A generator for Debian preseed files.
	Args:
		address: The IP address of the soon to be installed machine.
		netmask: The subnet mask of the soon to be installed machine.
		gateway: The gateway of the soon to be installed machine.
		overrrides: kwargs that override default values for other fields.
			Values that can be overridden are:
			locale
			console_keymap
			nameserver
			domain
			mirror
			suite
			full_name
			username
			password_hash (MD5)
			timezone
			recipe (list of dicts)
				Required dict fields:
					min_size
					max_size
					priority
					method (format or swap)
					file_system
					bootable (boolean)
					mount (not defined for swap)
			packages (space separated additional packages)
			upgrade (none, safe-upgrade, full-upgrade)
	'''

	def __init__(self, address, netmask, gateway, **overrides):
		# Construct the default partitioning recipie.
		boot = {
			"min_size": 40,
			"max_size": 100,
			"priority": 50,
			"method": "format",
			"file_system": "ext3",
			"bootable": True,
			"mount": "/boot",
			}
		root = {
			"min_size": 500,
			"max_size": 1000000000,
			"priority": 10000,
			"method": "format",
			"file_system": "ext3",
			"mount": "/",
			}
		swap = {
			"min_size": 64,
			"max_size": "300%",
			"file_system": "linux-swap",
			"priority": 512,
			"method": "swap"
			}
		default_recipe = [boot, root, swap]

		# Other defaults.
		default = {
								"locale": "en_US",
								"console_keymap": "us",
								"nameserver": "8.8.8.8",
								"hostname": "default",
								"domain": "default.default",
								"mirror": "ftp.us.debian.org",
								"suite": "testing",
								"full_name": "Default User",
								"username": "default",
								# password: default
								# generate has with printf "default" | mkpasswd -s -m md5
								"password_hash": "$1$mjaWlAAd$efDQvOYTkqbinSrsobZwP.",
								"timezone": "US/Eastern",
								"recipe": default_recipe,
								"packages": "openssh-server",
								"upgrade": "full-upgrade"
							}
		default['address'] = address
		default['netmask'] = netmask
		default['gateway'] = gateway

		if overrides != None:
			for k, v in overrides.items():
				if k in default.keys():
					default[k] = v

		from jinja2 import Environment, PackageLoader
		env = Environment(loader=PackageLoader('mkseed', 'templates'))
		template = env.get_template('preseed.cfg.tpl')
		self.__template = template.render(**default)

	def print(self):
		'''
		Prints the generate preseed.cfg to the console.
		'''
		print(self.__template)

	def save(self, path):
		'''
		Writes the generated preseed.cfg to the provided path.
		'''
		try:
			f = open(path, 'w')
			f.write(self.__template)
			f.close()
		except IOError as e:
			print("Invalid path: ", e)

	def publish(self, host, user, passw, path):
		'''
		Publishes the generated preseed file via FTP.
		'''
		from ftplib import FTP
		import os
		self.save("/tmp/tmp_preseed.cfg")
		preseed = open("/tmp/tmp_preseed.cfg", 'rb')

		ftp = FTP(host, user, passw)
		ftp.storbinary('STOR ' + path, preseed)

		preseed.close()
		os.unlink("/tmp/tmp_preseed.cfg")
