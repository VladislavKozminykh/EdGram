from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from database import get_product, update_balance

async def show_product(update: Update, context: ContextTypes.DEFAULT_TYPE):
    product_id = int(context.args[0])
    product = get_product(product_id)
    
    keyboard = [
        [InlineKeyboardButton(f"Купить за {product['price']} EdGram", 
         callback_data=f"buy_{product_id}")]
    ]
    
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"🎁 *{product['name']}*\n\n{product['description']}",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_purchase(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    product_id = int(query.data.split('_')[1])
    user_id = query.from_user.id
    product = get_product(product_id)
    
    # Проверяем баланс
    if get_user(user_id)['balance'] >= product['price']:
        update_balance(user_id, -product['price'], 'purchase', product_id)
        await query.answer(f"Вы купили {product['name']}!")
        await query.message.reply_text("Товар доставлен! Проверьте личные сообщения.")
    else:
        await query.answer("Недостаточно средств!", show_alert=True)
