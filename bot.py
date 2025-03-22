import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()


TOKEN = os.getenv("TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Сборка ПК", callback_data="build_pc"),
            InlineKeyboardButton("Ноутбука", callback_data="build_laptop")
            InlineKeyboardButton("Комплектующие", callback_data="components")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! Я бот-помощник для сборки компьютера. Выберите, что вас интересует:",
         reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "build_pc":
        await query.message.reply_text(
            'Для начала, укажите ваш бюджет:'
        )
    elif query.data == "build_laptop":
        await query.message.reply_text(
            'Для начала, укажите ваш бюджет:'
        )
    elif query.data == "components":
        await query.message.reply_text(
            'Для начала, укажите ваш бюджет:'
        )
    elif query.data == "components":
        await query.message.reply_text(
            'Выберите категорию комплектующих:\n'
            '1. Процессоры\n'
            '2. Материнские платы\n'
            '3. Видеокарты\n'
            '4. Оперативная память\n'
            '5. Жесткие диски\n'
            '6. SSD\n'
            '7. Блоки питания\n'
            '8. Кулеры\n'
            '9. Корпуса\n'
            '10. Охлаждение\n'
        )
    else:
        await query.message.reply_text(
            'Извините, я не понимаю ваш запрос.'
        )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == "__main__":
    main()








