# Globals Imports
from   typing import Generator
from   prompt_toolkit import prompt
from   prompt_toolkit.completion import WordCompleter

# Local Imports
from backend.models import SheetData, CteXML, CteItem
from backend.style  import cor, cabecalho
from backend.xmls   import getXmlList

def getPossibleCte(merged: list, i: int):
    try:
        if merged[i-1].cte - merged[(i + 1)%len(merged)].cte == -2:
            return merged[i-1].cte +1
    except:
        pass
    return ''

def mergeData(sheets:Generator[SheetData, None, None], xmls:list[CteXML], allData:bool=False)->Generator[CteItem, list[CteXML], None]:
    for sheet in sheets:
        is_valid = False
        cte, serie_nfe, rem_cnpj, dest_id, peso, xml_path = None, None, None, None, None, None
        for xml in xmls: 
            if int(sheet.nfe) == int(xml.nfe):
                xmls.remove(xml)
                is_valid = sheet.valor_frete == xml.valor_frete
                is_valid = is_valid and (abs (sheet.valor_mercadoria - xml.valor_carga) < 2 )
                cte = xml.cte; rem_cnpj = xml.rem_cnpj; dest_id = xml.dest_id; peso = xml.peso; xml_path = xml.xml_path; serie_nfe = xml.serie_nfe
                break
                          
        yield CteItem(
            nfe=sheet.nfe,
            serie_nfe=serie_nfe,
            cte=cte,
            data=sheet.data,
            rem_cnpj=rem_cnpj,
            dest_id=dest_id,
            valor_frete=sheet.valor_frete,
            valor_carga=sheet.valor_mercadoria,
            peso=peso,
            xml_path=xml_path,    
            is_valid=is_valid
        )
        
    if allData:
        yield xmls

def manualMerge(sheet:SheetData, xml:CteXML)->CteItem:
    return CteItem(
        nfe=sheet.nfe,
        serie_nfe=xml.serie_nfe,
        cte=xml.cte,
        data=sheet.data,
        rem_cnpj=xml.rem_cnpj,
        dest_id=xml.dest_id,
        valor_frete=sheet.valor_frete,
        valor_carga=sheet.valor_mercadoria,
        peso=xml.peso,
        xml_path=xml.xml_path,    
        is_valid=True
        )
        
def show_misseds(missed_data:list[tuple[CteItem, int, str]] , missed_xmls:list[CteXML])->None:
    cabecalho("Sheets Faltantes", tom='amarelo', reverse=True)
    for item, i, pos in missed_data:
        print(cor(
            texto='| {:>3} {}'.format(i, item),
            color='amarelo'
        ))
    
    print()
    
    cabecalho("XMLs Faltantes", tom='magenta')
    for xml in missed_xmls:
        print(cor(str(xml), color='magenta'))
    
def getCteItems(xmls:list[CteXML], sheets:list[SheetData]  )->list[CteItem]:
    xml_path = 'C:/Users/rubin/Desktop/Trabalho/OCORREN/2024/Março'
    xmls      : list[CteXML]  = list(getXmlList(xml_path))
    
    merged    : list[CteItem] = list(mergeData(sheets, xmls, True))
    miss_xmls : list[CteXML]  = merged.pop(-1)
    
    
    
    while True:
        miss_data : list[tuple[SheetData, int, str]] = []
        is_merged : bool = True
        
        for i, line in enumerate(merged):
            print(cor(
                texto = "|{:>3} {}".format(i, str(line)),
                color='verde' if line.is_valid else'vermelho',
                reverse= not line.is_valid
            ))
            if not line.is_valid:
                is_merged = False
                possible_cte = getPossibleCte(merged, i)
                miss_data.append((line, i, possible_cte))
        
        if is_merged:
            break
        
        cabecalho("Alguns Itens estão faltando", tom='amarelo', reverse=True)
        show_misseds(miss_data, miss_xmls)
        for item, i, pos in miss_data:
            print(cor(
                texto='| {:>3} {}'.format(i, item),
                color='amarelo'
            ))
            complete_xml = WordCompleter(list(map(str, miss_xmls)))
            selected_xml = prompt(completer=complete_xml)
            xml = next(filter(lambda x: str(x) == selected_xml, miss_xmls))
            miss_xmls.remove(xml)
            merged[i] = manualMerge(item, xml)
    
    return merged
            