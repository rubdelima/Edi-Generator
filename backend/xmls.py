# Global Imports
import xmltodict
import os
import tqdm
from   typing import Generator

# Local Imports
from backend.models import CteXML, loading


to_float = lambda value : round(float(value.replace(',', '.')), 2)

def getXmlData(filename:str)->CteXML:
    with open(filename, 'r') as f:
        xml_data = f.read()
    
    json_data = xmltodict.parse(xml_data, dict_constructor=dict)
    json_data = json_data = json_data['cteProc']['CTe']['infCte']
    
    errors_list : list[Exception] = []
    
    # Verificação do Valor do Frete
    try:
        vt_prest = json_data['vPrest']['vTPrest']
        vr_prest = json_data['vPrest']['vRec']
        vl_cobr  = json_data['infCTeNorm']['cobr']['fat']['vLiq']
        vo_cobr  = json_data['infCTeNorm']['cobr']['fat']['vOrig']
        
        assert ( vt_prest == vr_prest == vl_cobr == vo_cobr 
                ), (f"O valor da prestação ou frete é divergente:"+
                    f"\nValor Total da Prestação: {vt_prest}"+
                    f"\nValor a Receber da Prestação: {vr_prest}"+
                    f"\nValor da Cobrança Original: {vo_cobr}"+
                    f"\nValor da Cobrança Liquido: {vl_cobr}")
        
    except Exception as e:
        errors_list.append(e)
    
    # Verficação do Rememtente/Expedidor
    try:
        rem_id, rem_name = json_data['rem']['CNPJ'],   json_data['rem']['xNome'] 
        exp_id, exp_name = json_data['exped']['CNPJ'], json_data['exped']['xNome']
        
        assert ((rem_id == exp_id) and (rem_name == exp_name)
            ), ("Os dados do Remetente/Expedidor estão incorretos: "+
                f"\nCNPJ Remetente: {rem_id}, Nome Remetente: {rem_name}"+
                f"\nCNPJ Expedidor: {exp_id}, Nome Expedidor: {exp_name}")
    
    except Exception as e:
        errors_list.append(e)
    
    # Verificação do Destinatário/ Recebedor
    try:
        dest_id = json_data['dest']['CNPJ'] if 'CNPJ' in json_data['dest'].keys() else json_data['dest']['CPF']
        dest_name = json_data['dest']['xNome']
        receb_id = json_data['receb']['CNPJ'] if 'CNPJ' in json_data['receb'].keys() else json_data['dest']['CPF']
        receb_name = json_data['receb']['xNome']
        assert (dest_id == receb_id), (
            "Os dados do Destinatário/ Recebedor estão incorretos:" + 
            f"\nID Destinatário: {dest_id}, Nome Destinatário: {dest_name}" +
            f"\nID Recebedor: {receb_id}, Nome Recebedor: {receb_name}"  
        )
    except Exception as e:
        errors_list.append(e)
    
    try:
        cte_data = {
            'cte' : int(json_data['ide']['nCT']),
            'nfe' : int(json_data['infCTeNorm']['infDoc']['infNFe']['chave'][25:34]),
            'serie_nfe' : int(json_data['infCTeNorm']['infDoc']['infNFe']['chave'][22:25]),
            'rem_cnpj' : json_data['rem']['CNPJ'],
            'rem_nome' : json_data['rem']['xNome'],
            'dest_id' : dest_id,
            'dest_nome' : json_data['dest']['xNome'],
            'valor_frete' : float(vl_cobr),
            'valor_carga' : float(json_data['infCTeNorm']['infCarga']['vCarga']),
            'peso' : float(json_data['infCTeNorm']['infCarga']['infQ']['qCarga']),
            'xml_path' : filename
        }
        
        if len(errors_list) == 0:
            return CteXML(**cte_data)

    except Exception as e:
        errors_list.append(e)
    
    errors_list.insert(0, f'Um ou mais erros aconteceram no arquivo: {filename}: ')
    return errors_list

@loading("Carregando XMLs", "XMLs carregados")
def getXmlList(path:str)->Generator[CteXML, None, None]:
    files = [f for f in os.listdir(path) if f.endswith('.xml')]
    for filename in tqdm.tqdm(files, "Carregando XMLs"):
        try:
            xml_data = getXmlData(os.path.join(path, filename))
            if type(xml_data) == CteXML:
                yield getXmlData(os.path.join(path, filename))
                continue
        except Exception as e:
            print(e)