import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from telegram.request import HTTPXRequest

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = '8201264809:AAEc4BnUcY2NjyiwQdZP11zrhFHshJWTDno'
OWNER_IDS = [734572580, 1295431856]
BLOCKED_USERS_IDS = [123456789, 987654321]
BLOCKED_USERS_USERNAMES = []

group_settings = {}



def is_enabled(chat_id):
    return group_settings.get(chat_id, False)

async def enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ Только для владельца!")
        return
    group_settings[chat_id] = True
    await update.message.reply_text("✅ Удаление стикеров включено!")

async def disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ Только для владельца!")
        return
    group_settings[chat_id] = False
    await update.message.reply_text("❌ Удаление стикеров выключено!")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    enabled = group_settings.get(chat_id, False)
    if enabled:
        msg = "✅ Удаление стикеров *ВКЛЮЧЕНО* в этом чате."
    else:
        msg = "🔕 Удаление стикеров *ВЫКЛЮЧЕНО* в этом чате."
    await update.message.reply_text(msg, parse_mode="Markdown")


def is_owner(user_id: int) -> bool:
    return user_id in OWNER_IDS

def is_blocked(user_id: int, username: str = None) -> bool:
    return user_id in BLOCKED_USERS_IDS or (username and username in BLOCKED_USERS_USERNAMES)

def escape_markdown(text: str) -> str:
    escape_chars = r"_*[]()~`>#+-=|{}.!\\"
    return ''.join("\\" + c if c in escape_chars else c for c in (text or ""))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    owner_text = "\n\n🔐 - команды доступны только владельцу бота" if is_owner(user_id) else ""

    menu_text = (
        "👋 Привет! Я бот для удаления стикеров от Михача.\n\n"
        "📋 Команды:\n"
        "• /enable - Включить удаление стикеров\n"
        "• /disable - Выключить удаление стикеров\n"
        "• /status - Показать статус\n"
        "• /myid - Узнать свой ID\n"
        "• /block <ID> - Добавить пользователя в блоклист\n"
        "• /unblock <ID> - Удалить из блоклиста\n"
        "• /block_username <username> - Заблокировать пользователя по username\n"
        "• /unblock_username <username> - Разблокировать пользователя по username\n"
        "• /blocklist - Показать блоклист"
        f"{owner_text}"
    )

    await update.message.reply_text(menu_text)



async def getmyid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    userid = update.effective_user.id
    username = escape_markdown(update.effective_user.username or "нет")
    first_name = escape_markdown(update.effective_user.first_name or "")
    await update.message.reply_text(
        f"ID: {userid}\nUsername: {username}\nИмя: {first_name}",
        parse_mode="Markdown"
    )

async def block_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ Только для владельцев!")
        return
    if not context.args:
        await update.message.reply_text("/block <id>")
        return
    try:
        blocked_id = int(context.args[0])
        if blocked_id not in BLOCKED_USERS_IDS:
            BLOCKED_USERS_IDS.append(blocked_id)
            await update.message.reply_text(f"Пользователь с ID {blocked_id} заблокирован.")
            logger.info(f"Заблокирован ID: {blocked_id} by {user_id}")
        else:
            await update.message.reply_text(f"ID {blocked_id} уже в блок-листе.")
    except ValueError:
        await update.message.reply_text("Некорректный ID!")

async def block_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ Только для владельцев!")
        return
    if not context.args:
        await update.message.reply_text("/block_username <username>")
        return
    username = context.args[0].lstrip("@")
    username = username.casefold()
    if username not in BLOCKED_USERS_USERNAMES:
        BLOCKED_USERS_USERNAMES.append(username)
        await update.message.reply_text(f"Пользователь с username @{username} заблокирован.")
        logger.info(f"Заблокирован username: @{username} by {user_id}")
    else:
        await update.message.reply_text(f"@{username} уже в блок-листе.")

async def unblock_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ Только для владельцев!")
        return
    if not context.args:
        await update.message.reply_text("/unblock <id>")
        return
    try:
        unblocked_id = int(context.args[0])
        if unblocked_id in BLOCKED_USERS_IDS:
            BLOCKED_USERS_IDS.remove(unblocked_id)
            await update.message.reply_text(f"Пользователь с ID {unblocked_id} разблокирован.")
            logger.info(f"Разблокирован ID: {unblocked_id} by {user_id}")
        else:
            await update.message.reply_text(f"ID {unblocked_id} не найден в блок-листе.")
    except ValueError:
        await update.message.reply_text("Некорректный ID!")

async def unblock_username(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ Только для владельцев!")
        return
    if not context.args:
        await update.message.reply_text("/unblock_username <username>")
        return
    username = context.args[0].lstrip("@")
    username = username.casefold()
    if username in BLOCKED_USERS_USERNAMES:
        BLOCKED_USERS_USERNAMES.remove(username)
        await update.message.reply_text(f"Пользователь с username @{username} разблокирован.")
        logger.info(f"Разблокирован username: @{username} by {user_id}")
    else:
        await update.message.reply_text(f"@{username} не найден в блок-листе.")

async def show_blocklist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_owner(user_id):
        await update.message.reply_text("⛔ Только для владельцев!")
        return

    ids = "\n".join(f"`{uid}`" for uid in BLOCKED_USERS_IDS) or "-"
    usernames = "\n".join(f"@{escape_markdown(u)}" for u in BLOCKED_USERS_USERNAMES) or "-"

    msg = (
        "🛑 *Текущий блоклист:*\n"
        "\n*ID:*\n" + ids +
        "\n\n*Username:*\n" + usernames
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def sticker_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверка, активен ли режим удаления стикеров в этом чате
    chat_id = update.effective_chat.id
    if not is_enabled(chat_id):
        return
    # Извлечь user_id и username отправителя
    user_id = update.effective_user.id
    username = (update.effective_user.username or "").casefold()
    # Если пользователь в блоклистах — удалить стикер
    if is_blocked(user_id, username):
        try:
            await update.message.delete()
            logger.info(f"Удалён стикер от: {user_id}, username: {username}")
        except Exception as e:
            logger.error(f"Ошибка при удалении стикера: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Ошибка: {context.error}")

def main():
    request = HTTPXRequest(connection_pool_size=8)
    application = Application.builder().token(BOT_TOKEN).request(request).build()

    application.add_handler(CommandHandler("enable", enable, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("disable", disable, filters=filters.ChatType.GROUPS))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("myid", getmyid))
    application.add_handler(CommandHandler("block", block_user))
    application.add_handler(CommandHandler("block_username", block_username))
    application.add_handler(CommandHandler("unblock", unblock_user))
    application.add_handler(CommandHandler("unblock_username", unblock_username))
    application.add_handler(CommandHandler("blocklist", show_blocklist))

    application.add_handler(MessageHandler(filters.Sticker.ALL, sticker_handler))

    application.add_error_handler(error_handler)

    logger.info("🚀 Бот запущен!")
    logger.info(f"👑 Владельцы: {OWNER_IDS}")
    logger.info(f"🚫 Заблокированные пользователи: {BLOCKED_USERS_IDS}")
    logger.info(f"🚫 Заблокированные username: {BLOCKED_USERS_USERNAMES}")

    application.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)

if __name__ == "__main__":
    main()
