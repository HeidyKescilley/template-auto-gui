import pyautogui
import time
import os
import json
import logging
from datetime import datetime
from config import (
    GLOBAL_PAUSE, ENABLE_FAILSAFE, DEFAULT_CONFIDENCE, 
    DEFAULT_WAIT_TIMEOUT, CLICK_HISTORY_DIR, ENABLE_CLICK_HISTORY,
    CLICK_CAPTURE_PADDING, COORDINATE_MAP_FILE, LOG_FILE, LOG_LEVEL,
    LOG_DIR, IMAGE_DIR, DEFAULT_GRAYSCALE, ERROR_DIR, DEFAULT_DISAPPEAR_STABILITY
)

# --- 1. Setup Inicial e "Base de Logging" ---
def setup_automation():
    """Configura PyAutoGUI, Logging e cria todas as pastas necessárias."""
    pyautogui.PAUSE = GLOBAL_PAUSE
    pyautogui.FAILSAFE = ENABLE_FAILSAFE
    
    # Criar diretórios necessários
    for dir_path in [LOG_DIR, CLICK_HISTORY_DIR, IMAGE_DIR, ERROR_DIR]:
        if not os.path.exists(dir_path):
            try:
                os.makedirs(dir_path)
            except OSError as e:
                logging.critical(f"Erro fatal ao criar diretório {dir_path}: {e}")
                exit(1)
    
    # Configurar logging (para arquivo E console)
    logging.basicConfig(
        level=LOG_LEVEL,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )
    logging.info("--- Base de Logging Iniciada. Automação Pronta. ---")

# --- 2. Funções do "Mapa" de Coordenadas ---
def get_coords(name):
    """Busca uma coordenada nomeada do 'mapa' (coordinates.json)."""
    try:
        with open(COORDINATE_MAP_FILE, 'r') as f:
            data = json.load(f)
        coords = data.get(name)
        if coords and isinstance(coords, list) and len(coords) == 2:
            logging.debug(f"Coordenada '{name}' encontrada: {tuple(coords)}")
            return tuple(coords)
        else:
            logging.error(f"Coordenada '{name}' NÃO encontrada ou mal formatada no mapa.")
            return None
    except FileNotFoundError:
        logging.error(f"Arquivo de mapa '{COORDINATE_MAP_FILE}' não encontrado.")
        return None
    except json.JSONDecodeError:
        logging.error(f"Erro ao decodificar JSON em '{COORDINATE_MAP_FILE}'.")
        return None

# --- 3. Wrapper de Clique com Histórico ---
def safe_click(coords, log_message=""):
    """Realiza um clique seguro e registra no log e no histórico de screenshots."""
    if isinstance(coords, str):
        log_message = coords 
        coords = get_coords(coords)
        if not coords:
            logging.error(f"Falha ao clicar: Coordenada '{log_message}' não encontrada.")
            raise ValueError(f"Coordenada '{log_message}' não encontrada no mapa.")
    
    x, y = coords
    
    try:
        pyautogui.moveTo(x, y)
        pyautogui.click(x, y)
        logging.info(f"Clicado: '{log_message}' em ({x}, {y})")
        if ENABLE_CLICK_HISTORY:
            _capture_click_area(x, y, log_message)
    except Exception as e:
        logging.error(f"Erro ao tentar clicar em '{log_message}' ({x}, {y}): {e}")
        raise

def _capture_click_area(x, y, name_prefix=""):
    """Função interna para capturar screenshot ao redor do clique."""
    try:
        left = max(0, x - CLICK_CAPTURE_PADDING)
        top = max(0, y - CLICK_CAPTURE_PADDING)
        width = CLICK_CAPTURE_PADDING * 2
        height = CLICK_CAPTURE_PADDING * 2
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_prefix = "".join(c for c in name_prefix if c.isalnum() or c in (' ', '_')).rstrip()
        filename = f"{timestamp}_{safe_prefix}_{x}x{y}.png"
        filepath = os.path.join(CLICK_HISTORY_DIR, filename)
        pyautogui.screenshot(filepath, region=(left, top, width, height))
        logging.debug(f"Histórico de clique salvo: {filepath}")
    except Exception as e:
        logging.warning(f"Falha ao capturar screenshot do clique: {e}")

# --- 4. FUNÇÃO DE ESPERA (Sua Função Integrada) ---
def esperar_imagem(image_name: str, 
                   timeout_segundos: int = DEFAULT_WAIT_TIMEOUT, 
                   region: tuple = None, 
                   confianca: float = DEFAULT_CONFIDENCE,
                   grayscale: bool = DEFAULT_GRAYSCALE):
    """Aguarda até que uma imagem seja encontrada na tela, lançando TimeoutError se não encontrar."""
    caminho_imagem = os.path.join(IMAGE_DIR, image_name)
    
    if not os.path.exists(caminho_imagem):
        logging.error(f"Arquivo de imagem não encontrado: {caminho_imagem}")
        raise FileNotFoundError(f"Arquivo de imagem não encontrado: {caminho_imagem}")
    
    logging.info(f"Aguardando imagem: '{image_name}' (Timeout: {timeout_segundos}s, Confiança: {confianca})")
    
    inicio = time.time()
    while time.time() - inicio < timeout_segundos:
        try:
            # Localiza o CENTRO para ser compatível com o clique
            localizacao = pyautogui.locateCenterOnScreen(
                caminho_imagem, 
                confidence=confianca, 
                grayscale=grayscale, 
                region=region
            )
            if localizacao:
                logging.info(f"Imagem '{image_name}' encontrada em {localizacao}")
                return localizacao # Retorna as coordenadas (Point(x, y))
        except pyautogui.PyAutoGUIException:
            logging.debug("PyAutoGUIException temporária (ignorado).")
            pass 
        except Exception as e:
            if "confidence" in str(e):
                 logging.warning("Erro de 'confidence'. Tentando sem. Instale 'opencv-python' para melhor performance.")
                 confianca = 0.99
            else:
                 logging.error(f"Erro inesperado no locateOnScreen: {e}")
        time.sleep(0.5)
    
    time.sleep(1.5)
    logging.error(f"Timeout! Imagem '{image_name}' não foi encontrada em {timeout_segundos}s.")
    raise TimeoutError(f"A imagem '{image_name}' não foi encontrada em {timeout_segundos}s.")

def esperar_imagem_desaparecer(image_name: str, 
                               timeout_segundos: int = DEFAULT_WAIT_TIMEOUT, 
                               region: tuple = None, 
                               confianca: float = DEFAULT_CONFIDENCE,
                               grayscale: bool = DEFAULT_GRAYSCALE,
                               stability_check_sec: float = DEFAULT_DISAPPEAR_STABILITY):
    """
    Aguarda até que uma imagem NÃO seja mais encontrada na tela por um período
    estável, lançando TimeoutError se ela persistir.
    """
    caminho_imagem = os.path.join(IMAGE_DIR, image_name)
    
    if not os.path.exists(caminho_imagem):
        logging.warning(f"Arquivo de imagem não encontrado: {caminho_imagem}. Considerando 'desaparecida'.")
        return True 

    logging.info(f"Aguardando imagem DESAPARECER: '{image_name}' (Timeout: {timeout_segundos}s)")
    
    inicio = time.time()
    disappeared_timestamp = None 

    while time.time() - inicio < timeout_segundos:
        # 1. Reseta o status a cada loop
        image_found = False 
        
        try:
            # 2. Tenta localizar a imagem
            localizacao = pyautogui.locateCenterOnScreen(
                caminho_imagem, 
                confidence=confianca, 
                grayscale=grayscale, 
                region=region
            )
            if localizacao:
                # 3. SÓ SETA True SE REALMENTE ACHAR
                image_found = True

        except pyautogui.PyAutoGUIException:
            # Erro temporário de screenshot. Assume 'não encontrada' e deixa o loop tentar de novo.
            logging.debug("PyAutoGUIException (temporário) ao localizar. Tentando de novo...")
            # 'image_found' permanece False, o que é o correto
            
        except Exception as e:
            # CORREÇÃO: Erro inesperado (como tela minimizada). 
            # Loga o erro completo e assume 'não encontrada'.
            
            # (Adicionado exc_info=True para vermos o erro real, não só uma linha em branco)
            logging.error(f"Erro inesperado no locateOnScreen. Assumindo que a imagem sumiu.", exc_info=True)
            
            # 'image_found' permanece False, o que é o correto

        # --- Lógica de Estabilidade (Agora funciona com erros) ---
        
        if image_found:
            # IMAGEM ESTÁ VISÍVEL.
            # Reseta o timer de estabilidade.
            disappeared_timestamp = None
            logging.debug(f"Imagem '{image_name}' ainda está visível.")
        else:
            # IMAGEM NÃO ESTÁ VISÍVEL (ou um erro ocorreu)
            if disappeared_timestamp is None:
                # Primeira vez que não a vemos. Inicia o timer.
                logging.debug(f"Imagem '{image_name}' desapareceu (ou erro). Iniciando verificação de estabilidade...")
                disappeared_timestamp = time.time()
            else:
                # Já estamos na verificação.
                elapsed_since_disappeared = time.time() - disappeared_timestamp
                if elapsed_since_disappeared >= stability_check_sec:
                    # SUCESSO! A imagem sumiu (ou erro persistiu) pelo tempo de estabilidade.
                    logging.info(f"Imagem '{image_name}' desapareceu com sucesso (estável por {stability_check_sec}s).")
                    return True
        
        time.sleep(0.5)
        
    # Se o loop terminar (Timeout):
    logging.error(f"Timeout! Imagem '{image_name}' AINDA ESTÁ VISÍVEL após {timeout_segundos}s.")
    raise TimeoutError(f"A imagem '{image_name}' não desapareceu em {timeout_segundos}s.")

def imagem_esta_presente(image_name: str, 
                         timeout_segundos: int = DEFAULT_WAIT_TIMEOUT, 
                         region: tuple = None, 
                         confianca: float = DEFAULT_CONFIDENCE,
                         grayscale: bool = DEFAULT_GRAYSCALE) -> bool:
    """
    Verifica se uma imagem está presente na tela dentro do timeout.
    
    Retorna True se a imagem for encontrada a tempo.
    Retorna False se a imagem não for encontrada (Timeout) ou se o arquivo .png não existir.
    
    Esta função NUNCA lança um erro, permitindo o uso em condicionais (if/else).
    """
    try:
        # Tenta chamar sua função original 'esperar_imagem'
        # Se ela não lançar uma exceção, é porque encontrou a imagem.
        esperar_imagem(
            image_name, 
            timeout_segundos, 
            region, 
            confianca, 
            grayscale
        )
        # Se chegou até aqui, a imagem foi encontrada.
        logging.info(f"Verificação (imagem_esta_presente): Imagem '{image_name}' FOI encontrada.")
        return True
        
    except (TimeoutError, FileNotFoundError):
        # Captura os dois erros que 'esperar_imagem' pode lançar:
        # 1. TimeoutError: A imagem não apareceu.
        # 2. FileNotFoundError: O arquivo .png nem existe no diretório.
        
        # Em ambos os casos, a imagem "não está presente" para o robô.
        logging.info(f"Verificação (imagem_esta_presente): Imagem '{image_name}' NÃO foi encontrada (Timeout ou Arquivo Inexistente).")
        return False
        
    except Exception as e:
        # Captura qualquer outro erro inesperado (ex: problema de permissão)
        # para garantir que o script não quebre.
        logging.error(f"Erro inesperado ao verificar '{image_name}': {e}", exc_info=True)
        return False

# --- 5. Ações Combinadas ---
def find_and_click(image_name: str, 
                   timeout=DEFAULT_WAIT_TIMEOUT, 
                   confidence=DEFAULT_CONFIDENCE,
                   region=None,
                   grayscale=DEFAULT_GRAYSCALE):
    """Encontra uma imagem (usando esperar_imagem) e clica nela (usando safe_click)."""
    try:
        coords = esperar_imagem(image_name, timeout, region, confidence, grayscale)
        safe_click(coords, log_message=f"find_and_click: {image_name}")
        return True
    except (TimeoutError, FileNotFoundError):
        logging.warning(f"Não foi possível clicar em '{image_name}', pois não foi encontrada a tempo.")
        return False

def type_text(text, interval=0.05):
    """Digita texto de forma mais 'humana' (com intervalo)."""
    logging.info(f"Digitando: '{text[:20]}...'")
    pyautogui.write(text, interval=interval)

def click_relative(image_name: str, 
                            x: int, 
                            y: int, 
                            timeout=DEFAULT_WAIT_TIMEOUT, 
                            confidence=DEFAULT_CONFIDENCE,
                            region=None,
                            grayscale=DEFAULT_GRAYSCALE):
    """
    Encontra uma imagem-âncora e clica em um ponto relativo (offset) a ela.
    
    Ex: Encontra 'label_nome.png' e clica 150 pixels à direita (x=150).
    """
    logging.info(f"Tentando clique relativo: '{image_name}' com offset (x={x}, y={y})")
    
    try:
        # 1. Encontra o centro da imagem-âncora
        anchor_coords = esperar_imagem(
            image_name, 
            timeout_segundos=timeout, 
            confianca=confidence, 
            region=region, 
            grayscale=grayscale
        )
        
        # 2. Calcula as coordenadas do alvo
        # anchor_coords é um Point(x, y)
        target_x = anchor_coords.x + x
        target_y = anchor_coords.y + y
        
        target_coords = (target_x, target_y)
        
        # 3. Usa o safe_click para clicar no alvo (com log e histórico)
        log_msg = f"clique_relativo: {image_name} (+{x}, +{y})"
        safe_click(target_coords, log_message=log_msg)
        
        return True
        
    except (TimeoutError, FileNotFoundError):
        # O erro já foi logado por 'esperar_imagem'
        logging.warning(f"Imagem âncora '{image_name}' não encontrada. Clique relativo cancelado.")
        return False