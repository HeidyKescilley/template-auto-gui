from automation_helpers import (
    setup_automation, 
    safe_click, 
    find_and_click, 
    type_text,
    esperar_imagem,
    esperar_imagem_desaparecer
)
import time

esperar_imagem('cnpj_input.png')
print('apareceu')
esperar_imagem_desaparecer('cnpj_input.png')
print('sumiu...')
