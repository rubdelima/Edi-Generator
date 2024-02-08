from pydantic import BaseModel

class CteXML(BaseModel):
    cte : int
    nfe : int
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
    
class CteList(BaseModel):
    list : list[CteItem]

class Banco(BaseModel):
    agencia_bancaria_nome : str
    agencia_numero : str
    agencia_numero_ver : str
    cc_numero : str
    cc_verificador : str

    def getValues(self)->list[str]:
        return [self.agencia_bancaria_nome, self.agencia_numero,
                self.agencia_numero_ver, self.cc_numero, self.cc_verificador]

class Docob(BaseModel):
    n_cobranca : int
    destinatario_nome : str
    destinatario_cnpf : str
    emissor_nome : str
    emissor_cnpj : str
    valor_icms : float
    dados_banco : Banco
    items_list : CteList
    qnt_notas : int
    valor_doc : float
    