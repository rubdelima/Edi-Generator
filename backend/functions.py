# Global Imports
import os
import sys
import tqdm
from   halo      import Halo
from   tkinter   import filedialog
from   threading import Thread
from   prompt_toolkit import prompt
from   prompt_toolkit.completion import WordCompleter

# Local Imports
from   backend.docs     import EdiDoc
from   backend.edi      import generateNewDoc, separeDocs
from   backend.firebase import FirebaseStore
from   backend.items    import getCteItems
from   backend.models   import *
from   backend.sheets   import GoogleClient
from   backend.style    import cabecalho, cor
from   backend.xmls     import getXmlList

class Functions:
    def __init__(self, profile: Profile):
        self.profile = profile
        self.google = GoogleClient()
        self.fb = FirebaseStore()
        
        self.ano, self.mes = map(int, input("Insira o mês e o ano: ").split())

        thead_docs = Thread(target=self.load_docs)
        thead_docs.start()
        thread_data = Thread(target=self.load_data, args=(self.ano, self.mes))
        thread_data.start()

        self.current_sheet_list = []
        self.current_xml_list = []
        self.merged_list = []
        
        self.options = {
            '1. Adicionar dados da planilha' : self.load_sheets,
            '2. Adicionar xmls' : self.load_xmls,
            '3. Fazer merge dos dados atuais' : self.merge_data,
            '4. Adicionar dados da planilha e xlms e mesclar' : self.load_shert_xmls_and_merge,
            '5. Adicionar mesclados a docs' : self.save_merged,
            '6. Atualizar dados globais' : self.save_docs,
            '7. Gerar OCORREN' : self.generateOcorren,
            '8. Gerar DOCOB' :  self.generateDocob,
            '9. Baixar PDFs' : self.invalid,
            '10. Baixar XMLs e PDFs' : self.invalid,
            '11. Limpar Terminal' : self.clear,
            '12. Sair' : lambda : sys.exit(0)
        }
        
        thead_docs.join()
        thread_data.join()
    
    def load_docs(self):
        self.fb.load_all_docs()
        self.docs = self.fb.edis
        self.current_edi  = 0 if len(self.docs) > 0 else None

    def load_data(self, ano, mes):
        self.fb.load_database(ano, mes)
        self.month_items = self.fb.database
        self.current_data = 0 if len(self.month_items)  > 0 else None
        
    def run(self):
        self.menu()
        print(*self.options.keys(), sep='\n')
        self.options.get(
            prompt(completer=WordCompleter(self.options.keys())),
            self.invalid)()
    
    @staticmethod
    def clear():
        os.system('cls' if os.name == 'nt' else 'clear')
    
    @staticmethod
    def invalid():
        print(cor("Opção Inválida", 'vermelho'))
    
    def change_current(self, index, changedList):
        if index < len(changedList):
            self.current_data = index
            if isinstance (changedList[index], EdiDoc):
                print(f"O cursor atual da lista de docs é:")
                i : EdiDoc = changedList[index]
                print(f"Numero: {i.n_cobranca}, Destinario Nome: {i.destinatario_nome}, Destinario CNPJ: {i.destinatario_cpnj}")
                return
            
            i : CteItem = changedList[index]
            print(f" O cursor atual da lista de edis é\n{i}")
            return
        
        print(
            cor(
                "Não é possível alterar para esse endereço pois ele está além da quantidade",
                'vermelho'))
    
    def change_current_edi(self, index):
        if index < len(self.docs):
            self.current_edi = index
            print(f"")
            return
        
        print(
            cor(
                "Não é possível alterar para esse endereço pois ele está além da quantidade",
              'vermelho'))
    
    def menu(self):
        cabecalho("Terminal EDI", tam_cab=2, tom='azul')
        print(f"Total Xmls: {len(self.current_xml_list)}")
        print(f"Total Ymls: {len(self.current_sheet_list)}")
        print(f"Itens Combinados: {len(self.merged_list)}")
               
    def load_sheets(self):
        self.current_sheet_list = self.google.auto_load_sheet_data()
    
    def load_xmls(self, xml_path:str=None):
        xml_path = filedialog.askdirectory(title="Selecione a pasta que comtém os xmls") if xml_path is None else xml_path
        self.current_xml_list = list(getXmlList(xml_path))
    
    def merge_data(self):
        self.merged_list = list(getCteItems(self.current_xml_list, 
                                            self.current_sheet_list))
    
    def load_shert_xmls_and_merge(self):
        thr1 = Thread(target=self.load_sheets)
        path = filedialog.askdirectory(title="Selecione a pasta que comtém os xmls")
        thr2 = Thread(
            target=self.load_xmls,
            args=(path, )
        )
        thr1.start()
        thr2.start()
        thr1.join()
        thr2.join()
        self.merge_data()
    
    def save_merged(self):
        docs_list = list(map(str, self.docs.values()))
        new_docs = separeDocs(self.merged_list)
        
        for rem, rem_list in new_docs.items():
            doc_key = prompt(
                f"Selecione o Documento para o remetente {rem}",
                completer=WordCompleter(docs_list)
            )
            
            if doc_key in self.docs.keys():
                self.docs[doc_key].items_list.list.extend(rem_list)
                continue
            
            new_doc_id = int(input(f"Insira o número do documento de {rem}: "))
            self.docs[str(new_doc_id)] = generateNewDoc(
                rem=rem, rem_list=rem_list, n_cob=new_doc_id, profile=self.profile
            )
    
    def save_docs(self):
        self.fb.edis = self.docs
        self.fb.save_docs()
        self.fb.save_database(self.ano, self.mes)
    
    def getDocKey(self):
        for n_doc, doc in self.docs.items():
            print(doc)
    
        selected_doc = prompt(
            "Selecione o domcumento para emitir: ",
            completer=WordCompleter(self.docs.keys())
        )
        
        return selected_doc
            
    def generateDocob(self):
        selected_doc = self.getDocKey()
        if isinstance(self.docs.get(selected_doc), EdiDoc):
            self.docs[selected_doc].generateDocob()
            return
        print(cor("ID inválido", 'vermelho'))
    
    def generateOcorren(self, selected_doc):
        selected_doc = self.getDocKey()
        if isinstance(self.docs.get(selected_doc), EdiDoc):
            for i, edi in enumerate(self.docs[selected_doc].items_list.list):
                print("{:>3}|{}".format(i, edi))
            init, end = map(int, input("Insira o intervalo que deseja emitir: "))
            self.docs[selected_doc].generateDocob(init=init, end=end)
            return
        print(cor("ID inválido", 'vermelho'))
    