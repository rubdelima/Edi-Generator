from backend.main import get_all_data, save_data, load_data, CteData
from backend.edi import getEdi
from backend.models import Docob, Banco
import os

cte_xml, sheet_data, cte_data, l1, l2, l3 = get_all_data('1XZpMTcg1lEL8vrZN17visNt2XSfBL-cKQcp2r7TIt58', 'a1:i199' , 'C:\\Users\\rubenslima\\Desktop\\Trabalho\\OCORREN\\2023\Setembro\\10158356001930')

save_data('Setembro', 'Sheet_Data', [c.model_dump() for c in sheet_data])


_ , data = load_data('Setembro', 'Cte_Data')
n_data = [CteData(**d) for d in data]
docob_data = Docob( n_cobranca=30, 
                   destinatario_cnpj='10158356001930',
                   destinatario_nome='CPX DISTRIBUIDORA SA',
                   emissor_nome= 'CSRG TRANSPORTES LTDA',
                   emissor_cnpj= '46811890000112',
                   valor_icms= 0,
                   dados_banco=Banco(agencia_bancaria_nome='Cora SCD - 403',
                                     agencia_numero= '0001',
                                     agencia_numero_ver= '1',
                                     cc_numero='2666201',
                                     cc_verificador='8')
                   )


#getEdi(n_data, os.getcwd(), docob_data)

print(docob_data.model_dump())
print(docob_data.model_dump_json())