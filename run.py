from flask import Flask, Response, request, render_template, redirect
from flask_login import login_required,login_user,logout_user,current_user

from temod_flask.security.authentification import Authenticator, TemodUserHandler
from temod.ext.holders import init_holders

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

# ** Section ** ConfigurationLoad
with open("./config.toml") as config_file:
	config = toml.load(config_file)
# ** EndSection ** ConfigurationLoad

# ** Section ** AppCreation
app = Flask(
	__name__,
	template_folder=config['app']['templates_folder'],
	static_folder=config['app']['static_folder']
)
app.secret_key= config['app']['secret_key']
temod_core = config['temod']['core_directory']
init_holders(
	entities_dir=os.path.join(temod_core,r"entity"),
	joins_dir=os.path.join(temod_core,r"join"),
	databases=config['temod']['bound_database'],
	db_credentials=config['storage']['credentials']
)
init_context()
# ** EndSection ** AppCreation


# ** Section ** Blueprint
app.register_blueprint(quests_log_blueprint.setup(config['app'].get('blueprints',{}).get('quests_log',{})))
app.register_blueprint(users_blueprint.setup(config['app'].get('blueprints',{}).get("users",{})))
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
		print(request.form)
		print(user)
		if user is not None:
			AUTHENTICATOR.login_user(user)
			return redirect("/quests")
	return render_template("auth/login.html")

@app.route('/logout',methods=['GET'])
@login_required
def logout():
	AUTHENTICATOR.logout_user(current_user)
	return redirect('/login')
# ** EndSection ** AppMainRoutes


if __name__ == '__main__':
	if config['app']['prod']:
		from waitress import serve
		serve(app, host=config['app']['host'],port=config['app']['port'])
	else:
		app.run(host=config['app']['host'],port=config['app']['port'],threaded=config['app']['threaded'],debug=config['app']['debug'])