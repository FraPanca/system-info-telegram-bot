from config.constants import TOKEN
from middleware.log import logger
from services.handlers import (
    error_handler,
    help_command,
    shutdown_command,
    start,
    stats_command,
)
from telegram import (
    BotCommand,
)
from telegram.ext import (
    Application,
    CommandHandler,
)


async def post_init(app: Application):
    commands = [
        BotCommand("start", "Avvia il bot"),
        BotCommand("stats", "Visualizza le metriche"),
        BotCommand("shutdown", "Spegni il raspberry"),
        BotCommand("help", "Mostra l'aiuto"),
    ]
    await app.bot.set_my_commands(commands)


def main():
    app = (
        Application.builder()
        .token(TOKEN)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("shutdown", shutdown_command))
    app.add_error_handler(error_handler)

    logger.info("Avvio del bot Telegram")
    app.run_polling()


if __name__ == "__main__":
    main()
