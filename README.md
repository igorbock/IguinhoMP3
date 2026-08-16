# Iguinho MP3

Baixa automaticamente as músicas enviadas em conversas do WhatsApp a partir de um único script, sem precisar copiar link por link.

O serviço recebe como parâmetros o caminho do arquivo de texto da conversa (ou um arquivo com os links) e o diretório onde as músicas devem ser salvas. Todo o resto — extração, validação, download, nomes limpos e tags — é feito de ponta a ponta com uma única chamada.

---

## Recursos

- **Processo único**: chamar somente `baixador.py` resolve extração + validação + download.
- **Entrada flexível**: aceita o arquivo `.txt` exportado do WhatsApp ou um `.txt` simples com os links.
- **Validação de links**: só baixa de plataformas permitidas (YouTube, Facebook e TikTok).
- **Nomes limpos**: remove hashtags, emojis, contadores de visualizações e URLs do título.
- **Tags ID3**: grava título, artista, data e gênero no MP3, legíveis no Windows Explorer.
- **Sem duplicatas**: ignora vídeos já baixados (por ID) e exclui conteúdo repetido (por hash SHA-256).
- **Tolerante a falhas**: links que falham são salvos em um arquivo para tratamento posterior.
- **Ambiente automático**: instala `yt-dlp` e baixa o FFmpeg caso não estejam presentes.

---

## Pré-requisitos

| Item | Observação |
|------|------------|
| Python 3.8 ou superior | Testado com Python 3.11 |
| Conexão com a internet | Necessária para extração e download |
| FFmpeg | Baixado automaticamente pelo script, se não encontrado |
| yt-dlp | Instalado automaticamente pelo script, se não encontrado |

Não é preciso instalar nada manualmente: o próprio `baixador.py` prepara o ambiente na primeira execução.

---

## Como usar

### 1. Clone o repositório

```powershell
git clone https://SEU_REPOSITORIO/IguinhoMP3.git
cd IguinhoMP3
```

### 2. Execute o serviço

```powershell
python python\baixador.py <caminho_do_txt> <diretorio_destino>
```

Os dois parâmetros são **obrigatórios**:

| Parâmetro | Descrição |
|-----------|-----------|
| `caminho_do_txt` | Caminho do arquivo `.txt` da conversa do WhatsApp **ou** um arquivo `.txt` com os links (um por linha) |
| `diretorio_destino` | Pasta onde as músicas baixadas serão salvas |

> Dica: mantenha caminhos com espaços entre aspas, ex.: `"C:\Users\Voce\Desktop\conversa.txt"`.

### Exemplos de chamada

```powershell
# Conversa do WhatsApp exportada
python python\baixador.py "D:\Conversas\paulo_igor.txt" "D:\Musicas"

# Arquivo com links (um por linha)
python python\baixador.py "D:\links.txt" "D:\Musicas"

# Criando o destino automaticamente
python python\baixador.py "D:\conversa.txt" "D:\Musicas\Novas"
```

### Ajuda

```powershell
python python\baixador.py --help
```

---

## Cenários de execução

### Ao parametrizar os caminhos

| Cenário | O que acontece |
|---------|----------------|
| `conversa.txt` do WhatsApp + destino | O script extrai os links do texto da conversa, valida, gera o arquivo de links válidos e baixa as músicas |
| Arquivo `.txt` com links + destino | Os links são lidos do arquivo, validados e baixados (mesmo fluxo) |
| Destino **não existe** | A pasta é criada automaticamente (incluindo subpastas) |
| Destino em **disco indisponível** (ex.: unidade `Z:` não existe) | É impresso um erro no console e o processo é encerrado |
| Arquivo de conversa/links **não existe** | É impresso um erro no console e o processo é encerrado |

### Ao não parametrizar os caminhos

| Cenário | O que acontece |
|---------|----------------|
| Nenhum parâmetro informado | O console exibe: `error: the following arguments are required: conversa, destino` |
| Apenas um parâmetro informado | O console exibe o erro informando o parâmetro que falta |

Como os parâmetros são obrigatórios, o serviço **não executa o download** sem que os dois caminhos sejam informados — evitando baixar músicas para o lugar errado ou ler o arquivo errado.

---

## Como funciona

```
conversa.txt (ou links.txt)
        │
        ▼
[1. EXTRAÇÃO]  localiza todas as URLs no texto
        │
        ▼   gera arquivos/<data>.txt
[2. VALIDAÇÃO] mantém apenas links de plataformas permitidas
        │
        ▼   gera arquivos/links_validos_<data>.txt
[3. DOWNLOAD] baixa o áudio, converte para MP3,
              limpa o título e grava as tags ID3
        │
        ├── sucesso ──► diretório de destino (MP3)
        └── erro    ──► arquivos/links_com_erro_<data>.txt
```

### Fluxo detalhado

1. **Preparação do ambiente** — cria as pastas necessárias, instala `yt-dlp` e o FFmpeg (se preciso) e adiciona o FFmpeg ao PATH.
2. **Extração** (`extrator.py`) — varre o texto do arquivo informado e encontra todas as URLs, removendo duplicadas.
3. **Validação** (`validador.py`) — mantém apenas URLs de plataformas permitidas e grava `links_validos_<data>.txt`.
4. **Download** (`baixador.py`) — para cada link:
   - pula o vídeo se já existir arquivo com o mesmo ID;
   - baixa o melhor áudio disponível e converte para MP3 (192 kbps);
   - limpa o título e grava as tags ID3 (título, artista, data, gênero);
   - se o conteúdo já existir (mesmo hash), o arquivo recém-baixado é excluído;
   - se falhar, o link é registrado para a lista de erros.
5. **Encerramento** — limpa os temporários e mostra o resumo final.

---

## Estrutura do projeto

```
IguinhoMP3/
├── .gitignore
├── README.md
├── python/
│   ├── baixador.py              # Entrada principal: orquestra o processo todo
│   ├── extrator.py              # Extrai as URLs do texto da conversa
│   ├── validador.py             # Valida URLs e plataformas permitidas
│   └── validador_duplicacao.py  # Hash SHA-256 e utilitário de cópia p/ pendrive
├── arquivos/                    # (gerado) links extraídos, válidos e com erro
├── temp/                        # (gerado) arquivos temporários
├── ffmpeg/                      # (gerado) FFmpeg baixado automaticamente
└── musicas/                     # (gerado) destino padrão de exemplo
```

As pastas `arquivos/`, `temp/`, `ffmpeg/` e `musicas/` são criadas em tempo de execução e **não são versionadas** no repositório.

---

## Arquivos gerados

Todos os arquivos de apoio ficam em `arquivos/`:

| Arquivo | Conteúdo |
|---------|----------|
| `<data>.txt` | Links extraídos da conversa |
| `links_validos_<data>.txt` | Links aprovados na validação (usados no download) |
| `links_com_erro_<data>.txt` | Links que falharam no download — basta reutilizá-los numa nova execução |

Os nomes de arquivo contêm data/hora, então execuções diferentes não se sobrescrevem.

---

## Sobre os nomes das músicas

Os títulos vêm do vídeo e costumam ser poluídos (hashtags, emojis, contagens de visualizações). O serviço aplica uma limpeza automática:

```text
Antes:  Easy Bass Lines | Oye Como Va - Santana #BassTabs #EasyBassLines #fyp
Depois: Easy Bass Lines Oye Como Va - Santana [I26hNG4aflw].mp3
```

- O nome final é limitado a 80 caracteres e mantém o **ID do vídeo** entre colchetes para evitar conflitos.
- As **tags ID3** do MP3 recebem título limpo, artista (canal/uploader), data e gênero.
- Quando o vídeo não informa título útil (ex.: "TikTok video #123"), o serviço tenta montar `Artista - Faixa` quando esses dados existem.

---

## Evitando duplicatas

1. **Antes do download** — se já existe um arquivo com o mesmo ID do vídeo, o download é pulado.
2. **Depois do download** — o SHA-256 do arquivo é comparado com os já existentes; se for duplicado, o arquivo recém-baixado é excluído.

Isso garante que a mesma música não ocupe espaço duas vezes, mesmo que venha de um link diferente.

---

## Observações

- O caminho base do projeto (`PASTA_BASE`) está configurado no topo dos scripts. Se clonar para outra pasta, ajuste esse valor em `baixador.py` e `validador_duplicacao.py`.
- O utilitário de cópia para pendrive pode ser executado à parte: `python python\validador_duplicacao.py` (ajuste a constante `PENDRIVE`).
- Para reproduzir apenas os downloads que falharam, passe o arquivo `links_com_erro_<data>.txt` como parâmetro de entrada.

---

## Licença

Projeto pessoal. Nenhuma licença foi declarada ainda — entre em contato com o autor antes de reutilizar ou distribuir o código.