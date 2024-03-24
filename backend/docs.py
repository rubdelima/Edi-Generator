# Global Imports
from   pydantic import BaseModel
from   datetime import datetime
from   tkinter  import filedialog
import datetime as dt
import shutil
import json
import os

# Local Imports
from backend.models import Banco, CteList, CteItem

class EdiDoc(BaseModel):
    n_cobranca : int
    destinatario_nome : str
    destinatario_cnpj : str
    emissor_nome : str
    emissor_cnpj : str
    valor_icms : float
    items_list : CteList
    dados_banco : Banco | None = None
    qnt_notas : int | None = 0
    valor_doc : float | None = 0
    emitido : bool=False
    
    def __str__(self):
        return '| {:<4} | {:>10} | {:>10} | {:>14}'.format(
            self.n_cobranca, self.valor_doc, self.destinatario_nome, self.destinatario_cnpj, 
        )
    
    @staticmethod
    def get_value(value: int | float | str, size: int) -> str:
        if type(value) == str:
            value = ''.join([i for i in value if i.isdigit()])
        elif type(value) == float:
            value = (value*100)//1
            value: int = int(value)

        s_value = '0'*(size - len(str(value)))
        s_value += str(value)
        return s_value
    
    @staticmethod
    def printDoc(line:str, size:int, file)->None:
        print(line if len(line) < size else f"{line}{''*(size - len(line))}", file=file)
        
    @staticmethod
    def getRandomData(data:str):
        dia, mes, ano = map(int, [data[0:2], data[2:4], data[4:]])
        dian = (dia + 1) % 28
        mesn = mes if dian > dia else mes + 1
        anon = ano if mesn > mes else ano + 1
        return f'{dian}{mesn}{anon}'
    
    def addDocob(self, *items_list:CteItem):
        self.items_list.list.extend(items_list)
        
    def refresh(self):
        self.qnt_notas = len(self.items_list.list)
        self.valor_doc = self.items_list.ItemSum()
    
    def get_path(self):
        path = filedialog.askdirectory(title=f"Escolha o local para salvar os documentos de {self.destinatario_nome}")
        return path
    
    def generateDocs(self, path:str=None, seq=0):
        if path is None: path = self.get_path()
        hora = datetime.now()
        cob  = open(path + '/DOCOB'   + hora.strftime("%d%m%y%H%M") + f'{seq}.txt', 'w')
        oco  = open(path + '/OCORREN' + hora.strftime("%d%m%y%H%M") + f'{seq}.txt', 'w')
        
        valor_total = self.get_value(int(self.valor_doc*100), 15)
        
        # Linha 1 - DOCOB
        self.printDoc(
        '000{:<35}{:<35}{:<10}COB{:<8}{:<1}'.format(
        self.emissor_nome, self.destinatario_nome,
        hora.strftime("%d%m%y%H%M"), hora.strftime("%d%m%H%M"), seq
        ), 170, file=cob)
        
        # Linha 1 - Ocorren
        self.printDoc(
            '000{:<35}{:<35}{:<10}OCO{:<8}{:<1}'.format(
                self.emissor_nome, self.destinatario_nome,
                hora.strftime("%d%m%y%H%M"), hora.strftime("%d%m%H%M"), seq
        ), 120, file=oco)
        
        # Linha 2 - DOCOB
        self.printDoc(f'350COBRA{hora.strftime("%d%m%H%M")}{seq}', 170, file=cob)
        
        # Linha 2 - Ocorren
        self.printDoc(f'340OCORR{hora.strftime("%d%m%H%M")}{seq}', 120, file=oco)
        
        # Linha 3 - DOCOB
        self.printDoc('351{:<14}{:<40}'.format(self.emissor_cnpj, self.emissor_nome), 170, file=cob)
        
        # Linha 3 - Ocorren
        self.printDoc('341{:<14}{:<40}'.format(self.emissor_cnpj, self.emissor_nome), 120, file=oco)
        
        # Linha 4 - DOCOB
        dados_banco = self.dados_banco.getValues() if self.dados_banco is not None else ['', '', '', '', '']
        
        self.printDoc("352{:<10}0001{:>10}{:^8}{:^8}{:>15}000{:>15}{:>38}{:<35}{:^4}{:<1}{:<10}{:<2}I".format(
        self.emissor_nome,                                  # Filial Emissora
        self.get_value(self.n_cobranca,10),                 # Serie do Documento
        hora.strftime('%d%m%Y'),                            # Data Emissao
        (hora + dt.timedelta(days=15)).strftime('%d%m%Y'),  # Data Validade
        valor_total,                                        # Valor Documento
        self.get_value(self.valor_icms, 15),                # Valor ICMS
        '',
        *dados_banco), 170, file=cob)
        
        
        for item in self.items_list.list:
            # Linhas 5 e 6 - DOCOB
            self.printDoc(
            "353{:<10}00001{:>12}{:<15}{:<8}{:<14}{:<14}{:<14}". format(
                self.emissor_nome, 
                self.get_value(item.cte, 12), self.get_value(item.valor_frete, 15),
                "", item.rem_cnpj, self.get_value(item.dest_id, 14), self.emissor_cnpj
            ), 170, file=cob)
            
            self.printDoc(
            "354{:>3}{:<8}{:<8}{:<7}{:<15}{:<14}".format(
                self.get_value(item.serie_nfe, 3),
                self.get_value(item.nfe, 8), self.get_value(item.data, 8),
                self.get_value(item.peso, 7), self.get_value(item.valor_carga, 15),
                item.rem_cnpj
            ), 170, file=cob)
            
            # Linhas 4 do OCORREN
            rd = self.getRandomData(item.data)
            self.printDoc(
                "342{:<14}{:<3}{:<8}00{:<8}1100  {:<70}".format(
                self.destinatario_cnpj, self.get_value(item.serie_nfe, 3), self.get_value(item.nfe, 8),
                rd, 'Processo de Transporte já Iniciado', rd,
                ), 120, file=oco)
            
            self.printDoc(
                "342{:<14}{:<3}{:<8}01{:<8}1100  {:<70}".format(
                self.destinatario_cnpj, self.get_value(item.serie_nfe, 3), self.get_value(item.nfe, 8),
                rd, 'Entrega Realizada Normalmente', rd,
                ), 120, file=oco)
            
            pn = item.xml_path[:-12] + '.pdf'
            if os.path.exists(item.xml_path) and os.path.exists(pn):
                filename = item.xml_path.split('\\')[-1][:-3]
                shutil.copyfile(item.xml_path, path+'/'+filename + 'xml')
                shutil.copyfile(pn, path+'/'+filename + 'pdf')
            
        # Linha 7 - DOCOB
        self.printDoc("355{:<4}{:<15}".format(
            self.get_value(len(self.items_list.list), 4),
            self.get_value(int(valor_total), 15)
        ), 170, file=cob)
        
        cob.close()
        oco.close()
        
        jret = open(path + '/EDI' + hora.strftime("%d%m%y%H%M") + f'{seq}.json', 'w')
        json.dump(self.model_dump(), jret, indent=4)
        jret.close()
    
    def generateOcorren(self, path:str=None, init:int=0, end:int=None,  seq:int=0):
        if path is None: path = self.get_path()
        hora = datetime.now()
        oco  = open(path + '/OCORREN' + hora.strftime("%d%m%y%H%M") + f'{seq}.txt', 'w')

        # Linha 1 - Ocorren
        self.printDoc(
            '000{:<35}{:<35}{:<10}OCO{:<8}{:<1}'.format(
                self.emissor_nome, self.destinatario_nome,
                hora.strftime("%d%m%y%H%M"), hora.strftime("%d%m%H%M"), seq
        ), 120, file=oco)
        
        # Linha 2 - Ocorren
        self.printDoc(f'340OCORR{hora.strftime("%d%m%H%M")}{seq}', 120, file=oco)
        
        # Linha 3 - Ocorren
        self.printDoc('341{:<14}{:<40}'.format(self.emissor_cnpj, self.emissor_nome), 120, file=oco)
       
        for item in self.items_list.list[init:end]:          
            # Linhas 4 do OCORREN
            rd = self.getRandomData(item.data)
            self.printDoc(
                "342{:<14}{:<3}{:<8}00{:<8}1100  {:<70}".format(
                self.destinatario_cnpj, self.get_value(item.serie_nfe, 3), self.get_value(item.nfe, 8),
                rd, 'Processo de Transporte já Iniciado', rd,
                ), 120, file=oco)
            
            self.printDoc(
                "342{:<14}{:<3}{:<8}01{:<8}1100  {:<70}".format(
                self.destinatario_cnpj, self.get_value(item.serie_nfe, 3), self.get_value(item.nfe, 8),
                rd, 'Entrega Realizada Normalmente', rd,
                ), 120, file=oco)
        oco.close()
    def generateDocob(self, path=None, seq=0):
        if path is None: path = self.get_path()
        hora = datetime.now()
        cob  = open(path + '/DOCOB'   + hora.strftime("%d%m%y%H%M") + f'{seq}.txt', 'w')
        
        valor_total = self.get_value(int(self.valor_doc*100), 15)

        # Linha 1 - DOCOB
        self.printDoc(
        '000{:<35}{:<35}{:<10}COB{:<8}{:<1}'.format(
        self.emissor_nome, self.destinatario_nome,
        hora.strftime("%d%m%y%H%M"), hora.strftime("%d%m%H%M"), seq
        ), 170, file=cob)
        
         # Linha 2 - DOCOB
        self.printDoc(f'350COBRA{hora.strftime("%d%m%H%M")}{seq}', 170, file=cob)
        
        # Linha 3 - DOCOB
        self.printDoc('351{:<14}{:<40}'.format(self.emissor_cnpj, self.emissor_nome), 170, file=cob)
        
                # Linha 4 - DOCOB
        dados_banco = self.dados_banco.getValues() if self.dados_banco is not None else ['', '', '', '', '']
        
        self.printDoc("352{:<10}0001{:>10}{:^8}{:^8}{:>15}000{:>15}{:>38}{:<35}{:^4}{:<1}{:<10}{:<2}I".format(
        self.emissor_nome,                                  # Filial Emissora
        self.get_value(self.n_cobranca,10),                 # Serie do Documento
        hora.strftime('%d%m%Y'),                            # Data Emissao
        (hora + dt.timedelta(days=15)).strftime('%d%m%Y'),  # Data Validade
        valor_total,                                        # Valor Documento
        self.get_value(self.valor_icms, 15),                # Valor ICMS
        '',
        *dados_banco), 170, file=cob)
        
        for item in self.items_list.list:
            # Linhas 5 e 6 - DOCOB
            self.printDoc(
            "353{:<10}00001{:>12}{:<15}{:<8}{:<14}{:<14}{:<14}". format(
                self.emissor_nome, 
                self.get_value(item.cte, 12), self.get_value(item.valor_frete, 15),
                "", item.rem_cnpj, self.get_value(item.dest_id, 14), self.emissor_cnpj
            ), 170, file=cob)
            
            self.printDoc(
            "354{:>3}{:<8}{:<8}{:<7}{:<15}{:<14}".format(
                self.get_value(item.serie_nfe, 3),
                self.get_value(item.nfe, 8), self.get_value(item.data, 8),
                self.get_value(item.peso, 7), self.get_value(item.valor_carga, 15),
                item.rem_cnpj
            ), 170, file=cob)
            
        # Linha 7 - DOCOB
        self.printDoc("355{:<4}{:<15}".format(
            self.get_value(len(self.items_list.list), 4),
            self.get_value(int(valor_total), 15)
        ), 170, file=cob)
        
        cob.close()
        