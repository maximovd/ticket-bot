import os
import sys
import logging
from threading import Thread

from dotenv import load_dotenv
from telegram import (
    ReplyKeyboardMarkup,
    ParseMode,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
    CallbackContext,
)
from telegram.update import Update

from utils.handlers import create_deal

logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log',
)

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

PROXY = {
    'proxy_url': os.environ.get('proxy_url'),
    'urllib3_proxy_kwargs': {
        'username': os.environ.get('username'),
        'password': os.environ.get('password'),
    },
}
CANCEL = ReplyKeyboardMarkup([['❌Отмена']], resize_keyboard=True)
START = ReplyKeyboardMarkup([['Начать']], resize_keyboard=True)


def greet_user(update: Update, context: CallbackContext) -> None:
    create_ticket = ReplyKeyboardMarkup(
        [['Создать заявку📋']],
        resize_keyboard=True,
    )
    update.message.reply_text(
        text='Привет, я бот для приема заявок.'
        'Нажми *Создать заявку*.'
        'Если по какой-то причине у тебя не'
        'получается создать новую заявку,'
        'воспользуйся [формой]'
        '(https://bitrix24public.com/'
        'prosushilife.bitrix24.ru/form/'
        '31_forma_podachi_zayavki_v_it_otdel/'
        'bsaoua/)',
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=create_ticket,
        )


def start_ticket(update: Update, context: CallbackContext) -> str:
    update.message.reply_text(
        'Пожалуйста введите ваше Имя и Фамилию.',
        reply_markup=CANCEL,
    )
    return 'name'


def ticket_get_name(update: Update, context: CallbackContext) -> str:
    user_full_name = update.message.text
    if len(user_full_name.split(' ')) != 2:
        update.message.reply_text(
            'Введите Имя и Фамилию через пробел.',
            reply_markup=CANCEL,
        )
        return 'name'
    else:
        context.user_data['full_name'] = user_full_name
        chat_id = update.message.chat_id
        context.bot.send_message(
            chat_id=chat_id,
            text='Введите номер своего подразделения:\n'
                 '1. Колл-Центр\n'
                 '2. Офис\n'
                 '3. Офис(Одесская)\n'
                 '4. Игнатова\n'
                 '5. Казбекская\n'
                 '6. Котлярова\n'
                 '7. Красная\n'
                 '8. Красная площадь\n'
                 '9. Лофт\n'
                 '10. Мега\n'
                 '11. Новороссийск Молодежная\n'
                 '12. Новроссийск Серебрякова\n'
                 '13. Покрышкина\n'
                 '14. СБС\n'
                 '15. Ставропольская\n'
                 '16. Туапсе\n'
                 '17. Тюляева\n'
                 '18. Чекистов\n'
                 '19. Российская\n',
                 '20. Сочи\n',
            reply_markup=CANCEL,
        )
        return 'department'


def ticket_department(update: Update, context: CallbackContext):
    answer = int(update.message.text)
    category_id = 0
    department_id = {
        1: 1449,
        2: 1451,
        3: 1453,
        4: 1455,
        5: 1457,
        6: 1459,
        7: 1461,
        8: 1463,
        9: 1465,
        10: 1467,
        11: 1469,
        12: 1471,
        13: 1473,
        14: 1475,
        15: 1477,
        16: 1479,
        17: 1481,
        18: 1483,
        19: 1485,
        20: 1487,
    }
    for key in department_id.keys():
        if key == answer:
            category_id = department_id[key]

    if category_id == 0:
        update.message.reply_text(
            'Нет такого подразделения, повторите ввод:',
            reply_markup=CANCEL,
        )
        return 'department'

    context.user_data['department'] = category_id
    update.message.reply_text(
        'Коротко опишите суть своей проблемы:',
        reply_markup=CANCEL,
    )
    return 'trouble_description'


def ticket_description(update: Update, context: CallbackContext):
    context.user_data['description'] = update.message.text
    update.message.reply_text('Номер телефона для связи:', reply_markup=CANCEL)
    return 'phone_number'


def ticket_phone_number(update: Update, context: CallbackContext):
    context.user_data['phone_number'] = update.message.text
    update.message.reply_text('Почта для связи:', reply_markup=CANCEL)
    return 'email'


def ticket_email(update: Update, context: CallbackContext):
    context.user_data['email'] = update.message.text
    keyboard = [['✅Да', '❌Нет']]
    markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    user_text = '''
    *Отправить заявку?*
    Имя и Фамилия: *{full_name}*\n
    Краткое описание проблемы:\n *{description}*\n
    Номер телефона для связи: *{phone_number}*\n
    Почта для связи: *{email}*\n
    Если все верно, нажмите *Да*, для отмены нажмите *Нет*
    '''.format(**context.user_data)
    update.message.reply_text(
        text=user_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=markup,
    )
    return 'confirmation'


def ticket_confirmation(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer == '❌Нет':
        update.message.reply_text(
            'Отмена...',
            reply_markup=ReplyKeyboardRemove(),
             )
        context.user_data.clear()
        return ConversationHandler.END
    elif answer == '✅Да':
        create_deal(user_data=context.user_data)
        update.message.reply_text(
            'Спасибо, ваша заявка передана ИТ отделу.\n'
            'В ближайшее время с вами свяжутся.',
            reply_markup=ReplyKeyboardRemove(),
        )
        context.user_data.clear()
        return ConversationHandler.END


def cancel(update: Update, context: CallbackContext):
    update.message.reply_text('Отмена...', reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()
    return ConversationHandler.END


def failure(update: Update, context: CallbackContext):
    update.message.reply_text('Ошибка, повторите ввод:')


def main():
    ticketbot = Updater(
        os.environ.get('TELEGRAM_TOKEN'),
        request_kwargs=PROXY,
        use_context=True,
    )
    dp = ticketbot.dispatcher

    logging.info('Бот запускается')

    def stop_restart() -> None:
        """Остановка процесса бота."""
        ticketbot.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update, context: CallbackContext) -> None:
        """Перезапуск бота."""
        Thread(target=stop_restart).start()
        update.message.reply_text('Успешно')

    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('restart', restart))

    ticket = ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex('^(Создать заявку📋)$'),
            start_ticket,
            pass_user_data=True,
        )],
        states={
            'name': [
                MessageHandler(
                    Filters.regex('^(❌Отмена)$'),
                    cancel,
                    pass_user_data=True,
                ),
                MessageHandler(
                    Filters.text,
                    ticket_get_name,
                    pass_user_data=True,
                ),
            ],
            'department': [
                MessageHandler(
                    Filters.regex('^(❌Отмена)$'),
                    cancel,
                    pass_user_data=True,
                ),
                MessageHandler(
                    Filters.text,
                    ticket_department,
                    pass_user_data=True,
                ),
            ],
            'trouble_description': [
                MessageHandler(
                    Filters.regex('^(❌Отмена)$'),
                    cancel,
                    pass_user_data=True,
                ),
                MessageHandler(
                    Filters.text,
                    ticket_description,
                    pass_user_data=True,
                ),
            ],
            'phone_number': [
                MessageHandler(
                    Filters.regex('^(❌Отмена)$'),
                    cancel,
                    pass_user_data=True,
                ),
                MessageHandler(
                    Filters.regex(r'^((\+7|7|8)+([0-9]){10})$'),
                    ticket_phone_number,
                    pass_user_data=True,
                ),
            ],
            'email': [
                MessageHandler(
                    Filters.regex('^(❌Отмена)$'),
                    cancel,
                    pass_user_data=True,
                ),
                MessageHandler(
                    Filters.regex(r'^[a-z0-9]+[\._]?'
                                  r'[a-z0-9]+[@]\w+[.]\w{2,3}$'),
                    ticket_email,
                    pass_user_data=True,
                ),
            ],
            'confirmation': [
                MessageHandler(
                    Filters.regex('^(✅Да|❌Нет)$'),
                    ticket_confirmation,
                    pass_user_data=True,
                ),
            ],
        },
        fallbacks=[MessageHandler(
            Filters.text | Filters.video | Filters.photo | Filters.document,
            failure,
            pass_user_data=True,
        )],
    )
    dp.add_handler(ticket)

    ticketbot.start_polling()
    ticketbot.idle()


if __name__ == '__main__':
    main()
