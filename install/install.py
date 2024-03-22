from temod.storage.mysql import MysqlEntityStorage
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path
from uuid import uuid4 

import mysql.connector
import sys
import re
import os


DATABASE_NAME = "digiq"
APP_VERSION = "0.0.0"


def print_decorated_title(title):
    decoration = '*' * (len(title) + 9)
    print(decoration)
    print("*" * 4 + "-" * (len(title) + 2) + "*" * 4)
    print("*  " + decorate_text(title) + " *")
    print("*" * 4 + "-" * (len(title) + 2) + "*" * 4)
    print(decoration)

def decorate_text(text):
    decorated_text = ''
    for char in text:
        if char.isalpha():
            decorated_text += char.upper() if char.islower() else char.lower()
        else:
            decorated_text += char
    return decorated_text


def is_valid_hostname(hostname):
	if hostname == "localhost":
		return True
	ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
	if re.match(ip_pattern, hostname):
		return True
	return False


def get_mysql_credentials():
	while True:
		host = input("Enter you mysql host (default localhost):")
		if host == "" or host == "localhost":
			host = "127.0.0.1"
		if is_valid_hostname(host):
			break
		print(f"Invalid host: {host}")

	while True:
		try:
			port = input("Enter you mysql port (default 3306):")
			if port == "":
				port = 3306
			port = int(port)
			if port >= 1024 and port <= 49151:
				break
			print(f"Invalid port (must be between 1024 and 49151)")
		except:
			print(f"Invalid port")

	user = input("Enter you mysql user: ")
	password = input("Enter you mysql password:")

	if user == "":
		user = None
	if password == "":
		password == None

	return {"host":host,"port":port, "user":user, "password":password, "database": DATABASE_NAME}


def search_existing_database(credentials):
	try:
		connexion = mysql.connector.connect(**credentials)
	except Exception as exc:
		print("Can't connect to the specified database using these credentials. Verify the credentials and the existence of the database.")
		print(exc)
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
	print_decorated_title("! DANGER")
	print("The specified database already exists and is not empty. This installation script will erase all the database content and overwrite it with a clean one.")
	rpsn = input("Continue the installation (y/*) ?").lower()
	return rpsn == "y"


def create_mysql_cmd(credentials):
	cmd = ["mysql"]
	if credentials['host'] and not (credentials['host'] in ['127.0.0.1',"localhost"]):
		cmd.extend(["-h",credentials['host']])
	if credentials['port'] and credentials['port'] != 3306:
		cmd.extend(["-P",str(credentials['port'])])
	if credentials['user']:
		cmd.extend(["-u",credentials['user']])
	cmd.extend([credentials['database']])
	if credentials['password']:
		cmd.extend([f"-p{credentials['password']}"])
	return cmd

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


if __name__ == "__main__":
	import pprinter

	cpath = Path(os.path.realpath(__file__))
	schema_path = os.path.join(cpath.parent, "storages", "dbscheme.sql")
	if not os.path.isfile(schema_path):
		print("DB schema file not found at",schema_path)
		sys.exit()

	try:
		from core.entity import *
	except:
		core_path = os.path.join(cpath.parent.parent)
		sys.path.insert(0,core_path)
		from core.entity import *	

	credentials = get_mysql_credentials()

	already_created = search_existing_database(credentials)
	if already_created:
		if not confirm_database_overwrite():
			print("If you which to just update the app, run the script install/update.py")
			sys.exit(1)

	cmd = create_mysql_cmd(credentials)

	print("Executing cmd:", cmd)
	p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
	with open(schema_path) as file:
		stdout_data = p.communicate(input=file.read())[0]

	install_preset_objects(credentials)
