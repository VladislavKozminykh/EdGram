from telegram import Update
from telegram.ext import ContextTypes
from database import add_task, get_user

async def add_task_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Добавление новой задачи (для преподавателей)"""
    user = get_user(update.effective_user.id)
    
    if user['role'] != 'teacher':
        await update.message.reply_text("❌ Только преподаватели могут добавлять задачи!")
        return

    try:
        # Формат: /add_task <предмет> <класс> <описание> <ответ> <награда>
        _, subject, class_, description, answer, reward = context.args
        task_id = add_task({
            'author_id': user['user_id'],
            'subject': subject,
            'class': class_,
            'description': description,
            'answer': answer,
            'reward': int(reward)
        })
        await update.message.reply_text(f"✅ Задача #{task_id} добавлена!")
    except Exception as e:
        await update.message.reply_text("❌ Ошибка. Формат: /add_task <предмет> <класс> <описание> <ответ> <награда>")

async def submit_task_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправка решения задачи (для учеников)"""
    await update.message.reply_text("Функция в разработке...")
