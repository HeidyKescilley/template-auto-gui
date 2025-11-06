import logging
from dotenv import load_dotenv 

# Funções principais da automação
from automation_helpers import (
    setup_automation, 
    safe_click, 
    find_and_click, 
    type_text,
    esperar_imagem
)

# Funções de notificação e performance
from reporting import (
    PerformanceTimer,
    salvar_screenshot_erro,
    enviar_notificacao_telegram
)

# --- Lógica de Negócio (Exemplo) ---
def fazer_login():
    """Executa o processo de login."""
    logging.info("Iniciando processo de login...")
    
    # Exemplo 1: Usando coordenadas do 'coordinates.json'
    # safe_click("campo_usuario") 
    # type_text("meu_usuario")
    
    # Exemplo 2: Usando imagens da pasta '/images/'
    if not find_and_click("campo_usuario.png"):
        raise Exception("Campo 'usuário' não encontrado. Abortando.")
    type_text("meu_usuario_secreto")

    if not find_and_click("campo_senha.png"):
        raise Exception("Campo 'senha' não encontrado. Abortando.")
    type_text("minha_senha_123")
    
    if not find_and_click("botao_login.png"):
        raise Exception("Botão 'login' não encontrado. Abortando.")
        
    esperar_imagem("icone_dashboard.png", timeout_segundos=15)
    logging.info("Login realizado com sucesso!")

def processar_fatura(id_fatura):
    """Executa a lógica de negócio principal para um item."""
    logging.info(f"Processando fatura ID: {id_fatura}")
    
    find_and_click("menu_faturas.png")
    find_and_click("campo_busca_fatura.png")
    type_text(str(id_fatura))
    find_and_click("botao_pesquisar_fatura.png")
    
    # Simula um erro na fatura 3
    if id_fatura == 3:
        logging.warning("Simulando um erro na fatura 3...")
        find_and_click("imagem_que_nao_existe.png") # Isso vai falhar e ser capturado
    
    esperar_imagem("confirmacao_fatura.png")
    find_and_click("botao_voltar_menu.png")
    logging.info(f"Fatura {id_fatura} processada.")


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
    
    faturas_para_processar = [1, 2, 3, 4, 5] # Lista de tarefas

    try:
        # 5. Inicia o Cronômetro
        timer.start()
        
        # --- Início da Lógica da Automação ---
        fazer_login()
        
        logging.info(f"Iniciando processamento de {len(faturas_para_processar)} faturas.")
        
        for fatura_id in faturas_para_processar:
            processar_fatura(fatura_id)
            
            # 6. Registra a conclusão da iteração (importante!)
            timer.lap() 
            
        logging.info("Todas as faturas foram processadas com sucesso.")

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