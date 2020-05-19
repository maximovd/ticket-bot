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


def greet_user(update: Update, context: CallbackContext) -> None:
    # chat_id = update.effective_chat.id
    create_ticket = ReplyKeyboardMarkup(
        [['Создать заявку']],
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
        reply_markup=ReplyKeyboardRemove(),
    )
    return 'name'


def ticket_get_name(update: Update, context: CallbackContext) -> str:
    user_full_name = update.message.text
    if len(user_full_name.split(' ')) != 2:
        update.message.reply_text('Введите Имя и Фамилию через пробел.',)
        return 'name'
    else:
        context.user_data['full_name'] = user_full_name
        chat_id = update.message.chat_id
        context.bot.send_message(
            chat_id=chat_id,
            text='Введите номер своего подразделения:\n'
                 '1. Офис\n'
                 '2. Офис(Одесская)\n'
                 '3. Игнатова\n'
                 '4. Казбекская\n'
                 '5. Котлярова\n'
                 '6. Красная\n'
                 '7. Красная площадь\n'
                 '8. Лофт\n'
                 '9. Мега\n'
                 '10. Новороссийск Молодежная\n'
                 '11. Новроссийск Серебрякова\n'
                 '12. Покрышкина\n'
                 '13. СБС\n'
                 '14. Ставропольская\n'
                 '15. Туапсе\n'
                 '16. Тюляева\n'
                 '17. Чекистов\n'
                 '18. Российская\n',
        )
        return 'department'


def ticket_department(update: Update, context: CallbackContext):
    answer = int(update.message.text)
    category_id = 0
    department_id = {
        1: 1449,
        2: 3445,
        3: 3456,
        4: 2345,
        5: 4564,
        6: 4353,
        7: 4123,
        8: 7989,
        9: 4534,
        10: 4534,
        11: 6685,
        12: 7788,
        13: 8643,
        14: 4233,
        15: 5675,
        16: 3423,
        17: 4356,
        18: 3423,
    }
    for key in department_id.keys():
        if key == answer:
            category_id = department_id[key]

    if category_id == 0:
        update.message.reply_text(
            'Номер подразделения неверный, повторите ввод',
        )
        return 'department'

    context.user_data['department'] = category_id
    update.message.reply_text('Коротко опишите суть своей проблемы:')
    return 'trouble_description'


def ticket_description(update: Update, context: CallbackContext):
    context.user_data['description'] = update.message.text
    update.message.reply_text('Номер телефона для связи:')
    return 'phone_number'


def ticket_phone_number(update: Update, context: CallbackContext):
    context.user_data['phone_number'] = update.message.text
    update.message.reply_text('Почта для связи:')
    return 'mail'


def ticket_mail(update: Update, context: CallbackContext):
    context.user_data['mail'] = update.message.text
    keyboard = [['Да', 'Нет']]
    markup = ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
    )
    user_text = '''
    *Отправить заявку?*
    Имя и Фамилия: *{full_name}*\n
    Краткое описание проблемы: *{description}*\n
    Номер телефона для связи: *{phone_number}*\n
    Почта для связи: *{mail}*\n
    Если все верно, введите *Да*, для введите *Нет*
    '''.format(**context.user_data)
    update.message.reply_text(
        text=user_text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=markup,
    )
    return 'confirmation'


def ticket_confirmation(update: Update, context: CallbackContext):
    answer = update.message.text
    if answer == 'Нет':
        update.message.reply_text('Отмена...')
        return ConversationHandler.END
    update.message.reply_text(
        'Спасибо, ваша заявка передана ИТ отделу.\n'
        'В ближайшее время с вами свяжутся.',
    )
    return ConversationHandler.END


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
            Filters.regex('^(Создать заявку)$'),
            start_ticket,
            pass_user_data=True,
        )],
        states={
            'name': [MessageHandler(
                Filters.text,
                ticket_get_name,
                pass_user_data=True,
            )],
            'department': [MessageHandler(
                Filters.text,
                ticket_department,
                pass_user_data=True,
            )],
            'trouble_description': [MessageHandler(
                Filters.text,
                ticket_description,
                pass_user_data=True,
            )],
            'phone_number': [MessageHandler(
                Filters.regex(r'^((\+7|7|8)+([0-9]){10})$'),
                ticket_phone_number,
                pass_user_data=True,
            )],
            'mail': [MessageHandler(
                Filters.text,
                ticket_mail,
                pass_user_data=True,
            )],
            'confirmation': [MessageHandler(
                Filters.regex('^(Да|Нет)$'),
                ticket_confirmation,
                pass_user_data=True,
            )],

        },
        fallbacks=[],
    )
    dp.add_handler(ticket)

    ticketbot.start_polling()
    ticketbot.idle()


if __name__ == '__main__':
    main()
