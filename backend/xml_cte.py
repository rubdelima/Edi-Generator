import xmltodict
from backend.models import CteXML
import os

def to_float(value:str)->float:
    value = value.replace(',', '.')
    return round(float(value), 2)

def getXmlData(filename:str)->tuple[False, dict]|tuple[True, CteXML]:
    with open(filename, "r") as file:
        xml_data = file.read()

    json_data = xmltodict.parse(xml_data, dict_constructor=dict)

    json_data = json_data['cteProc']['CTe']['infCte']

    errorList = []

    if json_data['vPrest']['vTPrest'] == json_data['vPrest']['vRec'] == json_data['infCTeNorm']['cobr']['fat']['vLiq'] == json_data['infCTeNorm']['cobr']['fat']['vOrig'] :
        valor_frete = json_data['vPrest']['vTPrest']
    else:
        errorList.append('Valor do frete é diferente')

    if not((json_data['rem']['CNPJ'] == json_data['exped']['CNPJ']) and (json_data['rem']['xNome'] == json_data['exped']['xNome'])) :
        errorList.append('Emissor é diferente do Remetente')

    dest_id = json_data['dest']['CNPJ'] if 'CNPJ' in json_data['dest'].keys() else json_data['dest']['CPF']
    receb_id = json_data['receb']['CNPJ'] if 'CNPJ' in json_data['receb'].keys() else json_data['dest']['CPF']
    
    if not ((dest_id == receb_id) and (json_data['dest']['xNome'] == json_data['receb']['xNome'])) :
        errorList.append('Emissor é diferente do Remetente')

    if  len(errorList) > 0:
        return False, {'errors' : errorList}
    
    cte_data = {
        'cte' : json_data['ide']['nCT'],
        'nfe' : json_data['infCTeNorm']['infDoc']['infNFe']['chave'][25:34],
        'emit_cnpj' : json_data['emit']['CNPJ'],
        'emit_nome' : json_data['emit']['xNome'],
        'rem_cnpj' : json_data['rem']['CNPJ'],
        'rem_nome' : json_data['rem']['xNome'],
        'dest_id' : dest_id,
        'dest_nome' : json_data['dest']['xNome'],
        'valor_frete' : float(valor_frete),
        'valor_carga' : float(json_data['infCTeNorm']['infCarga']['vCarga']),
        'peso' : float(json_data['infCTeNorm']['infCarga']['infQ']['qCarga']),
        'xml_path' : filename
    }

    return True, CteXML(**cte_data)

def getXmlList(path:str)->tuple[list[CteXML], list[str]]:
    success_list = []
    error_list = []

    for xml_file in os.listdir(path):
        try:
            if xml_file.endswith(".xml"):
                success, data = getXmlData(f'{path}/{xml_file}')
                if success : 
                    success_list.append(data)
                else:
                    error_list.append(xml_file)
        except Exception as e:
            print(e)
            error_list.append(xml_file)

    return success_list, error_list