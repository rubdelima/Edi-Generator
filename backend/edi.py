# Global Imports


# Local Imports
from backend.items  import getCteItems
from backend.models import CteItem, CteList, Banco, Docob
from backend.style  import cor, cabecalho

def generateDocs(items:list[CteItem]):
    items_sum = round(sum(items, lambda x: x.valor_frete), 2)
    