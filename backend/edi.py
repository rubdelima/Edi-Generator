# Global Imports
from   itertools      import groupby
from   datetime       import datetime as dt
from   typing         import Generator
from   prompt_toolkit import prompt
from   prompt_toolkit.completion import WordCompleter

# Local Imports
from   backend.models import CteItem, CteList, Profile
from   backend.style  import cor, cabecalho
from   backend.docs  import EdiDoc

def generateNewDoc(rem:str, rem_list:list[CteItem],n_cob:int,  profile:Profile)->Generator[EdiDoc, None, None]:
    rem_list : list[CteItem]
    doc = EdiDoc(
        n_cobranca=n_cob,
        destinatario_nome=input(f"Insira o nome do destinatário {rem}: "),
        destinatario_cnpj=rem,
        emissor_nome=profile.nome,
        emissor_cnpj=profile.cnpj,
        valor_icms=0.0,
        items_list=CteList(list=rem_list)
    )
    doc.refresh()
    return doc

def separeDocs(items:list[CteItem])->dict[str, list[CteItem]]:
    """
    Return a list of diffs docs
    """
    key = lambda x : x.rem_cnpj
    docs = groupby(sorted(items, key=key), key=key)
    docs = {key: list(value) for key, value in docs}
    while True:
        for rem in docs.keys():
            elementos : list[CteItem] = list(docs[rem])
            cabecalho(f'Documentos para {rem}: ')
            print(f"Quantidade de Elementos: {len(elementos)}")
            print(f"Valor do Documento: {sum(map(lambda x : x.valor_frete, elementos))}")
            print("Exemplos de Elementos:")
            for i in range(min(len(elementos), 3)):
                print(elementos[i])

        match(input("Escolha uma opção:\n1) Continuar\n2) Mesclar\nAny) Ver Novamente\n")):
            case '1' : break
            case '2' :
                base   = prompt("Qual emissor que você deseja mesclar? ", completer=WordCompleter(list(docs.keys())))
                target = prompt("Para qual emissor que você deseja mesclar? ", completer=WordCompleter(set(docs.keys()) - {base}))
                docs[target].extend(docs[base])
                del docs[base]
            case _ : pass
    return docs