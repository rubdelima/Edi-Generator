from pydantic import BaseModel
from halo import Halo
from functools import wraps

def loading(loading_message="Processing", completion_message="Completed"):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            spinner = Halo(text=loading_message, spinner='dots')
            spinner.start()
            try:
                result = func(*args, **kwargs)
                spinner.stop_and_persist(symbol='\033[92m✔\033[0m', text=completion_message)
            except Exception as e:
                spinner.fail(f"\033[91m{str(e)}\033[0m")
                raise e
            return result
        return wrapper
    return decorator

class CteXML(BaseModel):
    cte : int
    nfe : int
    serie_nfe : int
    rem_cnpj : str
    rem_nome : str
    dest_id : str
    dest_nome : str
    valor_frete : float
    valor_carga : float
    peso : float
    xml_path : str
    
    def __str__(self):
        return "|{:>5}|{:>10}|{:>10}|{:>8}|{:>14}|".format(
            self.cte, self.nfe, self.valor_carga, self.valor_frete, self.rem_cnpj
        )

class XmlList(BaseModel):
    list : list[CteXML]

class SheetData(BaseModel):
    nfe : int
    data : str
    dest_id : str
    cidade : str
    valor_mercadoria : float
    comissao : float
    valor_frete : float
    emissor : str

class SheetList(BaseModel):
    list : list[SheetData]

class CteItem(BaseModel):
    cte : int | None
    nfe : int
    serie_nfe : int | None
    data : str
    rem_cnpj : str | None
    dest_id : str  | None
    valor_frete : float
    valor_carga : float
    peso : float | None
    xml_path : str | None
    is_valid : bool
    
    def __str__(self):
        cte = '' if self.cte is None else self.cte
        rem_cnpj = '' if self.rem_cnpj is None else self.rem_cnpj
        return "|{:>8} | {:<10} | {:>10} | {:>8} | {:>5}| {:^14} |".format(
            self.nfe, self.data, self.valor_carga, self.valor_frete, cte, rem_cnpj
        )
        
    def __add__(self, other):
        if isinstance(other, CteItem):
            return self.valor_frete + other.valor_frete
        return self.valor_frete + other
    
class CteList(BaseModel):
    list : list[CteItem]
    
    def ItemSum(self):
        val = 0
        for item in self.list:
            val += item.valor_frete
        return val

class Banco(BaseModel):
    agencia_bancaria_nome : str
    agencia_numero : str
    agencia_numero_ver : str
    cc_numero : str
    cc_verificador : str

    def getValues(self)->list[str]:
        return [self.agencia_bancaria_nome, self.agencia_numero,
                self.agencia_numero_ver, self.cc_numero, self.cc_verificador]

class Profile(BaseModel):
    nome : str
    cnpj : str
    bancos : list[Banco]