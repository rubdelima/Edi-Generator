import os

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from backend.models import SheetData

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def to_float(value:str)->float:
    value = value.replace(',', '.')
    return round(float(value), 2)

def loginGoogle():
    creds = None
    if os.path.exists('./data/token.json'):
        creds = Credentials.from_authorized_user_file('./data/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './data/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./data/token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def runSheets(sheet_id:str, sheet_range:str):
    SAMPLE_RANGE_NAME = 'Página1!' + sheet_range
    for i in range(2):
        creds = loginGoogle()
        try:
            service = build('sheets', 'v4', credentials=creds)

            # Call the Sheets API
            sheet = service.spreadsheets()
            result = sheet.values().get(spreadsheetId=sheet_id,
                                        range=SAMPLE_RANGE_NAME).execute()
            values = result.get('values', [])

            valores = result['values']

            return valores, sheet

        except HttpError as err:
            if i == 0 and os.path.exists('./data/credentials.json'):
                os.remove('./data/credentials.json')
            else:
                print(err)

def getSheetData(table_address:str, table_range:str)->tuple[list[SheetData], list[str]]:
    sdl, _ = runSheets(table_address, table_range)
    
    success_list = []
    error_list = []

    for sd in sdl:
        try:
            success_list.append(SheetData(nfe=sd[0], data=sd[1], dest_id=sd[2], cidade=sd[3],
                      valor_mercadoria= to_float(sd[4]), comissao=to_float(sd[5]), valor_frete=to_float(sd[6]), emissor=sd[8]))
        except Exception as e:
            print(e)
            error_list.append(sd[0])
    
    return success_list, error_list