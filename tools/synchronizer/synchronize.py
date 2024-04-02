from temod.base.attribute import DateTimeAttribute
from temod.storage import MysqlEntityStorage
from temod.base.condition import Superior

from datetime import datetime

import googleapiclient
import traceback
import argparse
import logging
import toml
import sys
import os


GOOGLE_CALENDAR_SCOPES = [
	'https://www.googleapis.com/auth/calendar.app.created',
	'https://www.googleapis.com/auth/calendar.calendarlist.readonly'
]

GOOGLE_SYNC_JOB_NAME = "GsyncJob"

def load_configs(root_dir):
	with open(os.path.join(root_dir,"config.toml")) as config_file:
		config = toml.load(config_file)
	return config


def get_logger(logging_dir):
	logger = logging.getLogger()
	logger.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

	if logging_dir is not None and os.path.isdir(logging_dir):
		fh = logging.FileHandler(os.path.join(logging_dir,"synchronizer.log"), 'a')
		fh.setLevel(logging.DEBUG)
		fh.setFormatter(formatter)
		logger.addHandler(fh)
	else:
		print("No valid logging directory specified. No logs will be kept.")

	dh = logging.StreamHandler(sys.stdout)
	dh.setLevel(logging.WARNING)
	dh.setFormatter(formatter)
	logger.addHandler(dh)

	return logger


class GoogleCalendarSynchronizer(object):
	"""docstring for GoogleCalendarSynchronizer"""
	def __init__(self, tokens_dir, creds_file, **mysql_credentials):
		super(GoogleCalendarSynchronizer, self).__init__()
		self.tokens_dir = tokens_dir
		self.creds_file = creds_file
		self.mysql_credentials = mysql_credentials
		self.storages = {
			"quests": MysqlEntityStorage(Quest,**self.mysql_credentials),
			"events": MysqlEntityStorage(Event,**self.mysql_credentials),
			"gevents": MysqlEntityStorage(GEvent,**self.mysql_credentials),
			"resourceKeys": MysqlEntityStorage(ResourceKey,**self.mysql_credentials),
			"gcalendars": MysqlEntityStorage(UserGCalendar,**self.mysql_credentials),
			"tasks": MysqlEntityStorage(Task,**self.mysql_credentials)
		}

	def delete_event(self,event):
		gevent = self.storages['gevents'].get(event=event['id'])
		if gevent is not None:
			try:
				GoogleCalendar(
					token_file=os.path.join(self.tokens_dir,f"{gevent['owner']}.json"),
					credentials_file=self.creds_file,
					scopes=GOOGLE_CALENDAR_SCOPES,
					calendarId=gevent['gcalendar_id']
				).deleteEventById(
					gevent['gevent_id']
				)
			except googleapiclient.errors.HttpError as error:
				if error.status_code == 410:
					if "Resource has been deleted" in error.reason:
						LOGGER.info(f"Google event {gevent['event']} has already been deleted")
					else:
						raise
				else:
					raise
			else:
				LOGGER.info(f"Event {event['id']} deleted from gcalendar (event_id: {gevent['gevent_id']})")
			self.storages['gevents'].delete(event=gevent['event'])

		self.storages['events'].delete(id=event['id'])
		return True


	def create_event(self, event):
		quest = self.storages['quests'].get(id=event['quest'])
		task = self.storages['tasks'].get(id=event['task'])
		gcalendar = self.storages['gcalendars'].get(user=quest['owner'])
		if gcalendar is None or not gcalendar['sync']:
			LOGGER.info(f"Onwer {gevent['owner']} has not enabled sync.")
			return True

		created = GoogleCalendar(
			token_file=os.path.join(self.tokens_dir,f"{gcalendar['user']}.json"),
			credentials_file=self.creds_file,
			scopes=GOOGLE_CALENDAR_SCORES,
			calendarId=gcalendar['calendar']
		).addEvent(GoogleCalendarEvent(
			task['content'], event['start_date'], event['end_date']
		))

		self.storages['gevents'].create(GEvent(
			event=event['id'],owner=quest['owner'],gcalendar_id=gcalendar['calendar'],gevent_id=created['id']
		))
		LOGGER.info(f"Event {event['id']} created on gcalendar (event_id: {created['id']})")
		return True


	def update_event(self, event):
		gevent = self.storages['gevents'].get(event=event['id'])
		if gevent is None:
			return self.create_event(event)

		gevent.takeSnapshot()
		task = self.storages['tasks'].get(id=event['task'])
		gcalendar = self.storages['gcalendars'].get(user=gevent['owner'])
		if gcalendar is None or not gcalendar['sync']:
			LOGGER.info(f"Onwer {gevent['owner']} has not enabled sync.")
			return True

		updated = GoogleCalendar(
			token_file=os.path.join(self.tokens_dir,f"{gcalendar['user']}.json"),
			credentials_file=self.creds_file,
			scopes=GOOGLE_CALENDAR_SCORES,
			calendarId=gcalendar['calendar']
		).updateEvent(GoogleCalendarEvent(
			task['content'], event['start_date'], event['end_date'], id=gevent['gevent_id']
		))
		gevent.setAttribute("id",updated['id'])
		self.storages['gevents'].updateOnSnapshot(gevent)
		LOGGER.info(f"Event {event['id']} updated on gcalendar (event_id: {gevent['gevent_id']})")
		return True


	def synchronize_event(self,event):
		if event['task'] is None or event['quest'] is None:
			result = self.delete_event(event)
		result = self.update_event(event)
		event.takeSnapshot()
		event.setAttribute('synced',True)
		self.storages['events'].updateOnSnapshot(event)
		LOGGER.info(f"Event {event['id']} sync results: {result}")
		return result


	def synchronize(self):
		unsynchronized_events = self.storages['events'].list(
			Superior(DateTimeAttribute("start_date",value=datetime.utcnow())),synced=False
		)

		events_synchronized = []
		for event in unsynchronized_events:
			events_synchronized.append(self.synchronize_event(event))

		if len(events_synchronized) == 0:
			LOGGER.info("No event to synchronize")
			return None

		return all(events_synchronized)
		

def already_running(**mysql_credentials):
	GsyncJob = MysqlEntityStorage(Job, **mysql_credentials).get(name=GOOGLE_SYNC_JOB_NAME)
	if GsyncJob['state'] == "RUNNING":
		return True
	return False

def start_run(**mysql_credentials):
	storage = MysqlEntityStorage(Job, **mysql_credentials)
	GsyncJob = storage.get(name=GOOGLE_SYNC_JOB_NAME).takeSnapshot()
	GsyncJob.setAttribute("state","RUNNING")
	storage.updateOnSnapshot(GsyncJob)


def stop_run(exit_code, **mysql_credentials):
	storage = MysqlEntityStorage(Job, **mysql_credentials)
	GsyncJob = storage.get(name=GOOGLE_SYNC_JOB_NAME).takeSnapshot()
	GsyncJob.setAttribute("state","IDLE")
	GsyncJob.setAttribute("last_exit_code",exit_code)
	storage.updateOnSnapshot(GsyncJob)
	if exit_code != 0:
		sys.exit(exit_code)

def launch(config):
	if already_running(**config["storage"]["credentials"]):
		LOGGER.info("Synchronization is already ongoing. Postponing execution.")
		return
	start_run(**config["storage"]["credentials"])

	synchronizer = GoogleCalendarSynchronizer(
		config['app']['blueprints']['google_services']['tokens_dir'],
		config['app']['blueprints']['google_services']['credentials_file'],
		**config["storage"]["credentials"]
	)

	synchronization_results = synchronizer.synchronize()	
	exit_code=0	
	if synchronization_results is not None:
		if synchronization_results:
			LOGGER.info("All events synchronized successfully.")
		else:
			LOGGER.warning("Some events did not synchronize successfully.")
			exit_code=2

if __name__ == "__main__":
	""" Defining and parsing args """
	parser = argparse.ArgumentParser(prog="Synchronizes DigiQuest events with external apps")

	parser.add_argument('-r', '--root-dir', help='DigiQuest root directory', default=".")
	parser.add_argument('-l', '--logging-dir', help='Directory where to store logs.', default=None)

	args = parser.parse_args()

	if args.root_dir:
		if not os.path.isdir(args.root_dir):
			print(f"Root directory path must be a valid directory.")
			sys.exit(1)
		if not args.root_dir in sys.path:
			sys.path.append(args.root_dir)
	else:
		sys.exit(1)

	setattr(__builtins__,'LOGGER', get_logger(args.logging_dir))
	
	from core.entity import Event, GEvent, UserGCalendar, Quest, Task, ResourceKey, Job
	from tools.google import GoogleCalendar, GoogleCalendarEvent

	config = load_configs(args.root_dir)

	try:
		exit_code = launch(config)
	except:
		LOGGER.error("Synchronization failed with error. Traceback:")
		LOGGER.error(traceback.format_exc())
		stop_run(1,**config["storage"]["credentials"])
	else:
		stop_run(exit_code,**config["storage"]["credentials"])
