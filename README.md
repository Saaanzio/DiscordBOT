# Discord bot

Um bot do Discord em Python focado em comandos de música e algumas interações em texto. O bot originalmente foi feito para aprender Python e proporcionar bons momentos em grupos no Discord.

## Funcionalidades

- **Slash commands** (Discord Application Commands):
  - `/greet` – Dá bom dia mencionando o usuário.
  - `/modo_irritante` – Liga/desliga o modo que responde a todas as mensagens de texto dos usuários.
  - `/play <termo>` – Toca música do YouTube (busca com yt-dlp) no canal de voz do usuário e gerencia fila por servidor.
  - `/skip` – Pula a música atual.
  - `/show_queue` – Mostra a fila de músicas atual do servidor.
  - `/pause` – Pausa a música.
  - `/resume` – Retoma a música pausada.
  - `/stop` – Para a reprodução, limpa a fila e desconecta do canal de voz.

- **Eventos**:
  - `on_ready` – Loga no console quando o bot está online.
  - `on_message` – Se o modo irritante estiver ativado, responde a qualquer mensagem de usuário.
  - `on_message_edit` – Avisa quando uma mensagem é editada, mostrando o antes e o depois.

## Pré-requisitos

- Python 3.9+ (recomendado)
- [ffmpeg](https://ffmpeg.org/) binário disponível em `bin/ffmpeg/ffmpeg.exe` (pasta já esperada pelo código).
- Token de bot do Discord (criado no [Discord Developer Portal](https://discord.com/developers/applications)).

## Configuração do ambiente

1. Instale as dependências Python:

   > As principais libs usadas são: `discord.py`, `python-dotenv` e `yt-dlp`.

2. Crie um arquivo `.env` na raiz do projeto (baseando-se em `.env-example`, se existir) com, pelo menos:

   ```env
   DISCORD_TOKEN=seu_token_aqui
   ```

3. Verifique se o ffmpeg está no caminho esperado:

   - Windows: `bin/ffmpeg/ffmpeg.exe`
   - Se você quiser usar uma instalação global de ffmpeg, ajuste o caminho passado a `discord.FFmpegOpusAudio` em `discordbot.py`.

## Como rodar

Dentro da pasta do projeto:

```bash
python discordbot.py
```

Se o token estiver correto e o bot tiver sido adicionado ao seu servidor, ele ficará online e os comandos slash aparecerão (pode levar minutos até horas).

## Estrutura básica do projeto

- `discordbot.py` – Arquivo principal do bot, contendo configuração, eventos e comandos.
- `bin/ffmpeg/` – Binário do ffmpeg utilizado para tocar áudio nos canais de voz.

## Observações

- A fila de músicas é mantida em memória por servidor usando um `deque`.
- O bot usa `yt-dlp` para buscar e extrair a URL de áudio do YouTube sem baixar o arquivo.
- Caso os slash commands não apareçam, confira se o bot tem as permissões corretas e se você está no servidor onde ele foi registrado.
