from temod.storage.mysql import MysqlEntityStorage
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from uuid import uuid4 

import sys
import os

if not os.getcwd() in sys.path:
	sys.path.append(os.getcwd())

from install import common_funcs
from core.entity import *

import mysql.connector
import traceback
import argparse
import toml
import re


APP_VERSION = "1.0.5"


def search_existing_database(credentials):
	try:
		connexion = mysql.connector.connect(**credentials)
	except:
		LOGGER.error("Can't connect to the specified database using these credentials. Verify the credentials and the existence of the database.")
		LOGGER.error(traceback.format_exc())
		sys.exit(1)

	cursor = connexion.cursor()
	cursor.execute('show tables;')

	try:
		return len(cursor.fetchall()) > 0
	except:
		raise
	finally:
		cursor.close()
		connexion.close()


def confirm_database_overwrite():
	print(); common_funcs.print_decorated_title("! DANGER"); print()
	LOGGER.info("The specified database already exists and is not empty. This installation script will erase all the database content and overwrite it with a clean one.")
	rpsn = input("Continue the installation (y/*) ?").lower()
	return rpsn == "y"


def install_preset_objects(credentials):	
	digiquest = DigiQuest(version=APP_VERSION)
	MysqlEntityStorage(DigiQuest,**credentials).create(digiquest)

	admin_privilege = AccountPrivilege(id=str(uuid4()), label="admin", roles="*")
	MysqlEntityStorage(AccountPrivilege,**credentials).create(admin_privilege)

	admin_user = User(id=str(uuid4()), username="admin", mdp="admin")
	MysqlEntityStorage(User,**credentials).create(admin_user)

	MysqlEntityStorage(UserAccount,**credentials).create(UserAccount(
		id=str(uuid4()),
		idU=admin_user['id'],
		idP=admin_privilege['id']
	))

	MysqlEntityStorage(Job,**credentials).create(Job(
		name="GsyncJob",
		state="IDLE"
	))

def install_digiq_services(root_path, virtual_env, logging_dir, services_dir):
	# Install synchronizer
	with open(os.path.join(root_path,"tools","synchronizer","digiq.service")) as file:
		service = file.read()
	service = service.replace("$user", os.getlogin())
	service = service.replace("$script_path", os.path.join(root_path,"tools","synchronizer","synchronize.sh"))
	if virtual_env is not None:
		service = service.replace("$venv_path", f'-v "{os.path.join(virtual_env,"bin","activate")}"')
	else:
		service = service.replace("$venv_path", "")
	if logging_dir is not None:
		service = service.replace("$logging_dir", f'-l "{logging_dir}"')
	else:
		service = service.replace("$logging_dir", "")
	try:
		with open(os.path.join(services_dir,"digiq.service"),"w") as file:
			file.write(service)
		with open(os.path.join(services_dir,"digiq.timer"),"w") as file:
			with open(os.path.join(root_path,"tools","synchronizer","digiq.timer"),"r") as ofile:
				file.write(ofile.read())
	except:
		LOGGER.error(f"Unable to save digiq.service file in directory {services_dir}. You can either install the files in another directory with 'install.py -s [DIRECTORY]' or give enough rights to the install script.")
		LOGGER.error("Trace of the exception: ")
		LOGGER.error(traceback.format_exc())
		return False
	return True


def get_domain_name():
	domain_name = None
	while domain_name is None:
		domain_name = input("Enter the domain name of the app (Ex: digiq.mydomain.com). Leave empty to set it to localhost.")
		if domain_name == "":
			domain_name = "127.0.0.1"
		rpsn = input(f"App's domain name is {domain_name} ? (y/*)").lower()
		if rpsn != "y":
			domain_name = None
	return domain_name


def setup(app_paths, args):

	virtual_env = common_funcs.detect_virtual_env(app_paths['root'])
	logging_dir = args.logging_dir if not args.quiet else None
	if not install_digiq_services(app_paths['root'], virtual_env, logging_dir, args.services_dir):
		return False

	credentials = common_funcs.get_mysql_credentials()
	domain_name = get_domain_name()

	already_created = search_existing_database(credentials)
	if already_created:
		if not confirm_database_overwrite():
			LOGGER.warning("If you which to just update the app, run the script install/update.py")
			return False

	with open(app_paths['mysql_schema_file']) as file:
		if not common_funcs.execute_mysql_script(credentials, file.read().replace("$database",credentials['database'])):
			return False

	template_config = common_funcs.load_toml_config(app_paths['template_config_file'])
	template_config['storage']['credentials'].update(credentials)
	template_config['app']['blueprints']['google_services']['domain_name'] = domain_name
	common_funcs.save_toml_config(template_config, app_paths['config_file'])

	install_preset_objects(credentials)

if __name__ == "__main__":

	print("\n"); width = common_funcs.print_pattern("DigiQuest"); print(); print("#"*width); print()

	parser = argparse.ArgumentParser(prog="Synchronizes DigQuest events with external apps")
	parser.add_argument('-l', '--logging-dir', 
		help='Directory where log files will be stored', default=os.path.join("/","var","log","digiq")
	)
	parser.add_argument('-s', '--services-dir', 
		help='Directory where digiq service files will be stored', default=os.path.join("/","lib","systemd","system")
	)
	parser.add_argument('-q', '--quiet', action="store_true", help='No logging', default=False)
	args = parser.parse_args()

	setattr(__builtins__,'LOGGER', common_funcs.get_logger(args.logging_dir, quiet=args.quiet))
	app_paths = common_funcs.get_app_paths(Path(os.path.realpath(__file__)).parent)

	if not os.path.isfile(app_paths['mysql_schema_file']):
		LOGGER.error("DB schema file not found at",app_paths['mysql_schema_file'])
		sys.exit(1)

	if not os.path.isfile(app_paths['template_config_file']):
		LOGGER.error("Config template file not found at",app_paths['template_config_file'])
		sys.exit(1)

	if setup(app_paths, args):
		LOGGER.info("DigiQuests setup completed successfully")
	else:
		LOGGER.error("Error while installing DigiQuests")
		exit(1)