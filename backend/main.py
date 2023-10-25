from backend.models import CteXML, CteData, SheetData
from backend.sheets import getSheetData
from backend.xml_cte import getXmlList
import json

def get_merge_data(s_success_list:list[SheetData], x_success_list:list[CteXML])->tuple[list[CteData],list]:
    
    d_success_list = []
    d_error_list = []

    for cteXml in x_success_list:
        for itemSheet in s_success_list:
            if int(cteXml.nfe) == int(itemSheet.nfe):
                d_success_list.append(CteData(
                    cte = cteXml.cte, 
                    nfe=cteXml.nfe, 
                    data=itemSheet.data,
                    rem_cnpj=cteXml.rem_cnpj, 
                    dest_id=itemSheet.dest_id,
                    valor_frete=itemSheet.valor_frete,
                    valor_carga=itemSheet.valor_mercadoria,
                    peso=cteXml.peso,
                    xml_path=cteXml.xml_path
                ))
                break
            if itemSheet == s_success_list[-1]:
                d_error_list.append(cteXml.model_dump())
    
    return d_success_list, d_error_list
    

def save_data(month:str, list_name:str, dict_data:list)->bool | tuple[tuple, Exception]:
    try:
        with open('./data/db.json', 'r') as db:
            db_data = json.load(db)

        if month not in db_data.keys():
            db_data[month] = {list_name : dict_data}
        elif list_name not in db_data[month].keys():
            db_data[month][list_name] = dict_data
        else:
            db_data[month][list_name].extend(dict_data)

        with open('./data/db.json', 'w') as output:
            json.dump(db_data, output, indent=4)
        
        return True

    except Exception as e:
        return False, e

def get_all_data(table_address:str, table_range:str, path:str)->tuple[
        list[CteXML],list[SheetData], list[CteData], list[str],list[str],list]:
    s_success_list, s_fail_list = getSheetData(table_address, table_range)
    x_success_list, x_fail_list = getXmlList(path)
    d_success_list, d_fail_list = get_merge_data(s_success_list, x_success_list)
    return (x_success_list, s_success_list, d_success_list,
        x_fail_list, s_fail_list, d_fail_list
    )
    
def load_data(month:str, list_name:str)->tuple[bool, list[SheetData|CteData|CteXML|str]|KeyError]:
    with open('./data/db.json', 'r') as data:
        dados = json.load(data)
    try:
        return True, dados[month][list_name]
    except KeyError as e:
        return False, e

