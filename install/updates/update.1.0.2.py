from temod.storage.mysql import MysqlEntityStorage
from core.entity import UserGCalendar

import os

MYSQL_CMD = """
CREATE TABLE location(
    id varchar(36) primary key not null,
    name varchar(100) not null,
    address varchar(250) not null,
    label varchar(50)
);

ALTER TABLE event ADD location varchar(250) COLLATE latin1_general_cs;

UPDATE digiQuest SET version = "1.0.3";
"""

def launch_update(common_funcs, app_paths, app_config, mysql_credentials=None, **kwargs):
	return common_funcs.execute_mysql_script(mysql_credentials, MYSQL_CMD)
