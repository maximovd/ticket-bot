import os

from dotenv import load_dotenv
from bitrix24 import Bitrix24

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

BX24_TOKEN = os.environ.get('TOKEN')
BX24_URL = os.environ.get('URL')


def create_deal(user_data, token=BX24_TOKEN, url=BX24_URL) -> None:
    bx24 = Bitrix24(url, user_id=196)

    full_name = user_data['full_name']
    description = user_data['description']
    phone_number = user_data['phone_number']
    email = user_data['email']
    department = int(user_data['department'])

    bx24.call_webhook('crm.deal.add', token, params={
        'fields': {
            'CATEGORY_ID': 27,
            'UF_CRM_1588855684': full_name,
            'UF_CRM_1588855793': department,
            'UF_CRM_1588856215': description,
            'EMAIL': email,
            'PHONE': phone_number,
         },
    })


def _call_custom_command(token=BX24_TOKEN, url=BX24_URL):
    bx24 = Bitrix24(url, user_id=196)
    result = bx24.call_webhook('crm.contact.fields', token, params={
        'ID': 27
    })
    return result


if __name__ in '__main__':
    print(_call_custom_command())