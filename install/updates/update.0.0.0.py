MYSQL_CMD = """
ALTER TABLE quest ADD owner varchar(36) not null;
ALTER TABLE quest ADD CONSTRAINT foreign key (owner) references user(id);
UPDATE quest SET owner = (SELECT u.id FROM user u, userAccount ua, accountPrivilege ap WHERE ap.label = "admin" AND ua.idP = ap.id AND u.id = ua.idU LIMIT 1);
UPDATE digiQuest SET version = "1.0.0";
"""

def launch_update(dgq_version, app_paths, mysql_credentials=None, **kwargs):
	return common_funcs.execute_mysql_script(mysql_credentials, MYSQL_CMD)