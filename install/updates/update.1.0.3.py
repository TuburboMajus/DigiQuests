from temod.storage.mysql import MysqlEntityStorage
from core.entity import UserGCalendar

import os

MYSQL_CMD = """
ALTER TABLE event ADD reminder int;
UPDATE digiQuest SET version = "1.0.4";
"""

def launch_update(common_funcs, app_paths, app_config, mysql_credentials=None, **kwargs):
	return common_funcs.execute_mysql_script(mysql_credentials, MYSQL_CMD)
