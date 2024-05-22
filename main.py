import logging
import random
import string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler, CallbackContext, ConversationHandler

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = '6962023272:AAEu1paHmy9zKLfnz_xlc0tw-2wGmGcaXFo'
ADMIN_CHAT_ID = '6681527041'
PRICE_PER_KEY = 800

(START, BUY_CRYPTO, BUY_CARD, ENTER_AMOUNT, SELECT_CRYPTO, CONFIRM_PAYMENT, PAYMENT_CARD) = range(7)

CRYPTO_ADDRESSES = {
    'usdt': 'TYzuuiZFkGD1dR7yU4bkXmUWf8YvXnXwaZ',
    'eth': '0x8c8c35277ec7b263cDF68416816573D38A300069',
    'btc': 'bc1q5vzhwm73yenskzwvr00fy2yxmsdp9jz46jquhv',
    'ton': 'UQB7uKlzJScb0QMz4ofIY0Q3cZfKnh3af17oJ2o9OZQ2gd0A'
}

def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("О проекте", callback_data='about')],
        [InlineKeyboardButton("Купить ключи за крипту", callback_data='buy_crypto')],
        [InlineKeyboardButton("Купить ключи переводом по карте", callback_data='buy_card')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.message:
        update.message.reply_text('Добро пожаловать в KeyTime - командa профессионалов в сфере p2e ключей! Мы рады представить вам безопасные и прибыльные решения для вашего финансового опыта. Выберите действие:', reply_markup=reply_markup)
    elif update.callback_query:
        update.callback_query.message.edit_text('Добро пожаловать! Выберите действие:', reply_markup=reply_markup)
    return START

def button(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    if query.data == 'about':
        about = """
        Наш проект, посвященный p2e ключам, уверенно работает уже третий год на динамичном рынке. За это время мы зарекомендовали себя как надежного и стабильного партнера, выплатив нашим участникам впечатляющую сумму свыше 1 500 000 долларов.

        Благодаря нашему опыту и профессионализму мы предлагаем уникальные возможности для заработка с помощью p2e ключей. Мы гордимся достигнутыми результатами и стремимся к дальнейшему росту, постоянно совершенствуя наши услуги и расширяя горизонты для наших клиентов.

        Доверьтесь экспертам в области p2e ключей и откройте для себя новые перспективы финансового успеха.
        """
        keyboard = [[InlineKeyboardButton("Назад", callback_data='start')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(about, reply_markup=reply_markup)

    elif query.data == 'buy_crypto':
        context.user_data['payment_method'] = 'crypto'
        query.edit_message_text('Сколько хотите купить? (До 100 ключей)')
        return BUY_CRYPTO

    elif query.data == 'buy_card':
        context.user_data['payment_method'] = 'card'
        query.edit_message_text('Сколько хотите купить? (До 100 ключей)')
        return BUY_CARD

    elif query.data == 'start' or query.data == 'return_to_start':
        return start(update, context)

    elif query.data == 'confirm_payment':
        user_id = query.from_user.id
        username = query.from_user.username
        amount = context.user_data["amount"]
        context.bot_data[user_id] = {
            "amount": amount,
            "username": username
        }
        query.edit_message_text('Заявка создана, ожидайте.')
        context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f'Создана заявка от @{username} на покупку в размере {amount * PRICE_PER_KEY} рублей.',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("✅ Подтвердить", callback_data=f'approve_{user_id}')],
                [InlineKeyboardButton("❌ Отклонить", callback_data=f'decline_{user_id}')]
            ])
        )
        return ConversationHandler.END

    elif query.data == 'change_amount':
        query.edit_message_text('Сколько хотите купить? (До 100 ключей)')
        return ENTER_AMOUNT

    elif query.data == 'change_payment_method':
        return select_crypto(update, context)

    elif query.data == 'mark_as_paid':
        return handle_card_payment(update, context)


def crypto_selection(update: Update, context: CallbackContext) -> int:
    query = update.callback_query
    query.answer()

    amount = context.user_data.get('amount')
    if query.data in CRYPTO_ADDRESSES:
        crypto_address = CRYPTO_ADDRESSES[query.data]
        keyboard = [
            [InlineKeyboardButton("Я оплатил", callback_data='confirm_payment')],
            [InlineKeyboardButton("Изменить метод оплаты", callback_data='change_payment_method')],
            [InlineKeyboardButton("Изменить количество", callback_data='change_amount')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        query.edit_message_text(
            f'Переведите {amount * PRICE_PER_KEY} рублей на указанный адрес: `{crypto_address}`. Нажмите "Я оплатил" после перевода.',
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        return CONFIRM_PAYMENT

    elif query.data == 'select_crypto':
        return select_crypto(update, context)

def select_crypto(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [InlineKeyboardButton("USDT", callback_data='usdt')],
        [InlineKeyboardButton("BTC", callback_data='btc')],
        [InlineKeyboardButton("ETH", callback_data='eth')],
        [InlineKeyboardButton("TON", callback_data='ton')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        update.callback_query.message.edit_text('Выберите криптовалюту для оплаты:', reply_markup=reply_markup)
    else:
        update.message.reply_text('Выберите криптовалюту для оплаты:', reply_markup=reply_markup)
    return SELECT_CRYPTO

def amount_handler(update: Update, context: CallbackContext) -> int:
    try:
        amount = int(update.message.text)
        if 1 <= amount <= 100:
            context.user_data['amount'] = amount
            context.user_data['user_id'] = update.message.from_user.id
            context.user_data['username'] = update.message.from_user.username

            if context.user_data.get('payment_method') == 'card':
                return handle_card_payment(update, context)
            else:
                return select_crypto(update, context)
        else:
            update.message.reply_text('Введите целое число от 1 до 100.')
    except ValueError:
        update.message.reply_text('Введите целое число от 1 до 100.')
    return ENTER_AMOUNT

def handle_card_payment(update: Update, context: CallbackContext) -> int:
    amount = context.user_data['amount']
    keyboard = [
        [InlineKeyboardButton("Я оплатил", callback_data='confirm_payment')],
        [InlineKeyboardButton("Изменить количество", callback_data='change_amount')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(
        f'Переведите {amount * PRICE_PER_KEY} рублей на номер карты: (Уточнять в лс @Chraaack). Нажмите "Я оплатил" после перевода.',
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return PAYMENT_CARD


def generate_keys(amount):
    keys = []
    for _ in range(amount):
        key = ''.join(random.choices(string.ascii_uppercase, k=5)) + ':' + str(random.randint(0, 9)) + ''.join(random.choices(string.ascii_lowercase, k=7))
        keys.append(key)
    return '\n'.join(keys)

def admin_button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    data = query.data.split('_')
    action = data[0]
    user_id = int(data[1])

    # Получаем информацию о заявке из context.bot_data
    user_data = context.bot_data.get(user_id)
    if not user_data:
        query.edit_message_text('Ошибка: не удалось найти данные о заявке.')
        return

    user_nickname = user_data["username"]
    amount = user_data["amount"]

    if action == 'approve':
        keys = generate_keys(amount)
        context.bot.send_message(
            chat_id=user_id, 
            text=f'Ваша заявка подтверждена.\nСпасибо за покупку p2e ключей!\nВаша поддержка бесценна.\nВот ваши ключи:\n{keys}'
        )
        query.edit_message_text(f'Заявка от @{user_nickname} подтверждена. Ключи отправлены.')

    elif action == 'decline':
        context.bot.send_message(
            chat_id=user_id, 
            text='Ваша заявка отклонена.\nВы можете перезапустить бота или связаться с техподдержкой.',
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Тех поддержка", url='https://t.me/Chraaack')]
            ])
        )
        query.edit_message_text(f'Заявка от @{user_nickname} отклонена.')


def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            START: [CallbackQueryHandler(button)],
            BUY_CRYPTO: [MessageHandler(Filters.text & ~Filters.command, amount_handler)],
            BUY_CARD: [MessageHandler(Filters.text & ~Filters.command, amount_handler)],
            ENTER_AMOUNT: [MessageHandler(Filters.text & ~Filters.command, amount_handler)],
            SELECT_CRYPTO: [CallbackQueryHandler(crypto_selection)],
            CONFIRM_PAYMENT: [CallbackQueryHandler(button, pattern='^confirm_payment$|^change_amount$|^change_payment_method$')],
            PAYMENT_CARD: [CallbackQueryHandler(button, pattern='^confirm_payment$|^change_amount$|^mark_as_paid$')],
        },
        fallbacks=[CommandHandler('start', start)],
    )

    dp.add_handler(conv_handler)
    dp.add_handler(CallbackQueryHandler(admin_button, pattern='^(approve|decline)_'))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
