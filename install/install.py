from temod.storage.mysql import MysqlEntityStorage
from subprocess import Popen, PIPE, STDOUT
from pathlib import Path

import sys
import re
import os


DATABASE_NAME = "digiq"


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
	from uuid import uuid4 
	admin_privilege = AccountPrivilege(id=str(uuid4()), label="admin", roles="*")
	MysqlEntityStorage(AccountPrivilege,**credentials).create(admin_privilege)

	admin_user = User(id=str(uuid4()), username="admin", mdp="admin")
	MysqlEntityStorage(User,**credentials).create(admin_user)

	MysqlEntityStorage(UserAccount,**credentials).create(UserAccount(
		id=str(uuid4()),
		idU=admin_user['id'],
		idP=admin_privilege['id']
	))

	admin_quest = Quest(id=str(uuid4()), title="Admin Quest", description="This is a test quest")
	all_users_quest = Quest(id=str(uuid4()), title="All users Quest", description="")
	MysqlEntityStorage(Quest,**credentials).create(admin_quest, all_users_quest)

	admin_quest_task_0 = Task(id=str(uuid4()), quest=admin_quest['id'], task_order=0, content="admin task 1")
	admin_quest_task_1 = Task(id=str(uuid4()), quest=admin_quest['id'], task_order=1, content="admin task 2")

	all_users_quest_task_0 = Task(id=str(uuid4()), quest=all_users_quest['id'], task_order=0, content="all users task 1")
	all_users_quest_task_1 = Task(id=str(uuid4()), quest=all_users_quest['id'], task_order=1, content="all users task 2")
	all_users_quest_task_2 = Task(id=str(uuid4()), quest=all_users_quest['id'], task_order=2, content="all users task 3")

	MysqlEntityStorage(Task,**credentials).create(admin_quest_task_0, admin_quest_task_1, all_users_quest_task_0, all_users_quest_task_1, all_users_quest_task_2)

	admin_quest_key = ResourceKey(id=str(uuid4()), resource=admin_quest['id'], resource_type="quest", user=admin_user['id'], resource_key="rwx")
	all_users_quest_key = ResourceKey(id=str(uuid4()), resource=all_users_quest['id'], resource_type="quest", user=None, resource_key="rwx")
	MysqlEntityStorage(ResourceKey,**credentials).create(admin_quest_key, all_users_quest_key)

	MysqlEntityStorage(ActiveQuest,**credentials).create(ActiveQuest(user=admin_user['id'],quest=admin_quest['id']))




#INSERT into accountPrivilege(id, label, roles, editable) VALUES ("5442aeeb-b0d6-49da-9e36-76898c74091f", "admin", "*", 0);
#INSERT into user(id, username, mdp) VALUES ("1cc6a4f4-623c-40ce-8bc0-8a09ee499327", "Y2RuemFz", "NDBvdmVyNDAk");
#INSERT into userAccount(id, idU, idP) VALUES ("01d15a74-a43f-4cbf-ad8a-29ded8495c96", "1cc6a4f4-623c-40ce-8bc0-8a09ee499327", "5442aeeb-b0d6-49da-9e36-76898c74091f");


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
	cmd = create_mysql_cmd(credentials)

	print("Executing cmd:", cmd)
	p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
	with open(schema_path) as file:
		stdout_data = p.communicate(input=file.read())[0]

	install_preset_objects(credentials)
