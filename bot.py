import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from dotenv import load_dotenv
from pc_parser import PCParser
from components_parser import ComponentsParser
import json
import pandas as pd
import logging
from datetime import datetime, timedelta

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

# Глобальные переменные для хранения состояния
user_states = {}
parsers = {
    'pc': None,
    'components': None
}
last_update = None
UPDATE_INTERVAL = timedelta(hours=1)

def get_parser(parser_type):
    """Получение или создание парсера нужного типа"""
    global parsers, last_update
    
    current_time = datetime.now()
    
    # Если парсер не существует или нужно обновить данные
    if (parsers[parser_type] is None or 
        last_update is None or 
        current_time - last_update > UPDATE_INTERVAL):
        
        try:
            if parser_type == 'pc':
                parsers[parser_type] = PCParser()
                parsers[parser_type].update_data()
            elif parser_type == 'components':
                parsers[parser_type] = ComponentsParser()
                parsers[parser_type].update_data()
            
            last_update = current_time
            logger.info(f"Парсер {parser_type} успешно инициализирован")
        except Exception as e:
            logger.error(f"Ошибка при инициализации парсера {parser_type}: {str(e)}")
            return None
    
    return parsers[parser_type]

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
            await update.message.reply_text("Собираю актуальные данные о сборках ПК...")
            
            parser = get_parser('pc')
            if parser is None:
                await update.message.reply_text(
                    "Извините, произошла ошибка при получении данных. Попробуйте позже."
                )
                return
            
            try:
                build = parser.get_random_build(
                    budget=budget,
                    purpose=state.get('purpose', 'work'),
                    type=state.get('action', 'pc')
                )
                
                if build:
                    message = f"Вот что я нашел для вас:\n\n"
                    message += f"💻 Тип: {'Ноутбук' if state.get('action') == 'build_laptop' else 'ПК'}\n"
                    message += f"🎯 Назначение: {'Игровой' if state.get('purpose') == 'gaming' else 'Рабочий'}\n"
                    message += f"💰 Бюджет: {budget} руб.\n\n"
                    message += f"📋 Комплектация:\n{build['title']}\n\n"
                    message += f"💵 Цена: {build['price']} руб.\n"
                    message += f"🏪 Магазин: {build['source']}\n"
                    message += f"🔗 Ссылка: {build['url']}"
                    
                    # Добавляем кнопку для поиска другой сборки
                    keyboard = [[InlineKeyboardButton("Найти другую сборку", callback_data=state.get('action'))]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(message, reply_markup=reply_markup)
                else:
                    # Добавляем кнопку для изменения параметров поиска
                    keyboard = [[InlineKeyboardButton("Изменить параметры поиска", callback_data="start")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        "К сожалению, не удалось найти подходящую сборку. Попробуйте изменить бюджет или параметры.",
                        reply_markup=reply_markup
                    )
                
                # Очищаем состояние пользователя после успешного поиска
                user_states[user_id] = {}
                
            except Exception as e:
                logger.error(f"Ошибка при получении сборки: {str(e)}")
                await update.message.reply_text(
                    "Произошла ошибка при поиске сборки. Попробуйте позже."
                )
        elif state.get('action') == 'components':
            category = state.get('category')
            if not category:
                await update.message.reply_text("Не выбрана категория комплектующих. Попробуйте начать заново с команды /start")
                return
                
            parser = get_parser('components')
            if parser is None:
                await update.message.reply_text(
                    "Извините, произошла ошибка при получении данных. Попробуйте позже."
                )
                return
            
            try:
                await update.message.reply_text("Собираю актуальные данные о комплектующих...")
                component = parser.get_component_by_budget(category, budget)
                
                if component:
                    message = f"Вот что я нашел для вас:\n\n"
                    message += f"📦 Категория: {category}\n"
                    message += f"💰 Бюджет: {budget} руб.\n\n"
                    message += f"📋 Название: {component['title']}\n"
                    message += f"💵 Цена: {component['price']} руб.\n"
                    message += f"🏪 Магазин: {component['source']}\n"
                    message += f"🔗 Ссылка: {component['url']}"
                    
                    # Добавляем кнопку для поиска другого комплектующего
                    keyboard = [[InlineKeyboardButton("Найти другое комплектующее", callback_data="components")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(message, reply_markup=reply_markup)
                else:
                    # Добавляем кнопку для изменения параметров поиска
                    keyboard = [[InlineKeyboardButton("Изменить параметры поиска", callback_data="start")]]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await update.message.reply_text(
                        "К сожалению, не удалось найти подходящее комплектующее. "
                        "Попробуйте увеличить бюджет или выбрать другую категорию.",
                        reply_markup=reply_markup
                    )
                
                # Очищаем состояние пользователя после успешного поиска
                user_states[user_id] = {}
                
            except Exception as e:
                logger.error(f"Ошибка при получении комплектующего: {str(e)}")
                await update.message.reply_text(
                    "Произошла ошибка при поиске комплектующего. Попробуйте позже."
                )
        else:
            await update.message.reply_text("Неизвестное действие. Попробуйте начать заново с команды /start")
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите корректное число для бюджета:")
    except Exception as e:
        logger.error(f"Ошибка при обработке бюджета: {str(e)}")
        await update.message.reply_text(
            "Произошла ошибка. Попробуйте начать заново с команды /start"
        )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик callback-запросов"""
    query = update.callback_query
    user_id = query.from_user.id
    
    try:
        if query.data in ['build_pc', 'build_laptop']:
            user_states[user_id] = {'action': query.data}
            await show_purpose(update, context)
        elif query.data in ['purpose_work', 'purpose_gaming']:
            if user_id in user_states:
                user_states[user_id]['purpose'] = 'work' if query.data == 'purpose_work' else 'gaming'
                await query.message.reply_text(
                    "Введите ваш бюджет в рублях:"
                )
        elif query.data == 'components':
            user_states[user_id] = {'action': 'components'}
            await show_component_categories(update, context)
        elif query.data.startswith('comp_'):
            if user_id in user_states:
                user_states[user_id]['category'] = query.data.replace('comp_', '')
                await query.message.reply_text(
                    "Введите ваш бюджет в рублях:"
                )
    except Exception as e:
        logger.error(f"Ошибка при обработке callback: {str(e)}")
        await query.message.reply_text(
            "Произошла ошибка. Попробуйте начать заново с команды /start"
        )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    text = update.message.text
    user_id = update.effective_user.id
    
    # Проверяем, ожидаем ли ввод бюджета
    if user_id in user_states and 'action' in user_states[user_id]:
        await handle_budget(update, context)
        return
        
    # Проверяем, является ли сообщение URL конфигурации DNS
    if 'dns-shop.ru/user-pc/configuration/' in text:
        await analyze_configuration(update, context, text)
        return
        
    # Если не распознали команду, отправляем помощь
    await start(update, context)

async def analyze_configuration(update: Update, context: ContextTypes.DEFAULT_TYPE, url: str):
    """Анализ конфигурации DNS"""
    try:
        await update.message.reply_text("Анализирую конфигурацию, это может занять некоторое время...")
        
        parser = get_parser('pc')
        if parser is None:
            await update.message.reply_text(
                "Извините, произошла ошибка при инициализации парсера. Попробуйте позже."
            )
            return
            
        build = parser.get_build_by_url(url)
        
        if build:
            message = "📋 Анализ конфигурации:\n\n"
            message += f"🖥 Название: {build['title']}\n"
            message += f"💰 Общая стоимость: {build['total_price']} руб.\n\n"
            message += "🔧 Компоненты:\n"
            
            for component in build['components']:
                message += f"• {component['title']} - {component['price']} руб.\n"
            
            message += f"\n🔗 Ссылка: {build['url']}"
            
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(
                "К сожалению, не удалось получить информацию о конфигурации. "
                "Проверьте правильность ссылки или попробуйте позже."
            )
    except Exception as e:
        logger.error(f"Ошибка при анализе конфигурации: {str(e)}")
        await update.message.reply_text(
            "Произошла ошибка при анализе конфигурации. Попробуйте позже."
        )

def main():
    """Запуск бота"""
    try:
        # Создаем приложение
        application = Application.builder().token(TOKEN).build()
        
        # Добавляем обработчики
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CallbackQueryHandler(handle_callback))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        # Запускаем бота
        logger.info("Бот запущен")
        application.run_polling()
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {str(e)}")

if __name__ == "__main__":
    main()








