from telegram import Update
from telegram.ext import ContextTypes
from database import get_user, get_user_balance, update_user_activity

async def show_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = get_user(user_id)
    update_user_activity(user_id)  # Фиксируем активность
    
    profile_text = (
        f"👤 *{user['full_name']}*\n"
        f"🎯 Роль: {'Ученик' if user['role'] == 'student' else 'Преподаватель'}\n"
        f"🏫 Класс/Школа: {user.get('class', user.get('school', 'не указано'))}\n"
        f"💰 Баланс: *{user['balance']} EdGram*\n"
        f"📅 Последняя активность: {user.get('last_active', 'сегодня')}"
    )
    
    await update.message.reply_text(profile_text, parse_mode='Markdown')

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = get_user_balance(user_id)
    await update.message.reply_text(f"Ваш баланс: *{balance} EdGram*", parse_mode='Markdown')
