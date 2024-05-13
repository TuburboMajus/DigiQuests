from temod.storage.mysql import MysqlEntityStorage
from core.entity import UserGCalendar

import os

MYSQL_CMD = """
CREATE TABLE storyline(
    id varchar(36) primary key not null,
    title varchar(100) not null
);

ALTER TABLE quest ADD storyline varchar(36);
ALTER TABLE quest ADD CONSTRAINT foreign key (storyline) references storyline(id);

UPDATE digiQuest SET version = "1.0.5";
"""

def launch_update(common_funcs, app_paths, app_config, mysql_credentials=None, **kwargs):
	return common_funcs.execute_mysql_script(mysql_credentials, MYSQL_CMD)
