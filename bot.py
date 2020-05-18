import os
import sys
import logging
from threading import Thread

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ParseMode, ReplyKeyboardRemove
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
    RegexHandler,
    CallbackContext,
)

from utils.handlers import Department


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


def greet_user(update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    create_ticket = ReplyKeyboardMarkup(
        [['Создать заявку']],
        one_time_keyboard=True,
        resize_keyboard=True,
    )
    context.bot.send_message(chat_id=chat_id,
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


def start_ticket(update, context: CallbackContext) -> str:
    update.message.reply_text(
        'Пожалуйста введите ваше Имя и Фамилию.',
        reply_makrup=ReplyKeyboardRemove(),
    )
    return 'name'


def ticket_get_name(update, context: CallbackContext) -> str:
    user_full_name = update.message.text
    if len(user_full_name.split(' ')) != 2:
        update.message.reply_text('Пожалуйста введите имя и фамилию')
        return 'name'
    else:
        context.user_data['tiket_name'] = user_full_name
        print(Department.get_all())
        department_choice = [Department.get_all()]
        update.message.reply_text(
            'Выберите свой подразделение',
            reply_keyboard=ReplyKeyboardMarkup(
                keyboard=department_choice,
                one_time_keyboard=True,
                resize_keyboard=True,
            ),
        )
        return 'department'


def main():
    ticketbot = Updater(
        os.environ.get('TELEGRAM_TOKEN'),
        request_kwargs=PROXY,
        use_context=True,
    )
    dp = ticketbot.dispatcher

    logging.info('Бот запускается')

    def stop_restart() -> None:
        """Остановка процесса бота"""
        ticketbot.stop()
        os.execl(sys.executable, sys.executable, *sys.argv)

    def restart(update, context) -> None:
        """Перезапуск бота"""
        Thread(target=stop_restart).start()
        update.message.reply_text('Успешно')

    dp.add_handler(CommandHandler('start', greet_user))
    dp.add_handler(CommandHandler('restart', restart))

    ticket = ConversationHandler(
        entry_points=[MessageHandler(
            Filters.regex(r'^(Создать заявку)$'),
            start_ticket,
            pass_user_data=True,
        )],
        states={
            'name': [MessageHandler(
                Filters.text,
                ticket_get_name,
                pass_user_data=True,
            )]
        },
        fallbacks=[],
    )
    dp.add_handler(ticket)

    ticketbot.start_polling()
    ticketbot.idle()


if __name__ == '__main__':
    main()
