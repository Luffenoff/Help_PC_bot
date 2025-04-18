import logging
import os
from dotenv import load_dotenv
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, CallbackQuery
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from database import get_db_connection, update_user_last_active, get_device_types, get_price_categories, get_component_categories
from database import get_builds_by_type_and_price, get_build_details, get_components_by_category, get_component_details
import json

# Загружаем переменные окружения
load_dotenv()

# Состояния для ConversationHandler
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
    
    # Получаем ID типа устройства из callback_data
    device_type_id = int(query.data.split("_")[-1])
    
    # Сохраняем выбор пользователя
    user_states[user_id]["device_type_id"] = device_type_id
    
    # Получаем ценовые категории из БД
    price_categories = get_price_categories()
    
    # Создаем клавиатуру с ценовыми категориями и отображаем диапазон цен
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
    """Обработчик отображения случайной сборки по типу и цене"""
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
        # Выбираем случайную сборку
        import random
        build = random.choice(builds)
        
        # Получаем детали сборки
        build_details = get_build_details(build['id'])
        
        # Формируем сообщение
        message = f"🎮 {build['name']}\n\n"
        message += f"💰 Цена: {build['total_price']} руб.\n\n"
        message += f"📝 Описание: {build['description']}\n\n"
        
        # Добавляем ссылку на сборку, если она есть
        if build.get('link'):
            message += f"🔗 Ссылка на сборку: {build['link']}\n\n"
        
        if build_details and build_details.get('components'):
            message += "Компоненты:\n"
            for component in build_details['components']:
                message += f"• {component.get('name', '')} - {component.get('price', 0)} руб.\n"
                if component.get('specs'):
                    try:
                        specs = json.loads(component['specs'])
                        for spec_name, spec_value in specs.items():
                            message += f"  - {spec_name}: {spec_value}\n"
                    except:
                        pass
        
        # Создаем клавиатуру с кнопками навигации
        keyboard = [
            [
                InlineKeyboardButton("⬅️ Назад", callback_data="back_to_price"),
                InlineKeyboardButton("➡️ Следующая", callback_data=f"next_build_{price_category_id}")
            ]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            message,
            reply_markup=reply_markup
        )
    
    return VIEWING_BUILDS

async def next_build(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик переключения на следующую сборку"""
    query = update.callback_query
    await query.answer()
    
    # Получаем ID ценовой категории из callback_data
    price_category_id = int(query.data.split("_")[-1])
    
    # Создаем новый объект Update с обновленным callback_data
    new_update = Update(
        update.update_id,
        message=update.message,
        edited_message=update.edited_message,
        channel_post=update.channel_post,
        edited_channel_post=update.edited_channel_post,
        inline_query=update.inline_query,
        chosen_inline_result=update.chosen_inline_result,
        callback_query=CallbackQuery(
            id=query.id,
            from_user=query.from_user,
            chat_instance=query.chat_instance,
            message=query.message,
            data=f"price_{price_category_id}"
        ),
        shipping_query=update.shipping_query,
        pre_checkout_query=update.pre_checkout_query,
        poll=update.poll,
        poll_answer=update.poll_answer,
        my_chat_member=update.my_chat_member,
        chat_member=update.chat_member,
        chat_join_request=update.chat_join_request
    )
    
    # Вызываем show_builds с новым объектом Update
    return await show_builds(new_update, context)

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
    
    # Получаем компоненты из БД
    components = get_components_by_category(category_id)
    
    if not components:
        # Если компонентов нет, показываем сообщение
        keyboard = [[InlineKeyboardButton("⬅️ Назад", callback_data="back_to_categories")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "К сожалению, компонентов в данной категории не найдено.",
            reply_markup=reply_markup
        )
    else:
        # Создаем клавиатуру с компонентами
        keyboard = []
        for component in components:
            keyboard.append([
                InlineKeyboardButton(
                    f"{component['name']} - {component['price']} руб.", 
                    callback_data=f"component_{component['id']}"
                )
            ])
        
        # Добавляем кнопку возврата
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
    
    # Получаем ID компонента из callback_data
    component_id = int(query.data.split("_")[-1])
    
    # Получаем детали компонента из БД
    component = get_component_details(component_id)
    
    if not component:
        # Если компонент не найден, возвращаемся к списку
        await show_components(update, context)
        return VIEWING_COMPONENTS
    
    # Формируем текст сообщения
    message_text = f"*{component['name']}*\n\n"
    message_text += f"{component['description']}\n\n"
    message_text += f"*Цена:* {component['price']} руб.\n\n"
    
    if component["specs"]:
        message_text += f"*Характеристики:*\n{component['specs']}\n"
    
    # Создаем клавиатуру
    keyboard = [[InlineKeyboardButton("⬅️ Назад к списку", callback_data="back_to_components")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Если есть изображение, отправляем его
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
        # Возврат к выбору ценовой категории
        if user_id in user_states and "device_type_id" in user_states[user_id]:
            device_type_id = user_states[user_id]["device_type_id"]
            
            # Получаем типы устройств из БД
            device_types = get_device_types()
            
            # Создаем клавиатуру с ценовыми категориями
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
        # Возврат к списку сборок
        if user_id in user_states and "device_type_id" in user_states[user_id] and "price_category_id" in user_states[user_id]:
            device_type_id = user_states[user_id]["device_type_id"]
            price_category_id = user_states[user_id]["price_category_id"]
            
            # Получаем сборки из БД
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

def main():
    """Основная функция запуска бота"""
    application = ApplicationBuilder().token(TOKEN).build()
    
    # Создаем обработчик диалога
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_MAIN_MENU: [
                CallbackQueryHandler(build_pc, pattern="^build_pc$"),
                CallbackQueryHandler(components_menu, pattern="^components$"),
                CallbackQueryHandler(help_command, pattern="^help$")
            ],
            SELECTING_DEVICE_TYPE: [
                CallbackQueryHandler(select_price_category, pattern="^device_"),
                CallbackQueryHandler(back_handler, pattern="^back_to_main$")
            ],
            SELECTING_PRICE_CATEGORY: [
                CallbackQueryHandler(show_builds, pattern="^price_"),
                CallbackQueryHandler(back_handler, pattern="^back_to_device$")
            ],
            VIEWING_BUILDS: [
                CallbackQueryHandler(next_build, pattern="^next_build_"),
                CallbackQueryHandler(back_handler, pattern="^back_to_price$")
            ],
            SELECTING_COMPONENT_CATEGORY: [
                CallbackQueryHandler(show_components, pattern="^category_"),
                CallbackQueryHandler(back_handler, pattern="^back_to_main$")
            ],
            VIEWING_COMPONENTS: [
                CallbackQueryHandler(show_component_details, pattern="^component_"),
                CallbackQueryHandler(back_handler, pattern="^back_to_categories$")
            ],
            VIEWING_COMPONENT_DETAILS: [
                CallbackQueryHandler(back_handler, pattern="^back_to_components$")
            ]
        },
        fallbacks=[CommandHandler("start", start)]
    )
    
    # Добавляем обработчик в приложение
    application.add_handler(conv_handler)
    
    # Запускаем бота
    application.run_polling()

    
if __name__ == "__main__":
    main()








