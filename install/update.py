from temod.storage.mysql import MysqlEntityStorage
from subprocess import Popen, PIPE, STDOUT
from packaging import version
from pathlib import Path
from uuid import uuid4 

import importlib.machinery
import mysql.connector
import pprinter
import logging
import sys
import re
import os


ALL_VERSIONS = ["0.0.0","1.0.0"]
LATEST_VERSION = "1.0.0"


def get_logger():
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)

	handler = logging.StreamHandler(sys.stdout)
	handler.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
	handler.setFormatter(formatter)
	logger.addHandler(handler)

	return logger


def get_mysql_credentials():
	while True:
		host = input("Enter you mysql host (default localhost):")
		if host == "" or host == "localhost":
			host = "127.0.0.1"
		if is_valid_hostname(host):
			break
		logger.warning(f"Invalid host: {host}")

	while True:
		try:
			port = input("Enter you mysql port (default 3306):")
			if port == "":
				port = 3306
			port = int(port)
			if port >= 1024 and port <= 49151:
				break
			logger.warning(f"Invalid port (must be between 1024 and 49151)")
		except:
			logger.warning(f"Invalid port")

	user = input("Enter your mysql user: ")
	password = input("Enter your mysql password:")
	database = input("Enter your mysql database name:")

	if user == "":
		user = None
	if password == "":
		password == None

	print("\n\n"+"*"*20)
	print("Database: ")
	print(f"ip = {host}:{port}")
	print(f"user = {user}")
	print(f"password = {password}")
	print(f"database = {database}")
	rspn = input("confirm ? (y/*)").lower()
	if rspn == "y":
		return {"host":host,"port":port, "user":user, "password":password, "database": database}
	print()
	return get_mysql_credentials()


def is_valid_hostname(hostname):
	if hostname == "localhost":
		return True
	ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
	if re.match(ip_pattern, hostname):
		return True
	return False


def detected_installed_version(credentials):	
	digiquest = list(MysqlEntityStorage(DigiQuest,**credentials).list())[0]
	return digiquest['version']


def update_from_version(version, credentials):
	cpath = Path(os.path.realpath(__file__))
	script = os.path.join(cpath.parent,"updates",f"update.{version}.py")
	if not os.path.isfile(script):
		logger.error(f"Update script from version {version} not found.")
		return

	loader = importlib.machinery.SourceFileLoader(f'upd_{version.replace(".","_")}', script)
	mod = loader.load_module()

	return mod.launch_update(credentials)


if __name__ == "__main__":

	print("\n"); width = pprinter.print_pattern("DigiQuest UPDATE"); print(); print("#"*width); print()

	logger = get_logger()

	cpath = Path(os.path.realpath(__file__))
	updates_dir = os.path.join(cpath.parent, "updates")
	if not os.path.isdir(updates_dir):
		logger.error("Updates scripts not found at ",updates_dir)
		sys.exit(1)

	try:
		from core.entity import *
	except:
		sys.path.insert(0,str(cpath.parent.parent))
		from core.entity import *	

	credentials = get_mysql_credentials()

	ALL_VERSIONS = sorted(ALL_VERSIONS, key=lambda x:version.parse(x))
	dgq_version = detected_installed_version(credentials)
	if dgq_version == ALL_VERSIONS[-1]:
		logger.info(f"DigiQuest is already at the lastest version {dgq_version}")
		sys.exit()

	logger.info(f"DigiQuest installed version detected: {dgq_version}")
	rspn = input("Update to latest version 1.0.0 ? (y/*)").lower()
	to_version = LATEST_VERSION
	if rspn != "y":
		rspn = input("Update to a specific version ? (y/*)").lower()
		if rspn != "y":
			logger.info("Exiting update script.")
			sys.exit()
		to_version = input("To which version do you want to update ?")

	if not to_version in ALL_VERSIONS:
		logger.error(f"Version {version} not found. Available versions are {', '.join(ALL_VERSIONS)}.")
		sys.exit(1)

	while dgq_version != to_version:

		if not update_from_version(dgq_version, credentials):
			sys.exit(1)

		new_version = detected_installed_version(credentials)
		if new_version == dgq_version:
			logger.error(f"Update from version {dgq_version} most likely failed. Detected version hasn't changed.")
			sys.exit(1)

		logger.info(f"Version updated succesfully from {dgq_version} to {new_version}")
		new_version = dgq_version

