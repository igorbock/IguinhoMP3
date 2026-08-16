import re
from datetime import datetime
from pathlib import Path


# ==========================================
# CONFIGURAÇÕES
# ==========================================

ARQUIVO_CONVERSA = "../conversa.txt"

# Diretório onde os arquivos serão salvos.
# "." = diretório atual onde o script está sendo executado.
DIRETORIO_SAIDA = Path("../arquivos")


# ==========================================
# EXTRATOR DE LINKS
# ==========================================

def extrair_links(arquivo):

    links = []

    with open(arquivo, "r", encoding="utf-8") as arquivo:
        texto = arquivo.read()

    # Procura URLs HTTP/HTTPS
    padrao = r'https?://[^\s]+'

    encontrados = re.findall(padrao, texto)

    for link in encontrados:

        # Remove pontuação que possa ter vindo junto
        link = link.rstrip('.,!?;:)')

        # Remove links duplicados
        if link not in links:
            links.append(link)

    return links


def processar(arquivo, diretorio_saida=None):

    """
    Extrai os links do arquivo de conversa e
    salva em um arquivo .txt com data/hora.

    Retorna (links, caminho_do_arquivo_gerado).
    """

    if diretorio_saida is None:
        diretorio_saida = DIRETORIO_SAIDA

    diretorio_saida = Path(diretorio_saida)

    links = extrair_links(arquivo)

    # Data/hora no formato:
    # dd_MM_yyyy_hh_mm
    data_hora = datetime.now().strftime("%d_%m_%Y_%H_%M")

    nome_arquivo = f"{data_hora}.txt"

    arquivo_saida = diretorio_saida / nome_arquivo

    with open(arquivo_saida, "w", encoding="utf-8") as arquivo:

        for link in links:
            arquivo.write(link + "\n")

    return links, arquivo_saida


# ==========================================
# EXECUÇÃO
# ==========================================

if __name__ == "__main__":

    links, arquivo_saida = processar(
        ARQUIVO_CONVERSA,
        DIRETORIO_SAIDA
    )

    print("Processamento concluído.")
    print(f"Links encontrados: {len(links)}")
    print(f"Arquivo criado: {arquivo_saida.resolve()}")