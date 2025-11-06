import tkinter as tk
from tkinter import simpledialog
import pyautogui
import os

# Tenta carregar o path do config, mas define um fallback
try:
    from config import IMAGE_DIR
except ImportError:
    print("Aviso: Não foi possível encontrar 'config.py'. Salvando em /images/")
    IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'images')
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

class RegionSelector:
    def __init__(self, root):
        self.root = root
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.root.attributes("-fullscreen", True)
        self.root.attributes("-alpha", 0.3)
        self.root.attributes("-topmost", True)
        self.root.overrideredirect(True)
        self.canvas = tk.Canvas(self.root, cursor="cross", bg="grey")
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.canvas.bind("<Button-1>", self.on_click)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.root.bind("<Escape>", self.cancel)
        self.root.bind("<Button-3>", self.cancel)

    def on_click(self, event):
        self.start_x = self.canvas.winfo_pointerx()
        self.start_y = self.canvas.winfo_pointery()
        self.rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y, 
            outline="red", width=2
        )

    def on_drag(self, event):
        cur_x = self.canvas.winfo_pointerx()
        cur_y = self.canvas.winfo_pointery()
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x = self.canvas.winfo_pointerx()
        end_y = self.canvas.winfo_pointery()
        self.root.withdraw() 
        
        left = min(self.start_x, end_x)
        top = min(self.start_y, end_y)
        width = abs(self.start_x - end_x)
        height = abs(self.start_y - end_y)
        region = (left, top, width, height)

        if width == 0 or height == 0:
            print("Seleção inválida. Cancelando.")
            self.root.destroy()
            return

        # Pede o nome
        root_dialog = tk.Tk()
        root_dialog.withdraw()
        root_dialog.attributes("-topmost", True)
        file_name = simpledialog.askstring(
            "Captura Inteligente", 
            "Digite o nome para esta imagem (sem .png):",
            parent=root_dialog
        )
        root_dialog.destroy()

        if file_name:
            if not file_name.endswith(".png"):
                file_name += ".png"
            file_path = os.path.join(IMAGE_DIR, file_name)
            try:
                pyautogui.screenshot(file_path, region=region)
                print(f"Sucesso! Imagem salva em: {file_path}")
            except Exception as e:
                print(f"Erro ao salvar screenshot: {e}")
        else:
            print("Captura cancelada.")
        self.root.destroy()

    def cancel(self, event=None):
        print("Captura cancelada pelo usuário.")
        self.root.destroy()

if __name__ == "__main__":
    print("Iniciando Capturador Inteligente...")
    print("Clique e arraste para selecionar uma região.")
    print("Pressione ESC ou clique com o botão direito para cancelar.")
    root = tk.Tk()
    app = RegionSelector(root)
    root.mainloop()