from flask import Flask, Response, request, render_template, redirect, session
from flask_login import login_required,login_user,logout_user,current_user

from temod_flask.security.authentification import Authenticator, TemodUserHandler
from temod.ext.holders import init_holders

from subprocess import Popen, PIPE, STDOUT

from blueprints import *
from context import *

import traceback
import mimetypes
import toml
import json
import os


# ** Section ** MimetypesDefinition
mimetypes.add_type('text/css', '.css')
mimetypes.add_type('text/css', '.min.css')
mimetypes.add_type('text/javascript', '.js')
mimetypes.add_type('text/javascript', '.min.js')
# ** EndSection ** MimetypesDefinition


# ** Section ** LoadConfiguration
with open(os.path.join(os.path.dirname(os.path.realpath(__file__)),"config.toml")) as config_file:
	config = toml.load(config_file)
# ** EndSection ** LoadConfiguration


# ** Section ** ContextCreation
init_holders(
	entities_dir=os.path.join(config['temod']['core_directory'],r"entity"),
	joins_dir=os.path.join(config['temod']['core_directory'],r"join"),
	databases=config['temod']['bound_database'],
	db_credentials=config['storage']['credentials']
)
init_context(config)
# ** EndSection ** ContextCreation


# ** Section ** AppCreation
def update_configuration(original_config, new_config):
    new_keys = set(new_config).difference(set(original_config))
    common_keys = set(new_config).intersection(set(original_config))
    for k in common_keys:
        if type(original_config[k]) is dict and type(new_config[k]) is not dict:
            raise Exception("Unmatched config type")
        if type(original_config[k]) is dict:
            update_configuration(original_config[k],new_config[k])
        else:
            original_config[k] = new_config[k]
    for k in new_keys:
        original_config[k] = new_config[k]

def build_app(**app_configuration):

	update_configuration(config,app_configuration)

	app = Flask(
		__name__,
		template_folder=config['app']['templates_folder'],
		static_folder=config['app']['static_folder']
	)

	secret_key = config['app'].get('secret_key','')
	app.secret_key = secret_key if len(secret_key) > 0 else generate_secret_key(32)
	app.config['CUSTOM_CONFIG'] = {k:v for k,v in config['app'].items() if not type(v) is dict} 


	# ** Section ** Blueprint
	app.register_blueprint(quests_log_blueprint.setup(config['app'].get('blueprints',{}).get('quests_log',{})))
	app.register_blueprint(users_blueprint.setup(config['app'].get('blueprints',{}).get("users",{})))
	app.register_blueprint(google_services_blueprint.setup(config['app'].get('blueprints',{}).get("google_services",{})))
	# ** EndSection ** Blueprint

	# ** Section ** Authentification
	AUTHENTICATOR = Authenticator(TemodUserHandler(
		joins.AccountFile, "mysql", logins=['username','mdp'], **config['storage']['credentials']
	))
	AUTHENTICATOR.init_app(app)
	# ** EndSection ** Authentification

	# ** Section ** AppMainRoutes
	@app.route('/', methods=['GET'])
	@login_required
	def home():
		return redirect("/quests")

	@app.route('/login', methods=["GET",'POST'])
	def login():
		
		if request.method == "POST":
			user = AUTHENTICATOR.search_user(request.form.get("username"),request.form.get("password"))
			if user is not None:
				AUTHENTICATOR.login_user(user)
				return redirect("/quests")
		return render_template("auth/login.html")

	@app.route('/logout',methods=['GET'])
	@login_required
	def logout():
		session.clear()
		AUTHENTICATOR.logout_user(current_user)
		return redirect('/login')
	# ** EndSection ** AppMainRoutes

	return app
# ** EndSection ** AppCreation


# ** Section ** DigiqService
def check_digiq_service():
	cmd = ["systemctl","status","digiq.timer"]
	
	p = Popen(cmd, stdout=PIPE, stdin=PIPE, stderr=PIPE)
	stdout_data, stderr_data = p.communicate()

	if b'Unit digiq.service could not be found.' in stderr_data:
		raise Exception("Digiq service not installed, please update your app.")

	if b"Active: inactive (dead)" in stdout_data:
		raise Exception("Digiq service is stopped (dead). Start it before running the app.")
	
	if b"Active: active" in stdout_data:
		return True

	print(stdout_data.split(b'\n'))
	print(stderr_data.split(b'\n'))
	raise Exception("Digiq service is not running or can't determine if it is")
# ** EndSection ** DigiqService


if __name__ == '__main__':

	check_digiq_service()

	app = build_app(**config)

	server_configs = {
		"host":config['app']['host'], "port":config['app']['port'],
		"threaded":config['app']['threaded'],"debug":config['app']['debug']
	}
	if config['app'].get('ssl',False):
		server_configs['ssl_context'] = (config['app']['ssl_cert'],config['app']['ssl_key'])

	app.run(**server_configs)
