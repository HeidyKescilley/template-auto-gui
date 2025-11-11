import logging
from dotenv import load_dotenv 
import pandas as pd
import time
import pyautogui as pg

# Funções principais da automação
from automation_helpers import (
    setup_automation, 
    safe_click, 
    find_and_click, 
    type_text,
    esperar_imagem,
    esperar_imagem_desaparecer,
    imagem_esta_presente,
    click_relative
)

# Funções de notificação e performance
from reporting import (
    PerformanceTimer,
    salvar_screenshot_erro,
    enviar_notificacao_telegram
)

# --- Lógica de Negócio (funções aqui) ---


# --- Ponto de Entrada Principal ---
if __name__ == "__main__":
    
    # 1. Carrega variáveis de ambiente (.env) para o Telegram
    load_dotenv() 
    
    # 2. Inicia a "Base de Logging" e cria as pastas
    setup_automation()
    
    # 3. [ROI] Defina o "Custo" humano da tarefa
    # Quanto tempo (em segundos) um humano levaria para fazer UMA iteração?
    HUMAN_TIME_PER_TASK_SEC = 180 # Ex: 3 minutos
    
    # 4. Inicializa o Timer de Performance
    timer = PerformanceTimer(human_time_per_iteration_sec=HUMAN_TIME_PER_TASK_SEC)

    time.sleep(3)
    
    try:
        # 5. Inicia o Cronômetro
        timer.start()
        
        # --- Início da Lógica da Automação ---
        # Aqui é onde a magica acontece!
        
        df = pd.read_excel("./empresas.xlsx")
        
        logging.info(f"Iniciando processamento de {len(df)} meses.")
        
        if 'numero' not in df.columns or 'filial' not in df.columns:
            print("Erro: O arquivo não contém as colunas 'numero' e 'filial'.")
            print(f"Colunas encontradas: {list(df.columns)}")
            
            time.sleep(2)
        else:
            # 2. Itera sobre cada linha do DataFrame
            # A função iterrows() retorna o índice da linha e a linha (como um objeto)
            for indice, linha in df.iterrows():
                
                # 3. Captura o conteúdo das colunas pelo nome
                numero = linha['numero']
                filial = linha['filial']
                empresa = linha['empresa']
                regime = linha['regime']
                classe = linha['classe']
                logging.info(f"Processando empresa: {empresa}.")
                
                pg.press('f7')
                type_text(str(numero))
                pg.press('tab')
                type_text(str(filial))
                pg.press(['enter'] * 4)
                
                input("Aperte Enter para continuar...")
                
    except Exception as e:
        # 7. CAPTURA DE ERRO E NOTIFICAÇÃO
        logging.critical(f"Erro fatal não tratado na automação: {e}", exc_info=True)
        logging.info("Iniciando processo de notificação de erro...")
        
        # 7a. Salva os screenshots de erro
        screenshots = salvar_screenshot_erro(motivo=str(e))
        
        # 7b. Envia a notificação para o Telegram
        enviar_notificacao_telegram(
            mensagem=f"Erro fatal: {e}", 
            imagens=screenshots
        )

    finally:
        # 8. RELATÓRIO FINAL (sempre executa)
        timer.stop()
        logging.info("--- Automação Finalizada ---")