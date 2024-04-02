import traceback
import os

MYSQL_CMD = """
CREATE TABLE userGCalendar (
	user varchar(36) primary key not null,
	calendar varchar(200) not null,
	sync bool not null default 1,
	foreign key (user) references user(id)
);

create table event(
    id varchar(36) primary key not null,
    quest varchar(36),
    task varchar(36),
    start_date datetime not null,
    end_date datetime not null,
    synced bool not null default 0,
    constraint unique_event unique (task),
    foreign key (quest) references quest(id),
    foreign key (task) references task(id)
);

create table gevent(
    event varchar(36) primary key not null,
    owner varchar(36) not null,
    gcalendar_id varchar(200) not null,
    gevent_id varchar(200) not null,
    foreign key (event) references event(id),
    foreign key (owner) references user(id)
);

create table job(
    name varchar(50) primary key not null,
    state varchar(20) not null default "IDLE",
    last_exit_code int
);

INSERT into job(name, state) values ("GsyncJob","IDLE");
UPDATE digiQuest SET version = "1.0.1";
"""

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


def launch_update(common_funcs, app_paths, app_config, mysql_credentials=None, script_args=None, **kwargs):
	domain_name = get_domain_name()

	virtual_env = common_funcs.detect_virtual_env(app_paths['root'])
	logging_dir = script_args.logging_dir if not script_args.quiet else None
	if not install_digiq_services(app_paths['root'], virtual_env, logging_dir, script_args.services_dir):
		return False

	app_config['app']['blueprints']['google_services']['domain_name'] = domain_name
	return common_funcs.execute_mysql_script(mysql_credentials, MYSQL_CMD)