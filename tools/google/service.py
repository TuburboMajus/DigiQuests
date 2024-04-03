from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pathlib import Path

import datetime
import json
import os


CREDENTIAL_TYPE_WEB = 0


class GoogleService(object):
	"""docstring for GoogleService"""
	def __init__(self, service_name, service_version, scopes, token_file="token.json", credentials_file="credentials.json", 
		redirect_uri=None, credentials=None, credential_type=CREDENTIAL_TYPE_WEB):
		super(GoogleService, self).__init__()
		self.credentials = credentials if not credentials is None else {}
		self.scopes = scopes
		self.service_name = service_name
		self.service_version = service_version
		self.token_file = token_file
		self.credentials_file = credentials_file
		self.credential_type = credential_type
		self.redirect_uri = redirect_uri
		self.creds = None
		self.service = None


	def get_creds(self):
		if self.creds is not None:
			return self.creds

		creds = None
		if os.path.exists(self.token_file):
			creds = Credentials.from_authorized_user_file(self.token_file, self.scopes)

		if creds is None or not creds.valid:
			if creds and creds.expired and creds.refresh_token:
				creds.refresh(Request())
			else:
				if self.credential_type == CREDENTIAL_TYPE_WEB:
					self.flow = InstalledAppFlow.from_client_secrets_file(
						self.credentials_file, scopes=self.scopes,redirect_uri=self.redirect_uri
					)
				else:
					raise Exception('Unknown credential type')

		self.creds = creds
		return self.creds

	def fetch_creds(self, state, authorization_response):
		self.flow = InstalledAppFlow.from_client_secrets_file(
			self.credentials_file, scopes=self.scopes,redirect_uri=self.redirect_uri, state=state
		)
		self.flow.fetch_token(authorization_response=authorization_response)
		self.creds = self.flow.credentials

		path = Path(self.token_file)
		if not os.path.isdir(path.parent):
			os.makedirs(path.parent)
		with open(self.token_file, "w") as token:
			token.write(self.creds.to_json())

		return True

	def get_service(self):
		if self.service is not None:
			return self.service
		creds = self.get_creds()
		if creds is None:
			return self.flow
		print("creds = ",creds)
		self.service = build(self.service_name, self.service_version, credentials=creds)

