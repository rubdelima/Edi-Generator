import os
from   tkinter import filedialog
from   prompt_toolkit import prompt
from   prompt_toolkit.completion import WordCompleter

path     = filedialog.askdirectory(title="Selecione a pasta")
arquivos = WordCompleter(list(os.listdir(path)))
select   = prompt("Escolha o arquivo desejado: ", completer=arquivos)

print(f"Você selecionou o arquivo : {select}")