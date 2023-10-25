from backend.models import CteData, Docob
import datetime as dt
from datetime import datetime


def get_value(value: int | float | str, size: int) -> str:
    if type(value) == str:
        value = ''.join([i for i in value if i.isdigit()])
    elif type(value) == float:
        value = (value*100)//1
        value: int = int(value)

    s_value = '0'*(size - len(str(value)))
    s_value += str(value)
    return s_value


def getEdi(data: list[CteData], path: str, docob_data: Docob) -> bool:
    hora = datetime.now()

    linhas = []

    # Line 1

    linhas.append('000{:<35}{:<35}{:<10}COB{:<9}0'.format(
        docob_data.emissor_nome, docob_data.destinatario_nome,
        hora.strftime("%d%m%y%H%M"), hora.strftime("%d%m%H%M")
    ))

    # Line 2

    linhas.append(f'350COBRA{hora.strftime("%d%m%H%M")}1')

    # Line 3

    linhas.append('351{:<14}{:<40}'.format(
        docob_data.emissor_cnpj, docob_data.emissor_nome))

    valor_total = 0

    # Lines 5 and 6

    # @TODO: Remover o '0001'

    for cte in data:
        valor_total += cte.valor_frete * 100
        linhas.append(
            "353{:<14}{:<5}{:<12}{:<15}{:<8}{:<14}{:<14}{:<14}". format(
                docob_data.emissor_cnpj, '0001', cte.cte, get_value(
                    cte.valor_frete, 15),
                get_value(cte.data, 8), docob_data.destinatario_cnpj, get_value(
                    cte.dest_id, 14), docob_data.emissor_cnpj
            )
        )
        linhas.append(
            "354001{:<8}{:<8}{:<7}{:<15}".format(
                get_value(int(cte.nfe), 8), get_value(cte.data, 8),
                get_value(cte.peso, 7), get_value(cte.valor_carga, 15)
            )
        )

    # Line 4

    linhas.insert(3, "352{:<14}0{:<10}{:<8}{:<8}{:<15}000{:<15}{:<35}{:<4}{:1}{:<10}{:<2}I".format(
        docob_data.emissor_cnpj,

        docob_data.n_cobranca,
        hora.strftime('%d%m%Y'),
        (hora + dt.timedelta(days=15)).strftime('%d%m%Y'),
        get_value(int(valor_total), 15),

        get_value(docob_data.valor_icms, 15),
        *docob_data.dados_banco.getValues()
    )
    )

    # Line 7

    linhas.append("355{:<4}{:<15}".format(
        get_value(len(data), 4), get_value(int(valor_total), 15)))

    # doc = open(f'{path}/DOCOB{hora.strftime("%d%m%H%M")}.txt', 'w')
    with open('DOCOBTEST.txt', 'w') as output:
        for linha in linhas:
            print(f'{linha}{" "*(170-len(linha))}', file=output)
