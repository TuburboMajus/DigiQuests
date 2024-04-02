from .service import GoogleService
from datetime import datetime

GOOGLE_CALENDAR_SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

class WrongDateFormat(Exception):
	pass


class GoogleCalendar(GoogleService):
	"""docstring for GoogleCalendar"""
	NOW = -1
	DEFAULT_CALENDAR = "primary"

	def __init__(self, service_version="v3", scopes=None, calendarId=None, **kwargs):
		scopes = scopes if not scopes is None else GOOGLE_CALENDAR_SCOPES
		super(GoogleCalendar, self).__init__("calendar",service_version=service_version,scopes=scopes,**kwargs)
		self.calendarId = GoogleCalendar.DEFAULT_CALENDAR if calendarId is None else calendarId

	def setCalendar(self, calendar):
		self.calendarId = calendar
		return self

	def createCalendar(self, summary, timezone="utc"):
		service = self.get_service()
		kwargs = {"summary":summary,"timeZone":timezone}
		return service.calendars().insert(body=kwargs).execute()
		
	def getOrCreateCalendar(self, summary=None, id=None, timezone="utc"):
		if summary is None and id is None:
			raise Exception("At least one identifier is needed (summary or id) to get a calendar. Both can't be None.")
		filter_ = {}
		if id is not None:
			filter_['id'] = id
		if summary is not None:
			filter_['summary'] = summary
		service = self.get_service()
		calendars = service.calendarList().list().execute().get('items',[])
		for calendar in calendars:
			if all([filter_[k] == calendar[k] for k in filter_]):
				return self.setCalendar(calendar['id'])
		if summary is None:
			raise Exception("Cannot create calendar without summary")
		calendar = self.createCalendar(summary, timezone=timezone)
		return self.setCalendar(calendar['id'])

	def listEvents(self, calendar=None, start_date=None, max_results=None, singleEvents=True, orderBy="startTime"):
		service = self.get_service()
		kwargs = {"calendarId":calendar if not calendar is None else self.calendarId}

		if type(start_date) is int:
			if start_date == GoogleCalendar.NOW:
				start_date = datetime.utcnow().isoformat() + "Z"
			elif start_date > 0:
				start_date = datetime.fromtimestamp(start_date).isoformat() + "Z"
			else:
				raise WrongDateFormat(f"Wrong value {start_date} for start_date. Use isoformat strings, datetime objects, timestamps or GoogleCalendar constants")
			kwargs["timeMin"] = start_date
		elif type(start_date) is str:
			start_date = start_date.strip()
			if not start_date.endswith("Z"):
				start_date += "Z"
			kwargs["timeMin"] = start_date
		elif type(start_date) is datetime:
			kwargs["timeMin"] = datetime.isoformat() + "Z"

		if max_results is not None:
			kwargs['maxResults'] = int(max_results)

		if singleEvents:
			kwargs['singleEvents'] = bool(singleEvents)

		if orderBy is not None:
			kwargs['orderBy'] = orderBy

		return (service.events().list(**kwargs).execute()).get("events",[])

	def addEvent(self, gEvent, calendar=None):
		calendar = calendar if not calendar is None else self.calendarId
		self.get_service()
		return self.service.events().insert(calendarId=calendar, body=gEvent.to_dict()).execute()

	def updateEventById(self, eventId, calendar=None, **updates):
		calendar = calendar if not calendar is None else self.calendarId
		self.get_service()
		return self.service.events().update(calendarId=calendar, eventId=eventId, body=updates).execute()

	def updateEvent(self, gEvent, calendar=None):
		calendar = calendar if not calendar is None else self.calendarId
		self.get_service()
		body = gEvent.to_dict(); body.pop('id')
		return self.service.events().update(calendarId=calendar, eventId=gEvent.od, body=body).execute()

	def deleteEventById(self, eventId, calendar=None):
		calendar = calendar if not calendar is None else self.calendarId
		self.get_service()
		return self.service.events().delete(calendarId=calendar, eventId=eventId).execute()

	def deleteEvent(self, gEvent, calendar=None):
		calendar = calendar if not calendar is None else self.calendarId
		self.get_service()
		return self.service.events().delete(calendarId=calendar, eventId=gEvent.id).execute()


class GoogleCalendarEvent(object):
	"""docstring for GoogleCalendarEvent"""
	def __init__(self, summary, start_date, end_date, id=None, description=None, location=None, recurrence=None, attendees=None, reminders=None):
		super(GoogleCalendarEvent, self).__init__()
		self.id = id
		self.summary = summary
		self.start_date = start_date
		self.end_date = end_date
		self.description = description
		self.location = location
		self.recurrence = recurrence
		self.attendees = attendees
		self.reminders = reminders

	def to_dict(self):
		dct = {
			"id":self.id,
			"summary":self.summary, 
			"start":{
				"dateTime":self.start_date.isoformat(),"timeZone":"utc"
			}, 
			"end":{
				"dateTime":self.end_date.isoformat(),"timeZone":"utc"
			}
		}
		if self.description is not None:
			dct['description'] = self.description
		if self.location is not None:
			dct['location'] = self.location
		if self.recurrence is not None:
			dct['recurrence'] = self.recurrence
		if self.attendees is not None:
			dct['attendees'] = [{"email":attendee}  for attendee in self.attendees]
		if self.reminders is not None:
			dct['reminders'] = self.reminders
		return dct




		