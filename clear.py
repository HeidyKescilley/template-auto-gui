import os
import shutil
import logging

# Tenta importar as configurações de pastas do seu framework
try:
    from config import BASE_DIR, LOG_DIR, ERROR_DIR, CLICK_HISTORY_DIR
    # Pega o nome do arquivo de log para poder excluí-lo
    from config import LOG_FILE_NAME 
except ImportError:
    print("ERRO: Não foi possível encontrar 'config.py'.")
    print("Execute este script da pasta raiz do seu projeto RPA.")
    exit(1)

# Lista de diretórios que serão esvaziados
# Não vamos deletar o diretório em si, mas sim seu conteúdo.
DIRS_TO_EMPTY = [
    LOG_DIR,
    ERROR_DIR,
    CLICK_HISTORY_DIR
]

def empty_directory(dir_path):
    """Remove todos os arquivos e subpastas de um diretório, mas mantém o diretório."""
    if not os.path.exists(dir_path):
        print(f"  [INFO] Diretório não existe, nada a fazer: {dir_path}")
        return

    if not os.path.isdir(dir_path):
        print(f"  [AVISO] O caminho não é um diretório: {dir_path}")
        return
        
    print(f"  Esvaziando diretório: {dir_path}")
    file_count = 0
    dir_count = 0
    
    # Itera sobre os itens no diretório
    for item_name in os.listdir(dir_path):
        item_path = os.path.join(dir_path, item_name)
        
        try:
            if os.path.isfile(item_path) or os.path.islink(item_path):
                # Se for o arquivo de log principal, ignora
                if item_name == LOG_FILE_NAME and dir_path == LOG_DIR:
                    continue 
                os.unlink(item_path)
                file_count += 1
            elif os.path.isdir(item_path):
                # Se for o __pycache__ (ver próxima função), ignora
                if item_name == "__pycache__":
                    continue
                shutil.rmtree(item_path)
                dir_count += 1
        except Exception as e:
            print(f"    [ERRO] Não foi possível remover {item_path}: {e}")
            
    print(f"    ... {file_count} arquivos e {dir_count} pastas removidos.")

def clear_main_log_file():
    """Limpa o conteúdo do arquivo de log principal, em vez de deletá-lo."""
    log_file_path = os.path.join(LOG_DIR, LOG_FILE_NAME)
    if os.path.exists(log_file_path):
        try:
            # Abre o arquivo em modo 'w' (write) para truncá-lo (zerar)
            with open(log_file_path, 'w') as f:
                pass # Apenas abrir e fechar já limpa o arquivo
            print(f"  [OK] Arquivo de log principal zerado: {log_file_path}")
        except Exception as e:
            print(f"  [ERRO] Não foi possível zerar o log: {e}")

def clean_pycache(root_dir):
    """Encontra e remove recursivamente todos os diretórios __pycache__."""
    print("\n--- Limpando Cache do Python (__pycache__) ---")
    pycache_found = False
    for root, dirs, files in os.walk(root_dir):
        if "__pycache__" in dirs:
            pycache_path = os.path.join(root, "__pycache__")
            try:
                shutil.rmtree(pycache_path)
                print(f"  [OK] Removido: {pycache_path}")
                pycache_found = True
            except Exception as e:
                print(f"  [ERRO] Falha ao remover {pycache_path}: {e}")
    
    if not pycache_found:
        print("  [INFO] Nenhum diretório __pycache__ encontrado.")

def main():
    print("--- Iniciando Limpeza do Projeto RPA ---")
    
    # 1. Esvaziar os diretórios de execução
    print("\n--- Limpando Logs e Screenshots de Execução ---")
    for dir_path in DIRS_TO_EMPTY:
        empty_directory(dir_path)
        
    # 2. Limpar o arquivo de log principal
    clear_main_log_file()
        
    # 3. Limpar o cache do Python
    clean_pycache(root_dir=BASE_DIR)
    
    print("\n--- Limpeza Concluída ---")
    print("O projeto está limpo e pronto para a próxima execução.")

if __name__ == "__main__":
    # Verifica se o script está sendo executado do lugar certo
    if not os.path.exists(os.path.join(os.path.dirname(__file__), 'config.py')):
        print("ERRO: 'config.py' não encontrado.")
        print("Este script deve ser executado da pasta raiz do seu projeto RPA.")
    else:
        main()