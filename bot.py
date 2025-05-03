import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from database import (
    get_db_connection, update_user_last_active, get_device_types,
    get_price_categories, get_component_categories, get_build_details,
    get_builds_by_type_and_price, get_components_by_category, get_component_details,
    get_random_build
)
import json


load_dotenv()


(
    START,
    SELECTING_MAIN_MENU,
    SELECTING_DEVICE_TYPE,
    SELECTING_PRICE_CATEGORY,
    SELECTING_COMPONENT_CATEGORY,
    VIEWING_BUILDS,
    VIEWING_BUILD_DETAILS,
    VIEWING_COMPONENTS,
    VIEWING_COMPONENT_DETAILS,
) = range(9)

# Словарь для хранения состояний пользователей
user_states = {}

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен из переменной окружения
TOKEN = os.environ.get("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.effective_user
    
    # Сохраняем информацию о пользователе в базу данных
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Проверяем, существует ли пользователь в базе
    existing_user = cursor.execute(
        "SELECT * FROM users WHERE user_id = ?", 
        (user.id,)
    ).fetchone()
    
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if not existing_user:
        # Добавляем нового пользователя
        cursor.execute(
            """
            INSERT INTO users (user_id, username, first_name, last_name, registration_date, last_active)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (user.id, user.username, user.first_name, user.last_name, current_time, current_time)
        )
    else:
        # Обновляем время последней активности
        update_user_last_active(user.id)
    
    conn.commit()
    conn.close()
    
    # Сбрасываем состояние пользователя
    user_states[user.id] = {}
    
    # Создаем клавиатуру
    keyboard = [
        [
            InlineKeyboardButton("🖥️ Собрать ПК", callback_data="build_pc"),
            InlineKeyboardButton("🔧 Компоненты", callback_data="components")
        ],
        [InlineKeyboardButton("❓ Помощь", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! 👋\n\n"
        "Я бот-помощник по сборке компьютеров. Я могу помочь тебе выбрать готовую сборку ПК или подобрать отдельные компоненты.\n\n"
        "Что ты хочешь сделать?",
        reply_markup=reply_markup
    )
    
    return SELECTING_MAIN_MENU

async def build_pc(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора сборки ПК"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    update_user_last_active(user_id)
    
    # Получаем типы устройств из БД
    device_types = get_device_types()
    
    # Создаем клавиатуру с типами устройств
    keyboard = []
    for device_type in device_types:
        keyboard.append([
            InlineKeyboardButton(
                device_type["name"], 
                callback_data=f"device_type_{device_type['id']}"
            )
        ])
    
    # Добавляем кнопку возврата
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Выберите тип устройства:",
        reply_markup=reply_markup
    )
    
    return SELECTING_DEVICE_TYPE

async def select_price_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик выбора ценовой категории"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    update_user_last_active(user_id)
    device_type_id = int(query.data.split("_")[-1])
    user_states[user_id] = {"device_type_id": device_type_id}
    price_categories = get_price_categories()
    keyboard = []
    for price_category in price_categories:
        # Форматируем цены с разделителями тысяч
        min_price = "{:,}".format(price_category["min_price"]).replace(",", " ")
        max_price = "{:,}".format(price_category["max_price"]).replace(",", " ")
        
        # Для премиум категории отображаем "от"
        if price_category["id"] == 3:
            price_text = f"{price_category['name']} (от {min_price} ₽)"
        else:
            price_text = f"{price_category['name']} ({min_price} - {max_price} ₽)"
            
        keyboard.append([
            InlineKeyboardButton(
                price_text, 
                callback_data=f"price_category_{price_category['id']}"
            )
        ])
    
    # Добавляем кнопку возврата
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_device")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Выберите ценовую категорию:",
        reply_markup=reply_markup
    )
    
    return SELECTING_PRICE_CATEGORY

async def show_builds(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отображения сборок"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    update_user_last_active(user_id)
    
    # Получаем ID ценовой категории из callback_data
    price_category_id = int(query.data.split("_")[-1])
    
    # Сохраняем выбор пользователя
    user_states[user_id]["price_category_id"] = price_category_id
    
    # Получаем сборки из БД
    device_type_id = user_states[user_id]["device_type_id"]
    builds = get_builds_by_type_and_price(device_type_id, price_category_id)
    
    if not builds:
        # Если сборок нет, показываем сообщение
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_price")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "К сожалению, сборок по заданным параметрам не найдено.",
            reply_markup=reply_markup
        )
    else:
        # Создаем клавиатуру со сборками
        keyboard = []
        for build in builds:
            keyboard.append([
                InlineKeyboardButton(
                    f"{build['name']} - {build['total_price']} руб.", 
                    callback_data=f"build_{build['id']}"
                )
            ])
        
        # Добавляем кнопку возврата
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_price")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "Доступные сборки:",
            reply_markup=reply_markup
        )
    
    return VIEWING_BUILDS

async def show_build_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отображения деталей сборки"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    update_user_last_active(user_id)
    
    # Получаем ID сборки из callback_data
    build_id = int(query.data.split("_")[-1])
    
    # Получаем детали сборки из БД
    build_details = get_build_details(build_id)
    
    if not build_details:
        # Если сборка не найдена, возвращаемся к списку
        await show_builds(update, context)
        return VIEWING_BUILDS
    
    build = build_details["build"]
    components = build_details["components"]
    
    # Формируем текст сообщения
    message_text = f"*{build['name']}*\n\n"
    message_text += f"{build['description']}\n\n"
    message_text += f"*Цена:* {build['total_price']} руб.\n\n"
    message_text += "*Компоненты:*\n"
    
    for component in components:
        message_text += f"- {component['name']} - {component['price']} руб.\n"
    # Создаем клавиатуру
    keyboard = [[InlineKeyboardButton("⬅️ Назад к списку", callback_data="back_to_builds")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Если есть изображение, отправляем его
    if build["image_url"]:
        await query.message.reply_photo(
            photo=build["image_url"],
            caption=message_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        await query.message.delete()
    else:
        await query.edit_message_text(
            text=message_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    return VIEWING_BUILD_DETAILS


async def components_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик меню компонентов"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    update_user_last_active(user_id)
    # Получаем категории компонентов из БД
    component_categories = get_component_categories()
    
    # Создаем клавиатуру с категориями
    keyboard = []
    for category in component_categories:
        keyboard.append([
            InlineKeyboardButton(
                category["name"], 
                callback_data=f"component_category_{category['id']}"
            )
        ])
    
    # Добавляем кнопку возврата
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "Выберите категорию компонентов:",
        reply_markup=reply_markup
    )
    
    return SELECTING_COMPONENT_CATEGORY

async def show_components(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отображения компонентов по категории"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    update_user_last_active(user_id)
    
    # Получаем ID категории из callback_data
    category_id = int(query.data.split("_")[-1])
    # Сохраняем выбор пользователя
    user_states[user_id]["component_category_id"] = category_id
    # компоненты из БД
    components = get_components_by_category(category_id)
    if not components:
        # компонентов нет, сообщение
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_categories")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "К сожалению, компонентов в данной категории не найдено.",
            reply_markup=reply_markup
        )
    else:
        #  клавиатура с компонентами
        keyboard = []
        for component in components:
            keyboard.append([
                InlineKeyboardButton(
                    f"{component['name']} - {component['price']} руб.", 
                    callback_data=f"component_{component['id']}"
                )
            ])
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_categories")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Доступные компоненты:",
            reply_markup=reply_markup
        )    
    return VIEWING_COMPONENTS


async def show_component_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отображения деталей компонента"""
    query = update.callback_query
    await query.answer()
    user_id = update.effective_user.id
    update_user_last_active(user_id)
    component_id = int(query.data.split("_")[-1])
    component = get_component_details(component_id)
    if not component:
        await show_components(update, context)
        return VIEWING_COMPONENTS
    message_text = f"*{component['name']}*\n\n"
    message_text += f"{component['description']}\n\n"
    message_text += f"*Цена:* {component['price']} руб.\n\n"
    if component["specs"]:
        message_text += f"*Характеристики:*\n{component['specs']}\n"
    keyboard = [[InlineKeyboardButton("⬅️ Назад к списку", callback_data="back_to_components")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if component["image_url"]:
        await query.message.reply_photo(
            photo=component["image_url"],
            caption=message_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
        await query.message.delete()
    else:
        await query.edit_message_text(
            text=message_text,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    
    return VIEWING_COMPONENT_DETAILS


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /help или кнопки Помощь"""
    if update.callback_query:
        query = update.callback_query
        await query.answer()
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "🔍 *Справка по использованию бота*\n\n"
            "Этот бот поможет вам выбрать готовую сборку ПК или отдельные компоненты.\n\n"
            "*Основные команды:*\n"
            "/start - Запустить бота и открыть главное меню\n"
            "/help - Показать эту справку\n\n"
            "*Как пользоваться:*\n"
            "1. В главном меню выберите 'Собрать ПК' или 'Компоненты'\n"
            "2. Следуйте инструкциям на экране для выбора нужных параметров\n"
            "3. Просматривайте доступные сборки или отдельные компоненты\n\n"
            "Если у вас возникли вопросы или проблемы, свяжитесь с администратором.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        keyboard = [[InlineKeyboardButton("⬅️ Главное меню", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔍 *Справка по использованию бота*\n\n"
            "Этот бот поможет вам выбрать готовую сборку ПК или отдельные компоненты.\n\n"
            "*Основные команды:*\n"
            "/start - Запустить бота и открыть главное меню\n"
            "/help - Показать эту справку\n\n"
            "*Как пользоваться:*\n"
            "1. В главном меню выберите 'Собрать ПК' или 'Компоненты'\n"
            "2. Следуйте инструкциям на экране для выбора нужных параметров\n"
            "3. Просматривайте доступные сборки или отдельные компоненты\n\n"
            "Если у вас возникли вопросы или проблемы, свяжитесь с администратором.",
            parse_mode="Markdown",
            reply_markup=reply_markup
        )


async def back_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопок возврата"""
    query = update.callback_query
    await query.answer()
    action = query.data
    user_id = update.effective_user.id
    if action == "back_to_main":
        keyboard = [
            [
                InlineKeyboardButton("🖥️ Собрать ПК", callback_data="build_pc"),
                InlineKeyboardButton("🔧 Компоненты", callback_data="components")
            ],
            [InlineKeyboardButton("❓ Помощь", callback_data="help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            "Что вы хотите сделать?",
            reply_markup=reply_markup
        )
        return SELECTING_MAIN_MENU
    elif action == "back_to_device":
        return await build_pc(update, context)
    elif action == "back_to_price":
        if user_id in user_states and "device_type_id" in user_states[user_id]:
            device_type_id = user_states[user_id]["device_type_id"]
            device_types = get_device_types()
            price_categories = get_price_categories()
            keyboard = []
            for price_category in price_categories:
                min_price = "{:,}".format(price_category["min_price"]).replace(",", " ")
                max_price = "{:,}".format(price_category["max_price"]).replace(",", " ")
                if price_category["id"] == 3:
                    price_text = f"{price_category['name']} (от {min_price} ₽)"
                else:
                    price_text = f"{price_category['name']} ({min_price} - {max_price} ₽)"
                keyboard.append([
                    InlineKeyboardButton(
                        price_text, 
                        callback_data=f"price_category_{price_category['id']}"
                    )
                ])
            keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_device")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "Выберите ценовую категорию:",
                reply_markup=reply_markup
            )
            return SELECTING_PRICE_CATEGORY
        else:
            return await build_pc(update, context)
    elif action == "back_to_builds":
        if user_id in user_states and "device_type_id" in user_states[user_id] and "price_category_id" in user_states[user_id]:
            device_type_id = user_states[user_id]["device_type_id"]
            price_category_id = user_states[user_id]["price_category_id"]
            builds = get_builds_by_type_and_price(device_type_id, price_category_id)
            keyboard = []
            for build in builds:
                keyboard.append([
                    InlineKeyboardButton(
                        f"{build['name']} - {build['total_price']} руб.", 
                        callback_data=f"build_{build['id']}"
                    )
                ])
            keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_price")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                "Доступные сборки:",
                reply_markup=reply_markup
            )
            return VIEWING_BUILDS
        else:
            return await build_pc(update, context)
            
    elif action == "back_to_categories":
        # Возврат к категориям компонентов
        return await components_menu(update, context)
        
    elif action == "back_to_components":
        # Возврат к списку компонентов
        if user_id in user_states and "component_category_id" in user_states[user_id]:
            category_id = user_states[user_id]["component_category_id"]
            
            # Получаем компоненты из БД
            components = get_components_by_category(category_id)
            
            keyboard = []
            for component in components:
                keyboard.append([
                    InlineKeyboardButton(
                        f"{component['name']} - {component['price']} руб.", 
                        callback_data=f"component_{component['id']}"
                    )
                ])
            
            keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_categories")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "Доступные компоненты:",
                reply_markup=reply_markup
            )
            return VIEWING_COMPONENTS
        else:
            return await components_menu(update, context)

async def show_random_build(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик отображения случайной сборки"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    update_user_last_active(user_id)
    
    # Получаем ID ценовой категории из callback_data
    price_category_id = int(query.data.split("_")[-1])
    
    # Сохраняем выбор пользователя
    user_states[user_id]["price_category_id"] = price_category_id
    
    # Получаем случайную сборку из БД
    device_type_id = user_states[user_id]["device_type_id"]
    build_details = get_random_build(device_type_id, price_category_id)
    
    if not build_details:
        # Если сборок нет, показываем сообщение
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_price")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "К сожалению, сборок по заданным параметрам не найдено.",
            reply_markup=reply_markup
        )
    else:
        build = build_details["build"]
        components = build_details["components"]
        
        # Формируем текст сообщения
        message_text = f"*{build['name']}*\n\n"
        message_text += f"{build['description']}\n\n"
        message_text += f"*Цена:* {build['total_price']} руб.\n\n"
        message_text += "*Компоненты:*\n"
        
        for component in components:
            message_text += f"- {component['name']} - {component['price']} руб.\n"
        
        # Создаем клавиатуру
        keyboard = [
            [InlineKeyboardButton("🔄 Следующая сборка", callback_data=f"next_build_{price_category_id}")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_price")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Если есть изображение, отправляем его
        if build["image_url"]:
            await query.message.reply_photo(
                photo=build["image_url"],
                caption=message_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            await query.message.delete()
        else:
            await query.edit_message_text(
                text=message_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    
    return VIEWING_BUILDS

async def next_build(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик кнопки 'Следующая сборка'"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    update_user_last_active(user_id)
    
    # Получаем ID ценовой категории из callback_data
    price_category_id = int(query.data.split("_")[-1])
    
    # Получаем случайную сборку из БД
    device_type_id = user_states[user_id]["device_type_id"]
    build_details = get_random_build(device_type_id, price_category_id)
    
    if not build_details:
        # Если сборок нет, показываем сообщение
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_price")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "К сожалению, сборок по заданным параметрам не найдено.",
            reply_markup=reply_markup
        )
    else:
        build = build_details["build"]
        components = build_details["components"]
        
        # Формируем текст сообщения
        message_text = f"*{build['name']}*\n\n"
        message_text += f"{build['description']}\n\n"
        message_text += f"*Цена:* {build['total_price']} руб.\n\n"
        message_text += "*Компоненты:*\n"
        
        for component in components:
            message_text += f"- {component['name']} - {component['price']} руб.\n"
        
        # Создаем клавиатуру
        keyboard = [
            [InlineKeyboardButton("🔄 Следующая сборка", callback_data=f"next_build_{price_category_id}")],
            [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_price")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Если есть изображение, отправляем его
        if build["image_url"]:
            await query.message.reply_photo(
                photo=build["image_url"],
                caption=message_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
            await query.message.delete()
        else:
            await query.edit_message_text(
                text=message_text,
                parse_mode="Markdown",
                reply_markup=reply_markup
            )
    
    return VIEWING_BUILDS

def main():
    """Запуск бота"""
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    
    # Обработчики для кнопок
    application.add_handler(CallbackQueryHandler(build_pc, pattern="^build_pc$"))
    application.add_handler(CallbackQueryHandler(components_menu, pattern="^components$"))
    application.add_handler(CallbackQueryHandler(help_command, pattern="^help$"))
    application.add_handler(CallbackQueryHandler(back_handler, pattern="^back_to"))
    application.add_handler(CallbackQueryHandler(select_price_category, pattern="^device_type_"))
    application.add_handler(CallbackQueryHandler(show_random_build, pattern="^price_category_"))
    application.add_handler(CallbackQueryHandler(next_build, pattern="^next_build_"))
    application.add_handler(CallbackQueryHandler(show_components, pattern="^component_category_"))
    application.add_handler(CallbackQueryHandler(show_component_details, pattern="^component_"))
    
    # Запускаем бота
    application.run_polling()

    
if __name__ == "__main__":
    main()








