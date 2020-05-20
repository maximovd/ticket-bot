import os

from dotenv import load_dotenv
from bitrix24 import Bitrix24

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

bx24_token = os.environ.get('TOKEN')
bx24_url = os.environ.get('URL')


def create_deal(user_data, token=bx24_token, url=bx24_url) -> None:
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


def _call_custom_command(token=bx24_token, url=bx24_url):
    bx24 = Bitrix24(url, user_id=196)
    result = bx24.call_webhook('crm.contact.fields', token, params={
        'ID': 27
    })
    print(result)


if __name__ in '__main__':
    _call_custom_command()