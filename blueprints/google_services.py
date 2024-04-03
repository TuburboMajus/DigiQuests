from flask import Blueprint, Response, current_app, request, render_template, abort, redirect, session
from flask_login import current_user, login_required

from tools.google import GoogleCalendar, GoogleCalendarEvent

from temod.base.condition import Equals, Or, In 
from temod.base.attribute import UUID4Attribute

from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path

import traceback
import shutil
import json
import os


def setup(configuration):
	default = {
		"credentials_file":"resources/gcalendar_creds.json",
		"tokens_dir":"resources/tokens",
		"domain_name":"127.0.0.1"
	}
	google_services_blueprint.configuration = {
		key: configuration.get(key, value) for key,value in default.items()
	}
	return google_services_blueprint


def get_configuration(config):
	try:
		return google_services_blueprint.configuration.get(config)
	except:
		if not hasattr(google_services_blueprint,"configuration"):
			setup({})
			return get_configuration(config)
		raise


google_services_blueprint = Blueprint('google_services', __name__)
google_services_blueprint.setup = setup


@google_services_blueprint.route("/gservices/calendar")
@login_required
def enableCalendarApi():

	base_url = urlparse(request.base_url)
	scheme = base_url.scheme
	netloc = base_url.netloc
	domain_name = get_configuration('domain_name')
	if domain_name is not None:
		netloc = domain_name

	final_url = request.args.get("final_url")
	redirect_uri_params = ""
	if final_url is not None:
		redirect_uri_params = f"?final_url={final_url}"

	token_file = os.path.join(get_configuration('tokens_dir'),f"{current_user['id']}.json")
	GCalendar = GoogleCalendar(
		token_file=token_file,
		credentials_file=get_configuration('credentials_file'),
		scopes=[
			'https://www.googleapis.com/auth/calendar.app.created',
			'https://www.googleapis.com/auth/calendar.calendarlist.readonly'
		],redirect_uri=f"{scheme}://{netloc}/gservices/calendar/auth"
	)

	flow = GCalendar.get_service()
	if flow is not None:
		authorization_url,state = flow.authorization_url(access_type='offline',prompt='select_account')
		session['state'] = state
		return redirect(authorization_url)

	gcalendar = UserGCalendar.storage.get(user=current_user['id'])
	if gcalendar is not None:
		GCalendar.setCalendar(gcalendar['calendar'])
	else:
		GCalendar.getOrCreateCalendar('digiq')
		UserGCalendar.storage.create(UserGCalendar(
			user=current_user['id'],calendar=GCalendar.calendarId,sync=True, token_file=token_file
		))

	return redirect(final_url if final_url is not None else "/")



@google_services_blueprint.route("/gservices/calendar/auth")
@login_required
def CalendarApiAuth():

	if request.args.get('state') != session['state']:
		raise Exception('Invalid state')

	base_url = urlparse(request.base_url)
	scheme = base_url.scheme
	netloc = base_url.netloc
	domain_name = get_configuration('domain_name')
	if domain_name is not None:
		netloc = domain_name
	final_url = request.args.get("final_url")
	redirect_uri_params = ""
	if final_url is not None:
		redirect_uri_params = f"?final_url={final_url}"
*
	token_file = os.path.join(get_configuration('tokens_dir'),f"{current_user['id']}.json")
	GCalendar = GoogleCalendar(
		token_file=token_file,
		credentials_file=get_configuration('credentials_file'),
		scopes=[
			'https://www.googleapis.com/auth/calendar.app.created',
			'https://www.googleapis.com/auth/calendar.calendarlist.readonly'
		],redirect_uri=f"{scheme}://{netloc}/gservices/calendar/auth"
	)

	if not GCalendar.fetch_creds(session['state'], request.url):
		return "Error occured while authentifiying"

	GCalendar.get_service()
	gcalendar = UserGCalendar.storage.get(user=current_user['id'])
	if gcalendar is not None:
		GCalendar.setCalendar(gcalendar['calendar'])
	else:
		GCalendar.getOrCreateCalendar('digiq')
		UserGCalendar.storage.create(UserGCalendar(
			user=current_user['id'],calendar=GCalendar.calendarId,sync=True, token_file=token_file
		))

	return redirect(final_url if final_url is not None else "/")