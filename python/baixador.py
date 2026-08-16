import os
import re
import sys
import argparse
import unicodedata
import shutil
import subprocess
import urllib.request
import zipfile

from datetime import datetime
from pathlib import Path

# Garante que o diretório deste script esteja na busca
# de módulos (ex.: validador_duplicacao.py)
PASTA_SCRIPT = Path(__file__).resolve().parent

if str(PASTA_SCRIPT) not in sys.path:
    sys.path.insert(0, str(PASTA_SCRIPT))


# ============================================================
# CONFIGURAÇÕES
# ============================================================

# Pasta principal do projeto
PASTA_BASE = Path(r"D:\Projetos\Pessoal\IguinhoMP3")

# Arquivo contendo os links válidos
ARQUIVO_LINKS = PASTA_BASE / "arquivos" / "links_validos_15_08_2026_15_59.txt"

# Pasta onde os MP3 serão armazenados
PASTA_SAIDA = PASTA_BASE / "musicas"

# Pasta para arquivos temporários
PASTA_TEMP = PASTA_BASE / "temp"

# Arquivo com os links que falharam no download
ARQUIVO_ERROS = PASTA_BASE / "arquivos" / "links_com_erro.txt"

# Pasta do FFmpeg
PASTA_FFMPEG = PASTA_BASE / "ffmpeg"


# URL do FFmpeg para Windows
URL_FFMPEG = (
    "https://www.gyan.dev/ffmpeg/builds/"
    "ffmpeg-release-essentials.zip"
)


# ============================================================
# PREPARAÇÃO DAS PASTAS
# ============================================================

def preparar_pastas():

    PASTA_BASE.mkdir(parents=True, exist_ok=True)
    PASTA_SAIDA.mkdir(parents=True, exist_ok=True)
    PASTA_TEMP.mkdir(parents=True, exist_ok=True)
    PASTA_FFMPEG.mkdir(parents=True, exist_ok=True)
    ARQUIVO_LINKS.parent.mkdir(parents=True, exist_ok=True)


# ============================================================
# CONFIGURAÇÃO DO TEMPORÁRIO
# ============================================================

def configurar_temporarios():

    """
    Faz com que Python e programas chamados por ele
    utilizem o D:\Projetos\Pessoal\IguinhoMP3\temp como diretório temporário.
    """

    os.environ["TEMP"] = str(PASTA_TEMP)
    os.environ["TMP"] = str(PASTA_TEMP)

    # Algumas aplicações utilizam essas variáveis
    os.environ["TMPDIR"] = str(PASTA_TEMP)

    print(f"Diretório TEMP: {PASTA_TEMP}")


# ============================================================
# LIMPEZA DO TEMPORÁRIO
# ============================================================

def limpar_temporarios():

    """
    Remove os arquivos temporários gerados pela execução anterior.
    """

    if not PASTA_TEMP.exists():
        return

    print()
    print("Limpando arquivos temporários...")

    for item in PASTA_TEMP.iterdir():

        try:

            if item.is_dir():
                shutil.rmtree(item)

            else:
                item.unlink()

        except Exception as erro:

            print(
                f"Não foi possível remover "
                f"{item}: {erro}"
            )

    print("✓ Pasta temporária limpa.")


# ============================================================
# VERIFICAÇÃO DO yt-dlp
# ============================================================

def verificar_ytdlp():

    try:

        import yt_dlp

        print("✓ yt-dlp encontrado.")

        return True

    except ImportError:

        print("yt-dlp não encontrado.")
        print("Instalando yt-dlp...")

        resultado = subprocess.run(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "--no-cache-dir",
                "yt-dlp"
            ],
            capture_output=True,
            text=True
        )

        if resultado.returncode != 0:

            print()
            print("ERRO ao instalar yt-dlp:")
            print(resultado.stderr)

            return False

        print("✓ yt-dlp instalado.")

        return True


# ============================================================
# LOCALIZAR FFmpeg
# ============================================================

def encontrar_ffmpeg():

    # Primeiro verifica se existe no PATH
    ffmpeg = shutil.which("ffmpeg")

    if ffmpeg:

        return Path(ffmpeg)

    # Depois verifica nossa instalação local
    caminho_local = (
        PASTA_FFMPEG
        / "bin"
        / "ffmpeg.exe"
    )

    if caminho_local.exists():

        return caminho_local

    return None


# ============================================================
# INSTALAR FFmpeg
# ============================================================

def instalar_ffmpeg():

    print()
    print("FFmpeg não encontrado.")
    print("Baixando FFmpeg para o D:...")

    PASTA_FFMPEG.mkdir(
        parents=True,
        exist_ok=True
    )

    arquivo_zip = (
        PASTA_TEMP
        / "ffmpeg.zip"
    )

    try:

        urllib.request.urlretrieve(
            URL_FFMPEG,
            arquivo_zip
        )

        print("✓ Download do FFmpeg concluído.")

        print("Extraindo FFmpeg...")

        with zipfile.ZipFile(
            arquivo_zip,
            "r"
        ) as zip_ref:

            zip_ref.extractall(
                PASTA_FFMPEG
            )

        # Remove o ZIP imediatamente
        arquivo_zip.unlink()

        # Procura o executável
        caminho_ffmpeg = None

        for caminho in PASTA_FFMPEG.rglob(
            "ffmpeg.exe"
        ):

            caminho_ffmpeg = caminho
            break

        if not caminho_ffmpeg:

            print(
                "ERRO: ffmpeg.exe não foi "
                "encontrado após a extração."
            )

            return None

        # Cria nossa pasta bin
        pasta_bin = (
            PASTA_FFMPEG
            / "bin"
        )

        pasta_bin.mkdir(
            parents=True,
            exist_ok=True
        )

        destino = (
            pasta_bin
            / "ffmpeg.exe"
        )

        # Se já estiver no destino, não precisa copiar
        if caminho_ffmpeg.resolve() != destino.resolve():

            shutil.copy2(
                caminho_ffmpeg,
                destino
            )

        print(
            f"✓ FFmpeg instalado em: "
            f"{destino}"
        )

        return destino

    except Exception as erro:

        print()
        print(
            f"ERRO ao instalar FFmpeg: {erro}"
        )

        return None


# ============================================================
# PREPARAR AMBIENTE
# ============================================================

def preparar_ambiente():

    print()
    print("========================================")
    print("PREPARANDO AMBIENTE")
    print("========================================")

    preparar_pastas()

    configurar_temporarios()

    # --------------------------------------------------------
    # yt-dlp
    # --------------------------------------------------------

    if not verificar_ytdlp():

        return False

    # --------------------------------------------------------
    # FFmpeg
    # --------------------------------------------------------

    ffmpeg = encontrar_ffmpeg()

    if ffmpeg:

        print(
            f"✓ FFmpeg encontrado: {ffmpeg}"
        )

    else:

        ffmpeg = instalar_ffmpeg()

        if not ffmpeg:

            return False

    # --------------------------------------------------------
    # Adiciona FFmpeg ao PATH
    # --------------------------------------------------------

    pasta_bin = ffmpeg.parent

    os.environ["PATH"] = (
        str(pasta_bin)
        + os.pathsep
        + os.environ["PATH"]
    )

    print()
    print("✓ Ambiente preparado.")

    return True


# ============================================================
# LER LINKS
# ============================================================

def carregar_links():

    if not ARQUIVO_LINKS.exists():

        print()
        print(
            f"Arquivo não encontrado:"
        )

        print(
            ARQUIVO_LINKS
        )

        return []

    with open(
        ARQUIVO_LINKS,
        "r",
        encoding="utf-8"
    ) as arquivo:

        links = [
            linha.strip()
            for linha in arquivo
            if linha.strip()
        ]

    return links


# ============================================================
# LIMPEZA DE TÍTULO
# ============================================================

LIMITE_TITULO = 80

# Símbolos que podem aparecer como separadores repetidos
SEPARADORES = "|•·‑–—"

# Caracteres que são mantidos no título limpo
CARACTERES_VALIDOS = set(
    "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "abcdefghijklmnopqrstuvwxyz"
    "0123456789"
    "áàâãäéèêëíìîïóòôõöúùûüçñ"
    "ÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ"
    " -_.()[]'\"&,+!?#"
)


def limpar_titulo(titulo):

    """
    Remove do título tudo o que não ajuda a identificar
    a música: URLs, hashtags, contadores de views/reações,
    emojis, símbolos especiais e sufixos como "on Reels".
    """

    if not titulo:
        return ""

    texto = titulo

    # Remove URLs
    texto = re.sub(r"https?://\S+", " ", texto)

    # Remove prefixos do tipo "110K views • 6K reactions |"
    texto = re.sub(
        r"^\s*"
        r"\d+([.,]\d+)?\s*[KkMm]?\s*(views?|reactions?|likes?)\s*"
        r"[•|·\-:.]\s*"
        r"\d+([.,]\d+)?\s*[KkMm]?\s*(views?|reactions?|likes?)?\s*"
        r"[•|·\-]?\s*",
        " ",
        texto
    )

    # Remove hashtags
    texto = re.sub(r"#\w+", " ", texto)

    # Remove sufixos do tipo "on Reels" / "- Reels"
    texto = re.sub(r"\s+(on\s+)?reels\s*$", "", texto, flags=re.IGNORECASE)

    # Remove emojis e símbolos especiais
    resultado = []

    for caractere in texto:

        categoria = unicodedata.category(caractere)

        # Mantém letras, números e pontuação comum
        if (
            caractere in CARACTERES_VALIDOS
            or categoria.startswith("L")
            or categoria.startswith("N")
            or caractere.isspace()
        ):
            resultado.append(caractere)

        else:
            resultado.append(" ")

    texto = "".join(resultado)

    # Remove "TikTok video #123" genérico (é tratado depois,
    # quando houver track/artist disponíveis)

    # Substitui separadores repetidos por um único
    texto = re.sub(
        r"[" + re.escape(SEPARADORES) + r"]{2,}",
        "|",
        texto
    )

    # Remove espaços em excesso
    texto = re.sub(r"\s+", " ", texto)

    # Remove separadores nas pontas e pontuação solta
    texto = texto.strip(" |·•‑–—-_.,;:()[]'\"")

    # Limita o tamanho final
    texto = texto[:LIMITE_TITULO].rstrip(" |·•‑–—-_.,;:()")

    return texto.strip()


def montar_nome(info):

    """
    Monta o título limpo usando track/artist quando
    disponíveis; caso contrário, limpa o título do vídeo.
    """

    artista = (
        info.get("artist")
        or info.get("creator")
        or info.get("uploader")
    )

    faixa = info.get("track")
    titulo = info.get("title") or ""

    # Título genérico do TikTok: "TikTok video #123"
    if faixa and re.search(r"^TikTok video\s+#?\d+", titulo):

        base = f"{limpar_titulo(artista)} - {limpar_titulo(faixa)}"

        return base or "sem_titulo"

    return limpar_titulo(titulo) or "sem_titulo"


# ============================================================
# SALVAR LINKS COM ERRO
# ============================================================

def salvar_links_com_erro(links_com_erro):

    if not links_com_erro:

        print()
        print("✓ Nenhum link com erro para salvar.")

        return

    # Nome com data/hora para não sobrescrever execuções anteriores
    momento = datetime.now().strftime("%d_%m_%Y_%H_%M")

    arquivo = (
        ARQUIVO_ERROS.parent
        / f"links_com_erro_{momento}.txt"
    )

    with open(
        arquivo,
        "w",
        encoding="utf-8"
    ) as f:

        for link in links_com_erro:

            f.write(link + "\n")

    print()
    print(
        f"✗ {len(links_com_erro)} link(s) com erro salvos em:"
    )
    print(arquivo)


# ============================================================
# DOWNLOAD
# ============================================================

def baixar_musicas():

    import yt_dlp

    from validador_duplicacao import calcular_hash, encontrar_hashes

    # --------------------------------------------------------
    # Post-processor que limpa o título/artista antes do
    # download, para que o nome do arquivo e as tags do MP3
    # já saiam limpos.
    # --------------------------------------------------------

    class LimparTituloPP(yt_dlp.postprocessor.PostProcessor):

        def run(self, info):

            # Define o artista para as tags (ID3)
            info["artist"] = (
                info.get("artist")
                or info.get("creator")
                or info.get("uploader")
            )

            # Limpa o título usado no nome do arquivo
            info["title"] = montar_nome(info)

            # Limpa a descrição (evita spam de hashtags
            # e URLs na tag de comentário/descrição)
            if info.get("description"):

                info["description"] = limpar_titulo(
                    info["description"]
                )

            return [], info

    links = carregar_links()

    if not links:

        print()
        print(
            "Nenhum link encontrado."
        )

        return

    print()
    print("========================================")
    print("DOWNLOAD")
    print("========================================")

    print(
        f"Links encontrados: {len(links)}"
    )

    print(
        f"Pasta de destino: {PASTA_SAIDA}"
    )

    print()

    # Lista em memória com os links que falharam
    links_com_erro = []

    # --------------------------------------------------------
    # Hash dos arquivos já existentes (para detectar duplicatas)
    # --------------------------------------------------------

    print()
    print("Verificando arquivos já existentes...")

    hashes_existentes = encontrar_hashes(PASTA_SAIDA)

    print(
        f"Arquivos existentes: {len(hashes_existentes)}"
    )

    # Contadores do resumo final
    downloads_ok = 0
    pulados_duplicados = 0
    duplicados_removidos = 0

    # --------------------------------------------------------
    # Configuração do yt-dlp
    # --------------------------------------------------------

    opcoes = {
        # Melhor áudio disponível
        "format": "bestaudio/best",

        # Nome do arquivo
        #
        # Limita o título a 80 caracteres e adiciona
        # o ID do vídeo para evitar conflitos de nomes.
        "outtmpl": str(
            PASTA_SAIDA
            / "%(title).80s [%(id)s].%(ext)s"
        ),

        # Não baixar playlists
        "noplaylist": True,

        # Não utilizar cache do yt-dlp
        "cachedir": False,

        # Adaptar nomes para o Windows
        "windowsfilenames": True,

        # Extrair áudio para MP3
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            },
            # Grava as tags ID3 no MP3 (título limpo,
            # artista, data, álbum quando existir)
            {
                "key": "FFmpegMetadata",
            },
        ],

        # Mostrar progresso
        "progress": True,
    }

    # --------------------------------------------------------
    # Inicializa yt-dlp
    # --------------------------------------------------------

    with yt_dlp.YoutubeDL(opcoes) as ydl:

        # Limpa o título/artista antes do download, para que
        # o nome do arquivo e as tags saiam limpos.
        ydl.add_post_processor(
            LimparTituloPP(),
            when="pre_process"
        )

        for indice, link in enumerate(
            links,
            start=1
        ):

            print()
            print("----------------------------------------")

            print(
                f"[{indice}/{len(links)}]"
            )

            print(
                f"URL: {link}"
            )

            print("----------------------------------------")

            # ----------------------------------------------------
            # Pré-checagem por ID do vídeo: se já existe um
            # arquivo com o mesmo ID, não precisa baixar.
            # ----------------------------------------------------

            id_video = None

            try:

                info = ydl.extract_info(
                    link,
                    download=False
                )

                id_video = info.get("id")

            except Exception:

                id_video = None

            if id_video:

                ja_baixado = any(
                    f"[{id_video}]" in arquivo.stem
                    for arquivo in PASTA_SAIDA.iterdir()
                    if arquivo.is_file()
                )

                if ja_baixado:

                    print()
                    print(
                        "→ Já baixado anteriormente "
                        "(mesmo ID). Pulando download."
                    )

                    pulados_duplicados += 1

                    continue

            # ----------------------------------------------------
            # Arquivos existentes antes do download
            # ----------------------------------------------------

            arquivos_antes = {
                arquivo
                for arquivo in PASTA_SAIDA.iterdir()
                if arquivo.is_file()
            }

            try:

                ydl.download([link])

                print()
                print("✓ Download concluído.")

                downloads_ok += 1

                # ----------------------------------------------------
                # Verificação de duplicidade por hash.
                # Se o conteúdo já existe na pasta, o arquivo
                # recém-baixado é excluído para não duplicar.
                # ----------------------------------------------------

                arquivos_novos = [
                    arquivo
                    for arquivo in PASTA_SAIDA.iterdir()
                    if arquivo.is_file()
                    and arquivo not in arquivos_antes
                ]

                for arquivo in arquivos_novos:

                    hash_arquivo = calcular_hash(arquivo)

                    if hash_arquivo in hashes_existentes:

                        arquivo.unlink()

                        print()
                        print(
                            "→ Conteúdo já existente, "
                            "arquivo excluído."
                        )

                        duplicados_removidos += 1

                    else:

                        hashes_existentes[hash_arquivo] = arquivo

            except Exception as erro:

                print()
                print(
                    f"✗ ERRO: {erro}"
                )

                links_com_erro.append(link)

    # --------------------------------------------------------
    # Resumo
    # --------------------------------------------------------

    print()
    print("========================================")
    print("RESUMO DO DOWNLOAD")
    print("========================================")
    print(f"Baixados:              {downloads_ok}")
    print(f"Já existiam (pulados): {pulados_duplicados}")
    print(f"Duplicatas excluídas:  {duplicados_removidos}")
    print(f"Com erro:              {len(links_com_erro)}")

    # --------------------------------------------------------
    # Salva os links que falharam
    # --------------------------------------------------------

    salvar_links_com_erro(links_com_erro)


# ============================================================
# LIMPEZA FINAL
# ============================================================

def finalizar():

    print()
    print("Limpando arquivos temporários...")

    limpar_temporarios()

    print()
    print("========================================")
    print("PROCESSO FINALIZADO")
    print("========================================")

    print(
        f"Músicas: {PASTA_SAIDA}"
    )


# ============================================================
# MAIN
# ============================================================

def main():

    global ARQUIVO_LINKS, PASTA_SAIDA

    print()
    print("========================================")
    print("       IGUINHO MP3")
    print("========================================")

    # ----------------------------------------------------
    # Argumentos da linha de comando
    # ----------------------------------------------------

    parser = argparse.ArgumentParser(
        description=(
            "Extrai os links de uma conversa do WhatsApp, "
            "valida e baixa as músicas."
        )
    )

    parser.add_argument(
        "conversa",
        help=(
            "Caminho do arquivo .txt da conversa "
            "do WhatsApp com os links."
        )
    )

    parser.add_argument(
        "destino",
        help=(
            "Diretório onde as músicas baixadas "
            "serão salvas."
        )
    )

    args = parser.parse_args()

    PASTA_SAIDA = Path(args.destino)

    # ----------------------------------------------------
    # Valida o arquivo de conversa informado
    # ----------------------------------------------------

    conversa = Path(args.conversa)

    if not conversa.exists():

        print()
        print("ERRO: Arquivo de conversa não encontrado:")
        print(conversa.resolve())

        return

    # ----------------------------------------------------
    # Verifica se o disco do destino está disponível
    # ----------------------------------------------------

    unidade = PASTA_SAIDA.anchor

    if unidade and not os.path.exists(unidade):

        print()
        print(
            f"ERRO: O disco {unidade} não está disponível."
        )
        print(
            f"Destino informado: {PASTA_SAIDA}"
        )

        return

    # ----------------------------------------------------
    # Cria o diretório de destino, se ainda não existir
    # ----------------------------------------------------

    try:

        PASTA_SAIDA.mkdir(
            parents=True,
            exist_ok=True
        )

    except OSError as erro:

        print()
        print(
            "ERRO: Não foi possível criar o diretório "
            "de destino:"
        )
        print(PASTA_SAIDA)
        print(erro)

        return

    print()
    print(f"Conversa:  {conversa.resolve()}")
    print(f"Destino:   {PASTA_SAIDA.resolve()}")

    try:

        # ----------------------------------------------------
        # Preparar ambiente
        # ----------------------------------------------------

        if not preparar_ambiente():

            print()
            print(
                "Não foi possível preparar "
                "o ambiente."
            )

            return

        # ----------------------------------------------------
        # Limpa temporários de execuções anteriores
        # ----------------------------------------------------

        limpar_temporarios()

        # ----------------------------------------------------
        # 1. Extrair os links da conversa do WhatsApp
        # ----------------------------------------------------

        print()
        print("========================================")
        print("1. EXTRAÇÃO DE LINKS")
        print("========================================")

        from extrator import processar as processar_extracao

        links_extraidos, arquivo_extraido = processar_extracao(
            args.conversa,
            ARQUIVO_LINKS.parent
        )

        print(
            f"Links encontrados: {len(links_extraidos)}"
        )
        print(
            f"Arquivo gerado: {arquivo_extraido.resolve()}"
        )

        if not links_extraidos:

            print()
            print("Nenhum link encontrado na conversa.")

            return

        # ----------------------------------------------------
        # 2. Validar os links extraídos
        # ----------------------------------------------------

        print()
        print("========================================")
        print("2. VALIDAÇÃO DOS LINKS")
        print("========================================")

        from validador import processar as processar_validacao

        links_validos, links_invalidos, arquivo_validos = processar_validacao(
            arquivo_extraido,
            ARQUIVO_LINKS.parent
        )

        print(
            f"Links válidos:   {len(links_validos)}"
        )
        print(
            f"Links inválidos: {len(links_invalidos)}"
        )
        print(
            f"Arquivo gerado: {arquivo_validos.resolve()}"
        )

        if not links_validos:

            print()
            print("Nenhum link válido para download.")

            return

        # ----------------------------------------------------
        # 3. Definir o arquivo de links válidos para o download
        # ----------------------------------------------------

        ARQUIVO_LINKS = arquivo_validos

        # ----------------------------------------------------
        # 4. Download das músicas
        # ----------------------------------------------------

        baixar_musicas()

    finally:

        # ----------------------------------------------------
        # Sempre tenta limpar temporários
        # ----------------------------------------------------

        finalizar()


# ============================================================
# EXECUÇÃO
# ============================================================

if __name__ == "__main__":

    main()