from config.constants import ADMIN_USER_ID
from telegram import (
    Update,
)


async def authorized(update: Update) -> bool:
    user = update.effective_user
    if user and user.id == ADMIN_USER_ID:
        return True

    if update.callback_query:
        await update.callback_query.answer(
            "Non autorizzato.", show_alert=True
        )
    elif update.effective_message:
        await update.effective_message.reply_text(
            "Non autorizzato."
        )
    return False