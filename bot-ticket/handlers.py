import os

from dotenv import load_dotenv
from bitrix24 import Bitrix24

dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

bx24_token = os.environ.get('TOKEN')
bx24_url = os.environ.get('URL')


def create_deal(token: str, url: str) -> None:
    bx24 = Bitrix24(url, user_id=196)
    bx24.call_webhook('crm.deal.add', token, params={
        'fields': {
            'CATEGORY_ID': None,
            'UF_CRM_1588855684': 'NAME',
            'UF_CRM_1588855793': None,
            'UF_CRM_1588856215': 'Comment',
            'UF_CRM_1588886392': 'example@example.com',
            'UF_CRM_5BC6E8532C716': None,
         },
    })


if __name__ in '__main__':
    create_deal(token=bx24_token, url=bx24_url)
