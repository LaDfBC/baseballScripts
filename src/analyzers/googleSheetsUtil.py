from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

from src.analyzers.distributionAnalyzer import groupValuesByRange
from src.spreadsheet.row_organizer import PITCHER, PITCH_VALUE, GAME_NUMBER, get_row_as_dict

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'

# The ID and range of a sample spreadsheet.
SAMPLE_RANGE_NAME = '1 - SDP@PHI'

'''
Negotiates with Oauth2 and the Google Sheets API to return the service used to fetch the Google Sheets spreadsheet
service.

Necessary for most functions calling out to a Google Sheet.
'''
def get_spreadsheet_service():
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('sheets', 'v4', http=creds.authorize(Http()))

    # Call the Sheets API
    return service.spreadsheets()

def analyzePitcherFromOnlineSheet():
    pass

if __name__ == '__main__':
    pitches, deltas = main()
    result = groupValuesByRange(deltas, range_size=100, numbers=[-999, 1001])
    print(result)