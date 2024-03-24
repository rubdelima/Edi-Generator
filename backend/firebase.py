# Global Imports
import copy
import tqdm
import firebase_admin
from   firebase_admin import firestore, storage, credentials
from   halo           import Halo

# Local Imports
from   backend.models import CteItem, loading
from   backend.docs   import EdiDoc
from   backend.style  import cor

class FirebaseStore:
    cred   : credentials.Certificate
    db     : firestore.Client
    
    def __init__(self):
        self.cred = credentials.Certificate('./backend/json/firebase_key.json')
        firebase_admin.initialize_app(self.cred,{
            'storageBucket' : 'gs://edi-database.appspot.com'
        })
        self.db = firestore.client()
        self.bucket = storage.bucket()
        self.database = {}
        self.backup_database = {}
        self.edis = self.load_all_docs()
        self.backup_edis = {}
        
    @loading("Carregando Database", "Database Carregada")
    def load_database(self, ano, mes):
        docs = self.db.collection(f'{ano}_{mes}').stream()
        self.database =  {doc.to_dict()['cte'] : CteItem.from_dict(doc.to_dict()) for doc in docs}
        self.backup_database  = copy.deepcopy(self.database)
        
    @loading("Carregando Todos os EDIs", "Todos os EDIs foram carregados")
    def load_all_docs(self)->dict[str, EdiDoc]:
        docs = self.db.collection("EDI").stream()
        self.edis =  {doc.to_dict()['n_cobranca'] : EdiDoc(**doc.to_dict()) for doc in docs}
        self.backup_edis = copy.deepcopy(self.edis)
        
    def load_doc(self, number)->EdiDoc:
        sp = Halo(text= f"Carregando o EDI {number}", spinner='dots')
        sp.start()
        doc = self.db.collection("EDI").get(f'{number}')
        if doc:
            sp.stop_and_persist(symbol='\033[92m✔\033[0m', text=cor(f'EDI {number} carregado com sucesso!', color='verde'))
            return EdiDoc.from_dict(doc.to_dict())
        sp.fail(f"Não foi possível carregar o EDI {number}")
    
    def save_doc(self, doc: EdiDoc):
        sp = Halo(text= f"Carregando o EDI {doc.n_cobranca}", spinner='dots')
        doc_ref = self.db.collection("EDI").document(str(doc.number))
        doc_ref.set(doc.model_dump())
        sp.stop_and_persist(symbol='\033[92m✔\033[0m', text=cor(f'EDI {doc.n_cobranca} foi salvo com sucesso!', color='verde'))
        
    def get_cte_list(self)->list[CteItem]:
        return self.database.values()
    
    def get_edis_list(self)->list[EdiDoc]:
        return self.edis.values()
    
    def set_ctes(self, *args:CteItem):
        for arg in args:
            if isinstance(arg, CteItem):
                arg : CteItem
                self.database[arg.cte] = arg
    
    def set_edis(self, *args:EdiDoc):
        for arg in args:
            if isinstance(arg, EdiDoc):
                arg : EdiDoc
                self.edis[arg.n_cobranca] = arg
    
    
    def save_database(self, ano, mes):
        spinner = Halo(text=f'Salvando na Database {ano}_{mes}', spinner='dots')
        spinner.start()
        collection_ref = self.db.collection(f'{ano}_{mes}')
        
        for cte, item in tqdm.tqdm(self.database.items(),desc="Atualizando o banco de dados"):
            if self.backup_database.get(cte) == item: continue
            
            #self.upload_archives(ano, mes, item)
            doc_ref = collection_ref.document(str(cte))
            item : CteItem
            doc_ref.set(item.model_dump())
        
        [collection_ref.document(str(cte)).delete() for cte in self.backup_database.keys() if cte not in self.database.keys()]
        spinner.stop_and_persist(symbol='\033[92m✔\033[0m', text=cor('Database {ano}_{mes} atualizada com sucesso', 'verde'))

    @loading("Salvando EDIs...", "EDIs salvos com sucesso!")
    def save_docs(self):
        collection_ref = self.db.collection("EDI")
        for n_doc, doc in self.edis.items():
            if self.backup_edis.get(n_doc) == doc: continue
            print(f"Oiiii, {n_doc} {doc}")
            doc_ref = collection_ref.document(str(n_doc))
            doc_ref.set(doc.model_dump())
        
        [collection_ref.document(str(doc)).delete() for doc in self.backup_edis.keys() if doc not in self.edis.keys()]

                
    def upload_archives(self, ano: int, mes: str, item: CteItem):
        blob_path = f"{ano}/{mes}/{item.cte}"
        
        if item.xml_path:
            xml_blob = self.bucket.blob(blob_path+'/xml')
            xml_blob.upload_from_filename(item.xml_path)
            item.xml_path = xml_blob.public_url
        
        if item.pdf_path:
            pdf_blob = self.bucket.blob(blob_path+'/pdf')
            pdf_blob.upload_from_filename(item.pdf_path)
            item.pdf_path = pdf_blob.public_url
        
    def download_archive(self, ano, mes, cte):
        octe_object = self.database.get(cte, None)
        if octe_object:
            # Faça o download dos arquivos e escolha uma pasta para salvar
            pass
        
    def download_all_archives(self, ano, mes):
        # Abrir seleção da pasta de destino
        for cte in self.database:
            # Fazer download dos arquivos
            # Aparecer no terminal uma barrinha de baixando enquanto estiver baixando ex:
            # |===>        |(20%(4/20))
            pass