# Telegram System Info Bot

## Italiano

Bot Telegram personale per controllare lo stato di un sistema Linux (come un Raspberry Pi) e spegnerlo da remoto.

**Stack:** Python · python-telegram-bot · psutil · systemd (deploy)

### Descrizione

Bot Telegram ad uso privato che restituisce le metriche principali del sistema su cui gira (CPU, RAM, disco, temperatura, uptime) e permette di spegnerlo con un comando direttamente dalla chat. L'accesso è limitato a un singolo utente autorizzato tramite il suo ID Telegram numerico. Il codice è organizzato in moduli separati (configurazione, middleware, handler) e include un file di unit systemd di esempio per l'esecuzione come servizio persistente.

### Come si esegue

1. Crea un virtualenv e installa le dipendenze:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copia il template in `.env`:
   ```
   cp .env.example .env
   ```

3. Compila `.env` con `TELEGRAM_BOT_TOKEN` (ottenuto da [@BotFather](https://t.me/BotFather)) e `TELEGRAM_USER_ID_ADMIN` (il tuo ID numerico Telegram, unico utente autorizzato).

4. Solo per `/shutdown`: consenti all'utente che esegue il bot di lanciare lo spegnimento senza password. Crea un file dedicato con `sudo visudo -f /etc/sudoers.d/systeminfo-bot` e inserisci una riga come questa (sostituisci `TUO_UTENTE` e verifica il percorso di `shutdown` con `command -v shutdown`):
   ```
   TUO_UTENTE ALL=(root) NOPASSWD: /usr/sbin/shutdown -h now
   ```
   Senza questa regola `/shutdown` risponde con un errore e il sistema non si spegne.

5. Avvia il bot:
   ```
   python src/bot.py
   ```

Per un deploy come servizio persistente è incluso un file di unit systemd in `ops/`: va copiato senza il suffisso `.example`, adattato (utente e percorsi) e installato con `systemctl` per far partire il bot automaticamente all'avvio e riavviarlo in caso di crash:

```
sudo cp ops/systeminfo-telegram.service.example /etc/systemd/system/systeminfo-telegram.service
sudo systemctl daemon-reload
sudo systemctl enable --now systeminfo-telegram.service
```

Il comando di avvio nell'unit deve puntare a `src/bot.py`, usando il Python del virtualenv (`venv/bin/python`).

### Funzionalità principali

- Autenticazione a singolo utente: solo l'ID Telegram configurato in `TELEGRAM_USER_ID_ADMIN` può usare il bot; ogni altro utente riceve un rifiuto generico ("Non autorizzato"), senza rivelare ulteriori dettagli sul bot
- Comandi: `/stats` (metriche del sistema), `/shutdown` (spegne il sistema), `/start`, `/help`
- `/stats` mostra uso della CPU (misurato su un secondo, in un thread separato per non bloccare il bot), RAM usata e totale in GB, disco principale `/` usato e totale in GB, temperatura e uptime in ore e minuti
- La temperatura viene letta dal primo sensore disponibile tra `coretemp`, `cpu_thermal`, `k10temp` e `acpitz`; se nessuno è presente compare "N/D"
- `/shutdown` esegue `sudo shutdown -h now`, registra nel log l'ID di chi l'ha richiesto e, se il comando fallisce, riporta l'errore in chat
- Comandi del bot registrati automaticamente su Telegram (menu nativo) all'avvio
- Logging centralizzato (livello INFO) e gestione degli errori dedicata, con messaggio di avviso all'utente in caso di errore imprevisto
- Deploy come servizio systemd con riavvio automatico in caso di crash

### Struttura del progetto

```
systeminfo/
├── ops/                          # Configurazione per il deploy (unit systemd di esempio)
├── src/
│   ├── bot.py                    # Entry point: crea l'applicazione, registra handler e comandi
│   ├── config/
│   │   └── constants.py          # Caricamento di .env, token e ID dell'utente autorizzato
│   ├── middleware/
│   │   ├── auth.py               # Controllo dell'utente autorizzato
│   │   └── log.py                # Configurazione del logging
│   └── services/
│       └── handlers.py           # Handler dei comandi (start, help, stats, shutdown) e degli errori
├── requirements.txt              # Dipendenze Python
├── .env.example                  # Template delle variabili d'ambiente richieste
├── .env                          # Configurazione locale (non va nel repository)
└── LICENSE                       # Licenza MIT
```

### Note

Il bot è pensato per Linux: la lettura delle temperature con `psutil` e lo spegnimento tramite `sudo shutdown` non sono disponibili su tutti i sistemi. Il comando `/shutdown` spegne davvero la macchina e non chiede conferma: per riaccenderla serve un intervento fisico (ad esempio ricollegare l'alimentazione di un Raspberry Pi).

Il file di unit systemd incluso in `ops/` contiene un utente e dei percorsi segnaposto (`TUO_UTENTE`, `/home/TUO_UTENTE/telegram-bots/systeminfo`) da sostituire con i propri prima dell'uso. Non attiva volutamente `NoNewPrivileges`, che impedirebbe a `sudo` di funzionare e quindi bloccherebbe `/shutdown`.

Il disco mostrato da `/stats` è solo quello montato su `/`: eventuali dischi aggiuntivi non vengono riportati. Gli import interni usano percorsi relativi a `src/` (es. `from config.constants import TOKEN`), quindi il bot va avviato come script (`python src/bot.py`) e non come pacchetto.

### Licenza

MIT

---

## English

A personal Telegram bot for checking the status of a Linux system (such as a Raspberry Pi) and shutting it down remotely.

**Stack:** Python · python-telegram-bot · psutil · systemd (deployment)

### Description

A private-use Telegram bot that reports the main metrics of the system it runs on (CPU, RAM, disk, temperature, uptime) and can shut it down with a single command from the chat. Access is restricted to a single authorized user via their numeric Telegram ID. The code is split into separate modules (configuration, middleware, handlers) and includes a sample systemd unit file for running it as a persistent service.

### How to run

1. Create a virtualenv and install dependencies:
   ```
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. Copy the template to `.env`:
   ```
   cp .env.example .env
   ```

3. Fill in `.env` with `TELEGRAM_BOT_TOKEN` (obtained from [@BotFather](https://t.me/BotFather)) and `TELEGRAM_USER_ID_ADMIN` (your numeric Telegram ID, the only authorized user).

4. Only for `/shutdown`: allow the user running the bot to run the shutdown command without a password. Create a dedicated file with `sudo visudo -f /etc/sudoers.d/systeminfo-bot` and add a line like this (replace `TUO_UTENTE` and check the path of `shutdown` with `command -v shutdown`):
   ```
   TUO_UTENTE ALL=(root) NOPASSWD: /usr/sbin/shutdown -h now
   ```
   Without this rule `/shutdown` replies with an error and the system does not power off.

5. Start the bot:
   ```
   python src/bot.py
   ```

For a persistent service deployment, a systemd unit file is included in `ops/`: copy it without the `.example` suffix, adapt it (user and paths) and install it with `systemctl` so the bot starts automatically on boot and restarts on crash:

```
sudo cp ops/systeminfo-telegram.service.example /etc/systemd/system/systeminfo-telegram.service
sudo systemctl daemon-reload
sudo systemctl enable --now systeminfo-telegram.service
```

The start command in the unit must point to `src/bot.py`, using the virtualenv's Python (`venv/bin/python`).

### Key features

- Single-user authentication: only the Telegram ID set in `TELEGRAM_USER_ID_ADMIN` can use the bot; any other user receives a generic "Not authorized" reply, with no further details about the bot revealed
- Commands: `/stats` (system metrics), `/shutdown` (power off the system), `/start`, `/help`
- `/stats` shows CPU usage (sampled over one second, in a separate thread so the bot is not blocked), used and total RAM in GB, used and total space of the main disk `/` in GB, temperature, and uptime in hours and minutes
- The temperature is read from the first available sensor among `coretemp`, `cpu_thermal`, `k10temp` and `acpitz`; if none is present, "N/D" is shown
- `/shutdown` runs `sudo shutdown -h now`, logs the ID of whoever requested it and, if the command fails, reports the error in the chat
- Bot commands automatically registered with Telegram (native menu) on startup
- Centralized logging (INFO level) and dedicated error handling, with a notice sent to the user on unexpected errors
- Deployed as a systemd service with automatic restart on crash

### Project structure

```
systeminfo/
├── ops/                          # Deployment configuration (sample systemd unit)
├── src/
│   ├── bot.py                    # Entry point: builds the application, registers handlers and commands
│   ├── config/
│   │   └── constants.py          # Loads .env, token and authorized user ID
│   ├── middleware/
│   │   ├── auth.py               # Authorized-user check
│   │   └── log.py                # Logging configuration
│   └── services/
│       └── handlers.py           # Command handlers (start, help, stats, shutdown) and error handler
├── requirements.txt              # Python dependencies
├── .env.example                  # Template for the required environment variables
├── .env                          # Local configuration (not committed)
└── LICENSE                       # MIT license
```

### Notes

The bot is meant for Linux: reading temperatures with `psutil` and shutting down via `sudo shutdown` are not available on every system. The `/shutdown` command really powers off the machine and does not ask for confirmation: turning it back on requires a physical action (for example reconnecting the power supply of a Raspberry Pi).

The systemd unit file included in `ops/` contains a placeholder user and paths (`TUO_UTENTE`, `/home/TUO_UTENTE/telegram-bots/systeminfo`) that need to be replaced with real ones before use. It deliberately does not enable `NoNewPrivileges`, which would stop `sudo` from working and therefore break `/shutdown`.

The disk shown by `/stats` is only the one mounted on `/`: any additional disks are not reported. Internal imports are relative to `src/` (e.g. `from config.constants import TOKEN`), so the bot must be started as a script (`python src/bot.py`) rather than as a package.

### License

MIT