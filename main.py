from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import sqlite3
import logging
from datetime import datetime

# Настройки
TOKEN = "7995509628:AAHyV-i2lb32PBfyBU0X6o1UK0kVonxQyrI"  # Замените на реальный!
DB_NAME = "edgram.db"
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Инициализация базы данных"""
    with sqlite3.connect(DB_NAME) as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            full_name TEXT,
            balance INTEGER DEFAULT 100,
            registered_at TEXT
        )""")
        
        conn.execute("""
        CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            price INTEGER,
            emoji TEXT
        )""")
        
        # Тестовые товары
        conn.execute("DELETE FROM products")
        conn.executemany(
            "INSERT INTO products (name, price, emoji) VALUES (?, ?, ?)",
            [("Учебник", 50, "📚"), ("Курс", 100, "🎥"), ("Конспект", 30, "📝")]
        )
        conn.commit()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    user = update.effective_user
    with sqlite3.connect(DB_NAME) as conn:
        if not conn.execute("SELECT 1 FROM users WHERE user_id = ?", (user.id,)).fetchone():
            keyboard = [[InlineKeyboardButton("✅ Принять условия", callback_data="accept_terms")]]
            await update.message.reply_text(
                "📜 *Пользовательское соглашение*\n\n"
                "1. Использование только для обучения\n"
                "2. Соблюдение правил платформы\n\n"
                "Нажмите кнопку ниже для подтверждения:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode="Markdown"
            )
        else:
            await show_main_menu(update)

async def handle_callbacks(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик всех callback-кнопок"""
    query = update.callback_query
    await query.answer()  # Важно для работы кнопок!
    
    if query.data == "accept_terms":
        user = query.from_user
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute(
                "INSERT INTO users (user_id, username, full_name, registered_at) "
                "VALUES (?, ?, ?, ?)",
                (user.id, user.username, user.full_name, datetime.now().isoformat())
            )
            conn.commit()
        
        await query.edit_message_text("🎉 *Регистрация завершена!*\nВам начислено 100 EdGram", parse_mode="Markdown")
        await show_main_menu(update)
    
    elif query.data == "menu_shop":
        await show_shop(update)
    
    elif query.data == "menu_balance":
        await show_balance(update)
    
    elif query.data.startswith("buy_"):
        await handle_purchase(update)

async def show_main_menu(update: Update):
    """Главное меню после регистрации"""
    keyboard = [
        [InlineKeyboardButton("🛍️ Магазин", callback_data="menu_shop")],
        [InlineKeyboardButton("💰 Баланс", callback_data="menu_balance")]
    ]
    if hasattr(update, 'callback_query'):
        await update.callback_query.message.reply_text(
            "Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text(
            "Главное меню:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

async def show_shop(update: Update):
    """Показываем магазин"""
    with sqlite3.connect(DB_NAME) as conn:
        products = conn.execute("SELECT * FROM products").fetchall()
    
    keyboard = [
        [InlineKeyboardButton(f"{p[3]} {p[1]} - {p[2]} EdGram", callback_data=f"buy_{p[0]}")]
        for p in products
    ]
    
    await update.callback_query.message.reply_text(
        "🛍️ *Магазин EdGram*",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def handle_purchase(update: Update):
    """Обработка покупки"""
    query = update.callback_query
    product_id = query.data.split("_")[1]
    
    with sqlite3.connect(DB_NAME) as conn:
        product = conn.execute(
            "SELECT name, price FROM products WHERE product_id = ?", 
            (product_id,)
        ).fetchone()
        
        balance = conn.execute(
            "SELECT balance FROM users WHERE user_id = ?", 
            (query.from_user.id,)
        ).fetchone()[0]
        
        if balance >= product[1]:
            conn.execute(
                "UPDATE users SET balance = balance - ? WHERE user_id = ?",
                (product[1], query.from_user.id)
            )
            conn.commit()
            await query.answer(f"🎉 Куплено: {product[0]}!")
            await query.message.reply_text(
                f"✅ Вы купили *{product[0]}* за {product[1]} EdGram\n"
                f"Остаток: *{balance - product[1]} EdGram*",
                parse_mode="Markdown"
            )
        else:
            await query.answer("❌ Недостаточно средств!", show_alert=True)

async def show_balance(update: Update):
    """Показываем баланс"""
    user_id = update.callback_query.from_user.id
    with sqlite3.connect(DB_NAME) as conn:
        balance = conn.execute(
            "SELECT balance FROM users WHERE user_id = ?", 
            (user_id,)
        ).fetchone()[0]
    
    await update.callback_query.message.reply_text(
        f"💰 *Ваш баланс:* {balance} EdGram",
        parse_mode="Markdown"
    )

def main():
    init_db()
    
    app = Application.builder().token(TOKEN).build()
    
    # Обработчики
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callbacks))
    
    logger.info("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
