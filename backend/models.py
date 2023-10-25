from pydantic import BaseModel

class CteXML(BaseModel):
    cte : str
    nfe : str
    emit_cnpj : str
    emit_nome : str
    rem_cnpj : str
    rem_nome : str
    dest_id : str
    dest_nome : str
    valor_frete : float
    valor_carga : float
    peso : float
    xml_path : str

class SheetData(BaseModel):
    nfe : str
    data : str
    dest_id : str
    cidade : str
    valor_mercadoria : float
    comissao : float
    valor_frete : float
    emissor : str

class CteData(BaseModel):
    cte : str
    nfe : str
    data : str
    rem_cnpj : str
    dest_id : str
    valor_frete : float
    valor_carga : float
    peso : float
    xml_path : str

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
    destinatario_cnpj : str
    emissor_nome : str
    emissor_cnpj : str
    valor_icms : int
    dados_banco : Banco


