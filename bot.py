import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from pc_parser import PCParser
from components_parser import ComponentsParser
import json
import pandas as pd


load_dotenv()


TOKEN = os.getenv("TOKEN")


user_states = {}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("Сборка ПК", callback_data="build_pc"),
            InlineKeyboardButton("Ноутбук", callback_data="build_laptop")
        ],
        [
            InlineKeyboardButton("Комплектующие", callback_data="components")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Привет! Я бот-помощник для сборки компьютера. Выберите, что вас интересует:",
        reply_markup=reply_markup
    )

async def show_purpose(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ кнопок выбора назначения"""
    keyboard = [
        [
            InlineKeyboardButton("Для работы", callback_data="purpose_work"),
            InlineKeyboardButton("Для игр", callback_data="purpose_gaming")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        "Выберите назначение компьютера:",
        reply_markup=reply_markup
    )

async def show_component_categories(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показ категорий комплектующих"""
    keyboard = [
        [
            InlineKeyboardButton("Процессоры", callback_data="comp_cpu"),
            InlineKeyboardButton("Видеокарты", callback_data="comp_gpu")
        ],
        [
            InlineKeyboardButton("Материнские платы", callback_data="comp_motherboard"),
            InlineKeyboardButton("Оперативная память", callback_data="comp_ram")
        ],
        [
            InlineKeyboardButton("Накопители", callback_data="comp_storage")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        "Выберите категорию комплектующих:",
        reply_markup=reply_markup
    )

async def handle_budget(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ввода бюджета"""
    user_id = update.effective_user.id
    try:
        budget = int(update.message.text)
        if budget <= 0:
            await update.message.reply_text("Бюджет должен быть положительным числом. Попробуйте еще раз:")
            return
        
        state = user_states.get(user_id, {})
        if state.get('action') in ['build_pc', 'build_laptop']:
            # Получаем случайную сборку
            parser = PCParser()
            try:
                parser.parse_dns()
                parser.parse_citilink()
                parser.parse_mvideo()
                
                build = parser.get_random_build(
                    budget=budget,
                    purpose=state.get('purpose', 'work'),
                    type=state.get('action', 'pc')
                )
                
                if build:
                    message = f"Вот что я нашел для вас:\n\n"
                    message += f"Название: {build['title']}\n"
                    message += f"Цена: {build['price']}₽\n"
                    message += f"Магазин: {build['source']}\n"
                    message += f"Ссылка: {build['url']}\n"
                    
                    # Добавляем кнопку для поиска другой сборки
                    keyboard = [[InlineKeyboardButton("Найти другую сборку", callback_data=state.get('action'))]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(message, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(
                        "К сожалению, для вашего бюджета не найдено подходящих сборок. "
                        "Попробуйте увеличить бюджет или изменить параметры поиска."
                    )
            finally:
                parser.close()
        elif state.get('action') == 'components':
            # Получаем комплектующее
            category = state.get('category')
            if not category:
                await update.message.reply_text("Ошибка: категория не выбрана. Попробуйте начать заново с команды /start")
                return
                
            parser = ComponentsParser()
            try:
                parser.main(category)
                component = parser.get_component_by_budget(category, budget)
                
                if component:
                    message = f"Вот что я нашел для вас:\n\n"
                    message += f"Название: {component['title']}\n"
                    message += f"Цена: {component['price']}₽\n"
                    message += f"Магазин: {component['source']}\n"
                    message += f"Ссылка: {component['url']}\n"
                    
                    # Добавляем кнопку для поиска другого комплектующего
                    keyboard = [[InlineKeyboardButton("Найти другое комплектующее", callback_data="components")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(message, reply_markup=reply_markup)
                else:
                    await update.message.reply_text(
                        "К сожалению, для вашего бюджета не найдено подходящих комплектующих. "
                        "Попробуйте увеличить бюджет или выбрать другую категорию."
                    )
            finally:
                parser.close()
        else:
            await update.message.reply_text("Неизвестное действие. Попробуйте начать заново с команды /start")
            
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число. Попробуйте еще раз:")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    
    if query.data in ["build_pc", "build_laptop"]:
        user_states[user_id] = {'action': query.data}
        await show_purpose(update, context)
    elif query.data in ["purpose_work", "purpose_gaming"]:
        state = user_states.get(user_id, {})
        state['purpose'] = 'work' if query.data == 'purpose_work' else 'gaming'
        user_states[user_id] = state
        await query.message.reply_text(
            'Отлично! Теперь укажите ваш бюджет в рублях:'
        )
    elif query.data == "components":
        user_states[user_id] = {'action': 'components'}
        await show_component_categories(update, context)
    elif query.data.startswith("comp_"):
        state = user_states.get(user_id, {})
        state['category'] = query.data.replace("comp_", "")
        user_states[user_id] = state
        await query.message.reply_text(
            'Отлично! Теперь укажите ваш бюджет в рублях:'
        )
    else:
        await query.message.reply_text(
            'Извините, я не понимаю ваш запрос.'
        )

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_budget))

    application.run_polling()

if __name__ == "__main__":
    main()








