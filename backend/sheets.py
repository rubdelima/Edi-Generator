# Global Imports
import os
import tqdm
from   typing import Generator, List
from   prompt_toolkit import prompt
from   prompt_toolkit.completion import WordCompleter

# Google API
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Local Imports
from backend.models import SheetData, loading

SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive.readonly']


class GoogleClient:
    @loading("Carregando Google API", "Google API Carregada")
    def __init__(self):
        self.creds = self.login_google()
        self.sheets_service = build('sheets', 'v4', credentials=self.creds)
        self.drive_service = build('drive',  'v3', credentials=self.creds)

    def login_google(self):
        creds = None
        if os.path.exists('./backend/json/token.json'):
            creds = Credentials.from_authorized_user_file(
                './backend/json/token.json', SCOPES)
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    './backend/json/credentials.json', SCOPES)
                creds = flow.run_local_server(port=0)
            with open('./backend/json/token.json', 'w') as token:
                token.write(creds.to_json())
        return creds
    
    @staticmethod
    def to_float(value: str) -> float:
        value = value.replace(',', '.')
        return round(float(value), 2)

    @loading("Obtendo Lista de Planilhas", "Lista de Planilhas obtidas com suceso!")
    def get_sheets_files(self):
        """Retorna um dicionário com o nome e o ID de todos os arquivos do Google Sheets no Drive do usuário."""
        try:
            results = self.drive_service.files().list(q="mimeType='application/vnd.google-apps.spreadsheet'",
                                                      spaces='drive',
                                                      fields='files(id, name)').execute()
            items = results.get('files', [])
            return {item['name']: item['id'] for item in items}
        except HttpError as err:
            print(err)
            return {}

    def list_sheet_folders(self, sheet_id: str) -> list:
        """Retorna uma lista com os nomes das páginas dentro do documento do Google Sheets especificado."""
        try:
            sheet_metadata = self.sheets_service.spreadsheets().get(
                spreadsheetId=sheet_id).execute()
            sheets = sheet_metadata.get('sheets', '')
            return [sheet.get('properties', {}).get('title', '') for sheet in sheets]
        except HttpError as err:
            print(err)
            return []

    def get_sheet_data(self, sheet_id: str, page_name: str, sheet_range: str) -> List[List[str]]:
        range_name = f'{page_name}!{sheet_range}'
        try:
            sheet = self.sheets_service.spreadsheets()
            result = sheet.values().get(spreadsheetId=sheet_id, range=range_name).execute()
            return result.get('values', [])
        except HttpError as err:
            print(err)
            return []
    
    @loading("Carregando Planilha", "Planilha Carregada")
    def getSheetData(self, sheet_id: str, page_name: str, sheet_range: str) -> Generator[SheetData, None, None]:
        sheet_list = self.get_sheet_data(sheet_id, page_name, sheet_range)

        for line in tqdm.tqdm(sheet_list, desc="Baixando EDIs"):
            try:
                yield SheetData(
                    nfe=int(line[0]),
                    data=line[1].replace("/", ""),
                    dest_id=line[2],
                    cidade=line[3],
                    valor_mercadoria=self.to_float(line[4]),
                    comissao=self.to_float(line[5]),
                    valor_frete=self.to_float(line[6]),
                    emissor=line[8]
                )
            except Exception as e:
                print(e)

    def auto_load_sheet_data(self)->list[SheetData]:
        sheets = self.get_sheets_files()
        doc = prompt(
            "Selecione o documento: ",
            completer=WordCompleter(sheets.keys())
        ),

        selected_sheet = sheets[doc[0]]
        folders = self.list_sheet_folders(selected_sheet)
        folder = prompt(
            "Selecione a pasta: ",
            completer=WordCompleter(folders)
        )

        init, end = map(int, input("Insira o range: ").split())
        
        sheet_data = self.getSheetData(
            sheet_id=selected_sheet,
            page_name=folder,
            sheet_range=f"A{init}:I{end}"
        )
        
        return list(sheet_data)