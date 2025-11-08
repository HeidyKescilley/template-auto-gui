import os
import logging

# --- Configurações Gerais de Comportamento ---
GLOBAL_PAUSE = 0.4
ENABLE_FAILSAFE = True

# --- Configurações de Paths (Caminhos) ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IMAGE_DIR = os.path.join(BASE_DIR, 'images')
LOG_DIR = os.path.join(BASE_DIR, 'logs')
CLICK_HISTORY_DIR = os.path.join(BASE_DIR, 'click_history')
ERROR_DIR = os.path.join(BASE_DIR, 'error_screenshots')
COORDINATE_MAP_FILE = os.path.join(BASE_DIR, 'coordinates.json')

# --- Configuração de Logging (Sua "Base de Logging") ---
LOG_FILE_NAME = 'automation.log'
LOG_FILE = os.path.join(LOG_DIR, LOG_FILE_NAME)
LOG_LEVEL = logging.INFO # Mude para logging.DEBUG para logs mais detalhados

# --- Configurações do Histórico de Cliques ---
ENABLE_CLICK_HISTORY = True
CLICK_CAPTURE_PADDING = 50 

# --- Configurações de Notificação ---
TELEGRAM_ENABLED = True # Mude para False para desabilitar globalmente
TELEGRAM_NOTIFICATION_TITLE = "Alerta de Automação RPA" # Título da notificação

# --- Configurações de Reconhecimento de Imagem ---
DEFAULT_CONFIDENCE = 0.9
DEFAULT_WAIT_TIMEOUT = 30
DEFAULT_GRAYSCALE = True
DEFAULT_DISAPPEAR_STABILITY = 0.5 # <-- ADICIONE ESTA LINHA (Tempo em seg. para confirmar que a imagem sumiu)