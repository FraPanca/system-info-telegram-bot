import asyncio
import time

import psutil
from middleware.auth import authorized
from middleware.log import logger
from telegram import Update
from telegram.ext import ContextTypes


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not await authorized(update):
    return

  await update.effective_message.reply_text(
      "Ciao! Ti fornisco le informazioni del tuo sistema.\n\n"
      "Usa /stats per visualizzare le metriche del sistema e /shutdown per spegnerlo.\n"
      "Scrivi /help per tutti i comandi."
  )


async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not await authorized(update):
    return

  # 1. CPU
  cpu_usage = await asyncio.to_thread(psutil.cpu_percent, 1)

  # 2. RAM (GB)
  ram = psutil.virtual_memory()
  ram_totale = ram.total / (1024**3)
  ram_usata = ram.used / (1024**3)
  ram_perc = ram.percent

  # 3. Disco principale '/' (GB)
  disco = psutil.disk_usage("/")
  disco_totale = disco.total / (1024**3)
  disco_usato = disco.used / (1024**3)
  disco_perc = disco.percent

  # 4. Temperatura
  temp_attuale = "N/D"
  if hasattr(psutil, "sensors_temperatures"):
    temps = psutil.sensors_temperatures()
    for nome_sensore in ["coretemp", "cpu_thermal", "k10temp", "acpitz"]:
      if temps.get(nome_sensore):
        temp_attuale = f"{temps[nome_sensore][0].current} °C"
        break

  # 5. Uptime
  boot_time = psutil.boot_time()
  secondi_attivi = int(time.time() - boot_time)
  ore, resto = divmod(secondi_attivi, 3600)
  minuti, _ = divmod(resto, 60)

  text = (
      f"📊 **Stato del Sistema**\n\n"
      f"• **CPU:** {cpu_usage}%\n"
      f"• **RAM:** {ram_usata:.1f} GB / {ram_totale:.1f} GB ({ram_perc}%)\n"
      f"• **Disco:** {disco_usato:.1f} GB / {disco_totale:.1f} GB ({disco_perc}%)\n"
      f"• **Temperatura:** {temp_attuale}\n"
      f"• **Uptime:** {ore} ore e {minuti} minuti"
  )

  await update.effective_message.reply_text(text, parse_mode="Markdown")


async def shutdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not await authorized(update):
    return

  logger.warning(
      f"Comando /shutdown richiesto dall'utente {update.effective_user.id}"
  )
  await update.effective_message.reply_text(
      "🛑 Spegnimento del sistema in corso..."
  )

  process = await asyncio.create_subprocess_exec(
      "sudo",
      "shutdown",
      "-h",
      "now",
      stdout=asyncio.subprocess.PIPE,
      stderr=asyncio.subprocess.PIPE,
  )
  _, stderr = await process.communicate()

  if process.returncode != 0:
    errore = stderr.decode().strip()
    logger.error(f"Errore durante lo spegnimento: {errore}")
    await update.effective_message.reply_text(
        f"⚠️ Errore durante lo spegnimento:\n`{errore}`",
        parse_mode="Markdown",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
  if not await authorized(update):
    return

  text = (
      "/stats - mostra le metriche del sistema\n"
      "/shutdown - spegne il sistema\n"
      "/help - mostra questo messaggio"
  )

  await update.effective_message.reply_text(text)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
  logger.error(
      "Errore durante l'elaborazione di un aggiornamento",
      exc_info=context.error,
  )
  if isinstance(update, Update) and update.effective_message:
    try:
      await update.effective_message.reply_text(
          "⚠️ Si è verificato un errore. Riprova tra poco."
      )
    except Exception:  # noqa: BLE001
      logger.exception("Impossibile inviare il messaggio di errore")
