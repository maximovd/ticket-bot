import os
import sys
import logging
from threading import Thread

from dotenv import load_dotenv

from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
    CallbackContext,
)

from handlers import (
    greet_user,
    start_ticket,
    ticket_get_name,
    ticket_department,
    ticket_description,
    ticket_email,
    ticket_phone_number,
    ticket_confirmation,
    cancel,
    failure,
)

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
