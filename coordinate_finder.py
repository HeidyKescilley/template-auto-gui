import pyautogui
import time
import json
import os

# Tenta carregar o path do config, mas define um fallback
try:
    from config import COORDINATE_MAP_FILE
except ImportError:
    COORDINATE_MAP_FILE = 'coordinates.json'

print("--- Ferramenta de Captura de Coordenadas ---")
print("Mova o mouse para a posição desejada.")
print("Pressione CTRL+C no terminal para salvar a posição atual.")

def load_coords():
    if os.path.exists(COORDINATE_MAP_FILE):
        try:
            with open(COORDINATE_MAP_FILE, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_coords(data):
    with open(COORDINATE_MAP_FILE, 'w') as f:
        json.dump(data, f, indent=4)
    print(f"\nCoordenadas salvas em {COORDINATE_MAP_FILE}")

coords_map = load_coords()
print(f"Mapa atual: {json.dumps(coords_map, indent=2)}")

last_pos = None
try:
    while True:
        pos = pyautogui.position()
        if pos != last_pos:
            print(f"Posição atual: {pos}", end='\r') 
            last_pos = pos
        time.sleep(0.1)
        
except KeyboardInterrupt:
    print(f"\nPosição final capturada: {last_pos}")
    name = input("Digite um nome para esta coordenada (ex: 'campo_usuario') ou 'pular': ")
    
    if name.lower() != 'pular' and name.strip() != "":
        coords_map[name] = [last_pos.x, last_pos.y]
        save_coords(coords_map)
    else:
        print("Coordenada descartada.")
        
print("Encerrando ferramenta.")