import os
import logging
import time
import requests
import pyautogui as pg
from datetime import datetime
from collections import deque
from config import (
    ERROR_DIR, LOG_FILE, TELEGRAM_ENABLED, 
    TELEGRAM_NOTIFICATION_TITLE
)

# --- 1. Funções de Leitura de Log ---
def get_last_log_lines(n_lines=15) -> str:
    """Lê e retorna as N últimas linhas do arquivo de log para diagnóstico."""
    try:
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            last_lines = deque(f, n_lines)
        return "".join(last_lines)
    except FileNotFoundError:
        return "Arquivo de log não encontrado."
    except Exception as e:
        return f"Erro ao ler o arquivo de log: {e}"

# --- 2. Funções de Captura de Erro ---
def salvar_screenshot_erro(motivo: str, region: tuple = None) -> list:
    """Salva screenshots de erro e retorna uma lista com os caminhos dos arquivos."""
    if not os.path.exists(ERROR_DIR):
        os.makedirs(ERROR_DIR)
    
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    nome_base = ''.join(c for c in motivo if c.isalnum() or c in ('_', '-')).strip()[:50]
    caminhos_salvos = []

    try:
        path_full = os.path.join(ERROR_DIR, f'{timestamp}_{nome_base}_TELA_CHEIA.png')
        pg.screenshot(path_full)
        logging.info(f"Screenshot de erro (tela cheia) salvo como '{path_full}'.")
        caminhos_salvos.append(path_full)
    except Exception as e:
        logging.error(f"Falha ao salvar screenshot de tela cheia: {e}", True)

    if region:
        try:
            path_region = os.path.join(ERROR_DIR, f'{timestamp}_{nome_base}_REGIAO.png')
            pg.screenshot(path_region, region=region)
            logging.info(f"Screenshot de erro (região) salvo como '{path_region}'.")
            caminhos_salvos.append(path_region)
        except Exception as e:
            logging.error(f"Falha ao salvar screenshot da região {region}: {e}", True)
            
    return caminhos_salvos

# --- 3. Funções de Notificação (Telegram) ---
def enviar_notificacao_telegram(mensagem: str, imagens: list = None):
    """Envia uma notificação completa (texto, logs, imagens) para o Telegram."""
    if not TELEGRAM_ENABLED:
        logging.warning("Notificações do Telegram estão desabilitadas no config.py")
        return

    token = os.getenv('TELEGRAM_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        logging.error("ERRO DE NOTIFICAÇÃO: Variáveis TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não definidas no .env")
        return

    logging.info("Iniciando envio de notificação para o Telegram...")
    try:
        log_info = get_last_log_lines()
        texto_completo = (
            f"🚨 *{TELEGRAM_NOTIFICATION_TITLE}* 🚨\n\n"
            f"*{mensagem}*\n\n"
            f"📋 *Últimos registros do log:*\n"
            f"```\n{log_info}\n```"
        )
        url_msg = f"https://api.telegram.org/bot{token}/sendMessage"
        payload_msg = {'chat_id': chat_id, 'text': texto_completo, 'parse_mode': 'Markdown'}
        requests.post(url_msg, json=payload_msg, timeout=10)
    except Exception as e:
        logging.error(f"Falha ao enviar mensagem de texto ao Telegram: {e}")

    if imagens:
        for img_path in imagens:
            if not os.path.exists(img_path):
                logging.error(f"Imagem de erro não encontrada para envio: {img_path}")
                continue
            try:
                url_img = f"https://api.telegram.org/bot{token}/sendPhoto"
                with open(img_path, 'rb') as photo_file:
                    files = {'photo': photo_file}
                    payload_img = {'chat_id': chat_id, 'caption': f'Evidência do erro: {os.path.basename(img_path)}'}
                    requests.post(url_img, files=files, data=payload_img, timeout=20)
            except Exception as e:
                logging.error(f"Falha ao enviar imagem '{img_path}' ao Telegram: {e}")
    logging.info("Notificação para o Telegram finalizada.")

# --- 4. Medição de Performance e ROI ---
class PerformanceTimer:
    """Classe para medir tempo de execução, iterações e calcular o tempo humano economizado."""
    def __init__(self, human_time_per_iteration_sec: int = 0):
        self.start_time = None
        self.lap_start_time = None
        self.lap_count = 0
        self.total_time = 0
        self.human_time_per_iteration = human_time_per_iteration_sec
        logging.info(f"Timer de ROI inicializado (Tempo humano p/ tarefa: {human_time_per_iteration_sec}s)")

    def start(self):
        """Inicia o cronômetro principal."""
        self.start_time = time.time()
        self.lap_start_time = self.start_time
        logging.info("Cronômetro de performance iniciado.")

    def lap(self):
        """Marca a conclusão de uma iteração."""
        if not self.start_time:
            logging.warning("Timer.start() não foi chamado. Ignorando 'lap'.")
            return
        lap_time = time.time() - self.lap_start_time
        self.lap_count += 1
        logging.info(f"Iteração {self.lap_count} concluída em {lap_time:.2f}s")
        self.lap_start_time = time.time()

    def stop(self) -> dict:
        """Para o cronômetro e gera o relatório final no log."""
        if not self.start_time:
            logging.warning("Timer.start() não foi chamado. Relatório vazio.")
            return {}
            
        self.total_time = time.time() - self.start_time
        avg_lap = (self.total_time / self.lap_count) if self.lap_count > 0 else 0
        
        report = {
            "total_time_sec": self.total_time,
            "total_iterations": self.lap_count,
            "avg_time_per_iteration_sec": avg_lap,
            "human_time_saved_sec": 0,
            "human_time_saved_hours": 0
        }

        logging.info("--- Relatório de Performance ---")
        logging.info(f"Tempo Total de Execução: {self.total_time:.2f} segundos")
        logging.info(f"Total de Iterações Concluídas: {self.lap_count}")
        logging.info(f"Tempo Médio por Iteração: {avg_lap:.2f} segundos")

        if self.human_time_per_iteration > 0 and self.lap_count > 0:
            human_total_time = self.human_time_per_iteration * self.lap_count
            time_saved_sec = human_total_time - self.total_time
            time_saved_hours = time_saved_sec / 3600
            
            report["human_time_saved_sec"] = time_saved_sec
            report["human_time_saved_hours"] = time_saved_hours

            logging.info("--- Relatório de ROI (Tempo Humano) ---")
            logging.info(f"Tempo Humano Estimado: {human_total_time / 60:.2f} minutos")
            logging.info(f"Tempo da Automação: {self.total_time / 60:.2f} minutos")
            logging.info(f"TEMPO ECONOMIZADO NESTA EXECUÇÃO: {time_saved_sec:.2f} segundos (~{time_saved_hours:.2f} horas)")
        
        return report