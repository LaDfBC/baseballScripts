from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from oauth2client.service_account import ServiceAccountCredentials
import gspread

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
SCOPES_WITH_WRITE_ENABLED = 'https://www.googleapis.com/auth/spreadsheets'

# The ID and range of a sample spreadsheet.
SAMPLE_RANGE_NAME = '1 - SDP@PHI'

'''
Negotiates with Oauth2 and the Google Sheets API to return the service used to fetch the Google Sheets spreadsheet
service.

Necessary for most functions calling out to a Google Sheet.
'''
def get_spreadsheet_service(write_enabled=False):
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        if write_enabled:
            flow = client.flow_from_clientsecrets('/usr/auth/credentials.json', SCOPES_WITH_WRITE_ENABLED)
        else:
            flow = client.flow_from_clientsecrets('/usr/auth/credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    return service.spreadsheets()


def get_gspread_service():
    scope = ['https://www.googleapis.com/auth/spreadsheets',
             'https://www.googleapis.com/auth/drive']

    credentials = ServiceAccountCredentials.from_json_keyfile_name('/usr/auth/file.txt', scope)

    return gspread.authorize(credentials)

def analyzePitcherFromOnlineSheet():
    pass
