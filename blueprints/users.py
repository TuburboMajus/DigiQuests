from flask import Blueprint, Response, current_app, request, render_template, abort, redirect
from flask_login import current_user, login_required

from temod.base.condition import Equals, Or, In 
from temod.base.attribute import UUID4Attribute

from pathlib import Path

import traceback
import shutil
import json
import os


def setup(configuration):
	default = {}
	users_blueprint.configuration = {
		key: configuration.get(key, value) for key,value in default.items()
	}
	return users_blueprint


def get_configuration(config):
	try:
		return users_blueprint.configuration.get(config)
	except:
		if not hasattr(users_blueprint,"configuration"):
			setup({})
			return get_configuration(config)
		raise


users_blueprint = Blueprint('users', __name__)
users_blueprint.setup = setup


@users_blueprint.route('/profile')
@login_required
def getProfile():
	account = AccountFile.storage.get(id=current_user['id'])
	gcalendar = UserGCalendar.storage.get(user=current_user['id'])
	return render_template(
		"users/profile.html",
		account=account,
		gcalendar=gcalendar
	)


@users_blueprint.route('/account/<string:accountid>',methods=['POST'])
@login_required
def updateAccount(accountid):
	account = AccountFile.storage.get(id=accountid)
	current_account = AccountFile.storage.get(id=current_user['id'])

	if account is None:
		return Response(404)

	account_privilege = AccountPrivilege.storage.get(id=current_account['userAccount']['idP'])
	if account_privilege['label'] != "admin":
		return Response(403)

	data = dict(request.json)
	if data['updater_password'] != current_account['mdp']:
		return Response(403)

	if data['user']['password'] != data['user']['cpassword']:
		return Response(400,'Passwords do not match')

	if len(data['user']['password']) < 8:
		return Response(400,'Password must be 8 characters or more')

	account.takeSnapshot()
	account['user']['mdp'] = data['user']['password']
	AccountFile.storage.updateOnSnapshot(account)

	return Response(200, 'update success')


@users_blueprint.route('/user/gcalendar',methods=['GET'])
@login_required
def getGcalendar():
	gcalendar = UserGCalendar.storage.get(user=current_user['id'])

	if gcalendar is None:
		return {"data":None}

	return {"data":gcalendar.to_dict()}


@users_blueprint.route('/user/gcalendar',methods=['POST'])
@login_required
def syncGcalendar():
	gcalendar = UserGCalendar.storage.get(user=current_user['id'])
	data = dict(request.form)

	if gcalendar is None:
		return redirect("/gservices/calendar?final_url=/user/gcalendar")
	else:
		gcalendar.takeSnapshot().setAttribute("sync",data['sync']=="true")
		UserGCalendar.storage.updateOnSnapshot(gcalendar)

	return {"success":"ok"}