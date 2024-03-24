from   backend.sheets import GoogleClient, getSheetData
from   prompt_toolkit import prompt
from   prompt_toolkit.completion import WordCompleter

if __name__ == '__main__':
    sc = GoogleClient()
    sheets = sc.get_sheets_files()
    print(sheets)
    doc = prompt(
        "Selecione o documento: ",
        completer=WordCompleter(sheets.keys())
    ),
    
    selected_sheet = sheets[doc[0]]
    print(selected_sheet)
    folders = sc.list_sheet_folders(selected_sheet)
    folder = prompt(
        "Selecione a pasta: ",
        completer=WordCompleter(folders)
    )
    
    init, end = map(int, input("Insira o range: ").split())
    sheet_data = getSheetData(
        client = sc,
        sheet_id= selected_sheet,
        page_name= folder,
        sheet_range= f"A{init}:I{end}"
    )
    
    sheet_data = list(sheet_data)
    print(len(sheet_data))