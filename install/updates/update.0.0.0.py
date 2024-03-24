from subprocess import Popen, PIPE, STDOUT


MYSQL_CMD = """
ALTER TABLE quest ADD owner varchar(36) not null;
ALTER TABLE quest ADD CONSTRAINT foreign key (owner) references user(id);
UPDATE quest SET owner = (SELECT id FROM user u, userAccount ua, accountPrivilege ap WHERE ap.label = "admin" AND ua.idP = ap.id AND u.id = ua.idU LIMIT 1);
"""


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

def launch_update(credentials):
	cmd = create_mysql_cmd(credentials)

	p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE, text=True)
	stdout_data = p.communicate(input=MYSQL_CMD)[0]