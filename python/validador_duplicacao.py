import hashlib
import shutil

from pathlib import Path


PASTA_BASE = Path(r"D:\Projetos\Pessoal\IguinhoMP3")
PASTA_SAIDA = PASTA_BASE / "musicas"

# Pendrive: ajuste a letra da unidade conforme o seu
PENDRIVE = Path("E:/Musicas")


def calcular_hash(arquivo):

    sha256 = hashlib.sha256()

    with open(arquivo, "rb") as f:

        while bloco := f.read(1024 * 1024):
            sha256.update(bloco)

    return sha256.hexdigest()


def encontrar_hashes(pasta, extensoes=(".mp3", ".mp4")):

    """
    Retorna um dicionário {hash: caminho} com todos
    os arquivos das extensões informadas na pasta.
    """

    hashes = {}

    for arquivo in Path(pasta).rglob("*"):

        if not arquivo.is_file():
            continue

        if arquivo.suffix.lower() not in extensoes:
            continue

        try:

            hash_arquivo = calcular_hash(arquivo)
            hashes[hash_arquivo] = arquivo

        except Exception as erro:

            print(f"Erro ao ler {arquivo}: {erro}")

    return hashes


def ja_existe(pasta, hash_arquivo, extensoes=(".mp3", ".mp4")):

    """
    Verifica se já existe um arquivo com o mesmo
    conteúdo (hash) na pasta.
    """

    hashes = encontrar_hashes(pasta, extensoes)

    return hash_arquivo in hashes


def copiar_novos_mp3(pasta_origem, pendrive):

    print("Analisando arquivos do pendrive...")

    hashes_pendrive = encontrar_hashes(pendrive)

    print(f"Arquivos encontrados no pendrive: {len(hashes_pendrive)}")
    print()

    arquivos_copiados = 0
    arquivos_ignorados = 0

    for arquivo in Path(pasta_origem).rglob("*.mp3"):

        print(f"Analisando: {arquivo.name}")

        hash_arquivo = calcular_hash(arquivo)

        if hash_arquivo in hashes_pendrive:

            print("  → Já existe no pendrive.")
            arquivos_ignorados += 1

        else:

            destino = Path(pendrive) / arquivo.name

            shutil.copy2(arquivo, destino)

            print("  → Copiado!")
            arquivos_copiados += 1

            hashes_pendrive[hash_arquivo] = destino

    print()
    print("==============================")
    print("PROCESSO FINALIZADO")
    print("==============================")
    print(f"Copiados:  {arquivos_copiados}")
    print(f"Ignorados: {arquivos_ignorados}")


if __name__ == "__main__":

    copiar_novos_mp3(PASTA_SAIDA, PENDRIVE)