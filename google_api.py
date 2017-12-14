
from __future__ import print_function
import httplib2
import os

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/sheets.googleapis.com-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/spreadsheets.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Sheets API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'sheets.googleapis.com-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials


def process_row(row):
    if (len(row) > 0):
        strategy = str(row[0])
        symbol = ''
        if (len(row)) > 1:
            symbol = str(row[1]).split(' ')[0]
        side = ''
        if (len(row)) > 2:
            side = str(row[2])
        bp_share = ''
        if (len(row)) > 3:
            bp_share = str(row[3])
        note = ''
        if (len(row)) > 4:
            note = str(row[4])
        account = ''
        if (len(row)) > 5:
            account = str(row[5]).upper()

        print('strategy: {0}, {1}, {2}, {3}, {4}, {5}'.format(strategy, symbol, side, bp_share, note, account))



def get_sheet():
    """Shows basic usage of the Sheets API.

    Creates a Sheets API service object and prints the names and majors of
    students in a sample spreadsheet:
    https://docs.google.com/spreadsheets/d/1BxiMVs0XRA5nFMdKvBdBZjgmUUqptlbs74OgvE2upms/edit
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    discoveryUrl = ('https://sheets.googleapis.com/$discovery/rest?'
                    'version=v4')
    service = discovery.build('sheets', 'v4', http=http,
                              discoveryServiceUrl=discoveryUrl)
    # https://docs.google.com/spreadsheets/d/1Z3POIK8N5Vi_CsF_MDLszrJeNviBwrU9BuVFC8h-xgQ/edit?usp=sharing
    spreadsheetId = '1Z3POIK8N5Vi_CsF_MDLszrJeNviBwrU9BuVFC8h-xgQ'
    # rangeName = 'Class Data!A2:E'
    # result = service.spreadsheets().values().get(
    #     spreadsheetId=spreadsheetId, range=rangeName).execute()
    # values = result.get('values', [])
    #
    # if not values:
    #     print('No data found.')
    # else:
    #     print('Name, Major:')
    #     for row in values:
    #         # Print columns A and E, which correspond to indices 0 and 4.
    #         print('%s, %s' % (row[0], row[4]))
    rangeName = 'Today Trading List!A1:M'
    result = service.spreadsheets().values().get(
        spreadsheetId = spreadsheetId, range = rangeName
    ).execute()
    return result.get('values',[])



