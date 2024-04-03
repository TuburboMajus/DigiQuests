from temod.storage.mysql import MysqlEntityStorage
from core.entity import UserGCalendar

import os

MYSQL_CMD = """
ALTER TABLE userGCalendar ADD token_file varchar(300) not null;
"""

MYSQL_CMD_2 = """
UPDATE digiQuest SET version = "1.0.2";
"""

def launch_update(common_funcs, app_paths, app_config, mysql_credentials=None, **kwargs):
	result = common_funcs.execute_mysql_script(mysql_credentials, MYSQL_CMD)
	if not result:
		return False

	calendars = MysqlEntityStorage(UserGCalendar,**mysql_credentials)

	for calendar in calendars.list():
		calendar.takeSnapshot().setAttribute("token_file",os.path.join(
			app_config['app']['blueprints']['google_services']['tokens_dir'],f'{calendar["user"]}.json'
		))
		calendars.updateOnSnapshot(calendar)

	return common_funcs.execute_mysql_script(mysql_credentials, MYSQL_CMD_2)
