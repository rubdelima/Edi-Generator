tonalidade = {
    'preto': '\033[1;30m',
    'cinza-claro': '\033[1;37m',
    'cinza-escuro': '\033[1;90m',
    'vermelho': '\033[1;91m',
    'verde': '\033[1;92m',
    'amarelo': '\033[1;93m',
    'azul': '\033[1;94m',
    'magenta': '\033[1;95m',
    'cyan': '\033[1;96m',
    'branco': '\033[1;97m'
}
def cor(texto, color=None, reverse=False, bold=False):
    texto = tonalidade.get(color,"\033[0;0m") + texto
    texto = "\033[;1m"+texto if bold else texto
    texto = "\033[;7m"+texto if reverse else texto
    return texto +"\033[0;0m"

def cabecalho(texto, tam_cab=1, tom=None, reverse=False):
    for i in range(tam_cab):
        print(cor(f"{'-'*80}", tom, reverse))
    print(cor(f'|{str(texto).center(78)}|', tom, reverse))
    for j in range(tam_cab):
        print(cor(f"{'-'*80}", tom, reverse))
