from urllib.parse import urlparse
from datetime import datetime
from pathlib import Path

PLATAFORMAS_PERMITIDAS = [
    "youtube.com",
    "youtu.be",
    "facebook.com",
    "fb.watch",
    "vt.tiktok.com",
    "tiktok.com",
    "vt.tiktok"
]

DIRETORIO_SAIDA = Path("../arquivos")


def validar_url(url):
    """
    Valida se a URL possui um formato válido
    e pertence a uma das plataformas permitidas.
    """

    try:
        resultado = urlparse(url)

        # Precisa possuir HTTP/HTTPS
        if resultado.scheme not in ("http", "https"):
            return False

        # Precisa possuir domínio
        if not resultado.netloc:
            return False

        dominio = resultado.netloc.lower()

        # Remove www.
        if dominio.startswith("www."):
            dominio = dominio[4:]

        # Verifica se pertence a uma plataforma permitida
        for plataforma in PLATAFORMAS_PERMITIDAS:
            if dominio == plataforma or dominio.endswith("." + plataforma):
                return True

        return False

    except Exception:
        return False


def validar_arquivo(arquivo_entrada):
    links_validos = []
    links_invalidos = []

    with open(arquivo_entrada, "r", encoding="utf-8") as arquivo:

        for numero_linha, linha in enumerate(arquivo, start=1):

            url = linha.strip()

            # Ignora linhas vazias
            if not url:
                continue

            if validar_url(url):

                if url not in links_validos:
                    links_validos.append(url)

            else:
                links_invalidos.append({
                    "linha": numero_linha,
                    "url": url
                })

    return links_validos, links_invalidos


def processar(arquivo_entrada, diretorio_saida=None):

    """
    Valida os links do arquivo e salva apenas os
    válidos em um arquivo .txt com data/hora.

    Retorna (links_validos, links_invalidos, caminho_do_arquivo_gerado).
    """

    if diretorio_saida is None:
        diretorio_saida = DIRETORIO_SAIDA

    diretorio_saida = Path(diretorio_saida)

    links_validos, links_invalidos = validar_arquivo(arquivo_entrada)

    # Data/hora no formato:
    # dd_MM_yyyy_hh_mm
    data_hora = datetime.now().strftime("%d_%m_%Y_%H_%M")

    nome_arquivo = f"links_validos_{data_hora}.txt"

    arquivo_saida = diretorio_saida / nome_arquivo

    with open(arquivo_saida, "w", encoding="utf-8") as arquivo:

        for link in links_validos:
            arquivo.write(link + "\n")

    return links_validos, links_invalidos, arquivo_saida


if __name__ == "__main__":

    links_validos, links_invalidos, arquivo_saida = processar(
        "15_08_2026_15_47.txt",
        DIRETORIO_SAIDA
    )

    print("====================================")
    print("VALIDAÇÃO DOS LINKS")
    print("====================================")

    print(f"Links válidos:   {len(links_validos)}")
    print(f"Links inválidos: {len(links_invalidos)}")
    print()

    print(f"Arquivo criado: {arquivo_saida.resolve()}")