from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pathlib import Path

import datetime
import json
import os


class GoogleService(object):
	"""docstring for GoogleService"""
	def __init__(self, service_name, service_version, scopes, token_file="token.json", credentials_file="credentials.json", redirect_uri=None, credentials=None):
		super(GoogleService, self).__init__()
		self.credentials = credentials if not credentials is None else {}
		self.scopes = scopes
		self.service_name = service_name
		self.service_version = service_version
		self.token_file = token_file
		self.credentials_file = credentials_file
		self.redirect_uri = redirect_uri
		self.creds = None
		self.service = None

	def get_creds(self, local=True, code=None, state=None):
		if self.creds is not None:
			return self.creds
		creds = None
		if os.path.exists(self.token_file):
			creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)

		if creds is None or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				self.flow = InstalledAppFlow.from_client_secrets_file(
					self.credentials_file, scopes=self.scopes,redirect_uri=self.redirect_uri, state=state
				)

				if local:
					creds = self.flow.run_local_server(port=0)
				elif code is not None:
					self.flow.fetch_token(code=code)
					creds = self.flow.credentials

				if creds is not None:
					path = Path(self.token_file)
					if not os.path.isdir(path.parent):
						os.mkdir(path.parent)
					with open(self.token_file, "w") as token:
						token.write(creds.to_json())

		self.creds = creds
		return self.creds

	def get_service(self, local=True, code=None, state=None):
		if self.service is not None:
			return self.service
		creds = self.get_creds(local=local, code=code, state=state)
		if creds is None:
			return self.flow
		self.service = build(self.service_name, self.service_version, credentials=creds)

