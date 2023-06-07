import aiohttp
import asyncio
import os
import random
import logging
from faker import Faker

SCAMMER_DOMAIN = 'nzta.37q7i.com'
proxy = os.environ.get('PROXY') # For bonus points use a rotating proxy network to make it harder for scammers to figure out which CC's came from this tool

fake = Faker()


def get_plate_number():
    return [random.choice(('ABCDEFGHJKLMNOPQRSTUVWXYZ0123456789')) for _ in range(6)]


async def get_php_session_cookie(session):
    headers = {
        'authority': SCAMMER_DOMAIN,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        'origin': f'https://{SCAMMER_DOMAIN}',
        'pragma': 'no-cache',
        'referer': f'https://{SCAMMER_DOMAIN}/page2.php',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    data = {
        'plate_number': get_plate_number(),
        'SubmitButton': 'Get started',
    }

    r = await session.post(f'https://{SCAMMER_DOMAIN}/payment.php', headers=headers, data=data, proxy=proxy)
    logging.info('Acquired session cookie: ' + str(r.cookies))


def generate_card_details():
    """    data = {
        'CardNumber': '1234 5678 9101 1234',
        'ExpiryDate': '01/28',
        'CardCvv': '324',
        'card_holder_name': 'FAKE NAME',
        'payment_submit': '',
    }"""
    card_details = {}
    card_number = fake.credit_card_number(card_type='visa')
    card_details['CardNumber'] = ' '.join(card_number[i:i+4] for i in range(0, len(card_number), 4))
    card_details['ExpiryDate'] = fake.credit_card_expire(start="now", end="+10y", date_format="%m/%y")
    card_details['CardCvv'] = fake.credit_card_security_code()
    card_details['card_holder_name'] = fake.name().upper()
    card_details['payment_submit'] = ''

    return card_details


async def send_details(session):
    headers = {
        'authority': SCAMMER_DOMAIN,
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'en-US,en;q=0.9',
        'cache-control': 'no-cache',
        'content-type': 'application/x-www-form-urlencoded',
        # 'cookie': 'PHPSESSID=kqprp2hv0l41i4iq48kcfmd6ff',
        'origin': f'https://{SCAMMER_DOMAIN}',
        'pragma': 'no-cache',
        'referer': f'https://{SCAMMER_DOMAIN}/payment.php',
        'sec-ch-ua': '"Not.A/Brand";v="8", "Chromium";v="114", "Google Chrome";v="114"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    }

    data = generate_card_details()

    r = await session.post('https://nzta.37q7i.com/payment.php', headers=headers, data=data, proxy=proxy)
    logging.info('Sent card details: ' + str(r.status))


async def spam():
    async with aiohttp.ClientSession() as session:
        await get_php_session_cookie(session)
        await send_details(session)


async def main():
    while True:
        tasks = []
        for i in range(10):
            tasks.append(asyncio.ensure_future(spam()))
        await asyncio.gather(*tasks)

logging.basicConfig(level=logging.INFO)
asyncio.run(main())