# Global Imports
import os
from typing import Generator

# Google API Imports
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Local Imports
from backend.models import SheetData

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def to_float(value:str)->float:
    value = value.replace(',', '.')
    return round(float(value), 2)

def loginGoogle():
    creds = None
    if os.path.exists('./backend/token.json'):
        creds = Credentials.from_authorized_user_file('./backend/token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                './backend/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('./backend/token.json', 'w') as token:
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

            return values, sheet

        except HttpError as err:
            if i == 0 and os.path.exists('./backend/credentials.json'):
                os.remove('./backend/credentials.json')
            else:
                print(err)

def getSheetData(table_address:str, table_range:str)->Generator[SheetData, None, None]:
    sheet_list, _ = runSheets(table_address, table_range)

    for line in sheet_list:
        try:
            yield SheetData(nfe=int(line[0]), data=line[1], dest_id=line[2],
                            cidade=line[3], valor_mercadoria= to_float(line[4]),
                            comissao=to_float(line[5]), valor_frete=to_float(line[6]),
                            emissor=line[8])
            
        except Exception as e:
            print(e)
    