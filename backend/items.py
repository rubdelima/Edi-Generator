# Globals Imports
import sys
from   typing import Generator
from   tkinter import filedialog
from   prompt_toolkit import prompt
from   prompt_toolkit.completion import WordCompleter

# Local Imports
from backend.models import SheetData, CteXML, CteItem
from backend.sheets import getSheetData
from backend.style  import cor, cabecalho
from backend.xmls   import getXmlList

def mergeData(sheets:Generator[SheetData, None, None], xmls:list[CteXML], allData:bool=False)->Generator[CteItem, list[CteXML], None]:
    for sheet in sheets:
        is_valid = False
        cte, rem_cnpj, dest_id, peso, xml_path = None, None, None, None, None
        for xml in xmls: 
            if int(sheet.nfe) == int(xml.nfe):
                xmls.remove(xml)
                is_valid = sheet.valor_frete == xml.valor_frete
                is_valid = is_valid and (abs (sheet.valor_mercadoria - xml.valor_carga) < 2 )
                cte = xml.cte; rem_cnpj = xml.rem_cnpj; dest_id = xml.dest_id; peso = xml.peso; xml_path = xml.xml_path
                break
                          
        yield CteItem(
            nfe=sheet.nfe,
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
            texto='| {:>3} {} {:>5}'.format(i, item, pos),
            color='amarelo'
        ))
    
    print()
    
    cabecalho("XMLs Faltantes", tom='magenta')
    for xml in missed_xmls:
        print(cor(str(xml), color='magenta'))
    

def getCteItems()->list[CteItem]:
    table_address = input("Insrira o endereço da tabela: ")
    table_range = f"A1:I{input('Insira a quantidade de Itens: ')}"
    sheets = getSheetData(table_address, table_range)
    
    xml_path  = filedialog.askdirectory(title="Selecione a pasta que comtém os xmls")
    xmls      : list[CteXML]  = list(getXmlList(xml_path))
    
    merged    : list[CteItem] = list(mergeData(sheets, xmls, True))
    miss_xmls : list[CteXML]  = merged.pop(-1)
    
    miss_data : list[tuple[SheetData, int, str]] = []
    is_merged : bool = False
    
    while True:
        is_merged = True
        for i, line in enumerate(merged):
            print(cor(
                texto = "|{:>3} {}".format(i, str(line)),
                color='verde' if line.is_valid else'vermelho',
                reverse= not line.is_valid
            ))
            if not line.is_valid:
                is_merged = False
                possible_cte = merged[i-1] +1 if merged[i-1] - merged[(i + 1)%len(merged)] == -2 else ''
                    
                miss_data.append((line, i, possible_cte))
        
        if is_merged:
            break
        
        elif len(miss_xmls) != len(miss_data):
            cabecalho(
                "Erro: Não é possível continuar pois a quantidade de xmls restantes é menor que a de Sheets faltantes!",
                reverse= True,
                tom='vermelho'
            )
            show_misseds(miss_data, miss_xmls)
            sys.exit(1)

        cabecalho("Alguns Itens estão faltando", tom='amarelo', reverse=True)
        show_misseds(miss_data, miss_xmls)
        for item, i, pos in miss_data:
            print(cor(
                texto='| {:>3} {} {:>5}'.format(i, item, pos),
                color='amarelo'
            ))
            complete_xml = WordCompleter(list(map(str, miss_xmls)))
            selected_xml = prompt(completer=complete_xml)
            xml = next(filter(lambda x: str(x) == selected_xml, miss_xmls))
            miss_xmls.remove(xml)
            merged[i] = manualMerge(item, xml)
    return merged
            