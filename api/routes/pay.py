from flask import Blueprint, jsonify, request
from db.pay_history import AddBill, UpdateBillStatus, GetBillById
from db.clients import GetClientById, UpdateClientAmount
from db.codes import GetCode, ActivateCode
import db.exeption as ex
import requests
import utils
import configparser
import logging
import base64
import hmac
import hashlib
from yoomoney import Quickpay

config = configparser.ConfigParser()
config.read('./config.ini')
ton_wallet_config = config['ton_wallet']
wallet_api = ton_wallet_config['api']
webhook = ton_wallet_config['webhook']

yoomoney_config = config['yoomoney']
receiver = yoomoney_config['receiver']
yoomoney_secret = yoomoney_config['secret']

pay_api = Blueprint('pay_api', __name__)

logger = logging.getLogger('gunicorn.error')


def create_order(client_id: int, amount: int, order_id: int) -> str:
    h = {
        'Wpay-Store-Api-Key': wallet_api,
    }
    payload = {
        "amount": {
            "currencyCode": "RUB",
            "amount": str(amount)
        },
        "description": f"Пополнение счета WolfVPN в размере {amount}",
        "returnUrl": "https://t.me/wolf0vpn_bot",
        "failReturnUrl": "https://t.me/wolf0vpn_bot",
        "customData": f"{client_id} {amount} {order_id}",
        "externalId": str(order_id),
        "timeoutSeconds": 10800,
        "customerTelegramUserId": client_id
    }
    r = requests.post(
        'https://pay.wallet.tg/wpay/store-api/v1/order',
        headers=h,
        json=payload
    )

    logger.info(f'{r}')

    if r.status_code != 200:
        raise InterruptedError("can't create order")

    order_data = r.json()

    if order_data['status'] != 'SUCCESS':
        logger.error(f'Cant create order, msg={order_data["message"]}')
        raise InterruptedError("can't create order status error")

    return order_data['data']['directPayLink']


def create_yoomoney_order(amount: int, order_id: int) -> str:
    quickpay = Quickpay(
        receiver=receiver,
        quickpay_form="shop",
        targets="WolfVPN",
        paymentType="SB",
        sum=amount,
        label=str(order_id),
    )
    return quickpay.redirected_url


@pay_api.route('/api/v1.0/create_bill', methods=['POST'])
def create_bill():
    """создание чека ton wallet или yoomoney

    Args(POST):
        client_id (int): id пользователя из телеги
        amount (int): сумма чека
    """
    logger.info('create_bill')
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if ('client_id' not in request_data or 'amount' not in request_data or 'type' not in request_data
        or int(request_data['amount']) < 0 or int(request_data['amount']) > 500):
        logger.error(f'invalid params in create_bill: request_data = {request_data}')
        answer['status'] = False
        answer['data'] = 'Client id and amount not presented'
        return jsonify(answer)

    client_id = int(request_data['client_id'])
    amount = int(request_data['amount'])
    type = request_data['type']

    try:
        bill_id = AddBill().execute(client_id, amount)
        if type == 'yoomoney':
            create_order_url = create_yoomoney_order(amount, bill_id)
        elif type == 'wallet':
            create_order_url = create_order(client_id, amount, bill_id)
        else:
            raise InterruptedError('type of pay not found')

        answer['data'] = {'bill': create_order_url}
    except (ex.ClientNotExist, ValueError) as e:
        logger.error(f'Add bill and quickpay: client_id = {client_id}, amount = {amount}, ex = {e}')
        answer['status'] = False
        answer['data'] = str(e)

    return jsonify(answer)


@pay_api.route('/api/v1.0/coupon_activate', methods=['POST'])
def coupon_activate():
    """активация купона

    Args(POST):
        client_id (int): id пользователя из телеги
        coupon (int): купон
    """
    logger.info('coupon_activate')
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'coupon' not in request_data or len(request_data['coupon'].strip()) != 7:
        logger.error(f'invalid params in coupon_activate: request_data = {request_data}')
        answer['status'] = False
        answer['data'] = 'Client id and coupon not presented'
        return jsonify(answer)

    client_id = int(request_data['client_id'])
    coupon = str(request_data['coupon'])
    logger.info(f'coupon = {coupon}')
    answer['data'] = 'ok'

    try:
        code = GetCode().execute(coupon)
        if code is None:
            raise InterruptedError('coupon not exist')
        if code['activated'] is True:
            raise InterruptedError('coupon already activate')

        ActivateCode().execute(coupon)
        client = GetClientById().execute(client_id)

        if client is None:
            raise InterruptedError('client not exist')

        UpdateClientAmount().execute(
            client_id=client_id,
            amount=int(code['amount']) + int(client['amount'])
        )
    except ValueError as e:
        logger.error(f'activate code and update amount: client_id = {client_id}, coupon = {coupon}, ex = {e}')
        answer['status'] = False
        answer['data'] = str(e)
    
    return jsonify(answer)


@pay_api.route('/api/v1.0/wallet_callback', methods=['POST'])
def get_pay():
    """обработчик callback с ton wallet
    Обновляет баланс пользователя взависимости от параметров с wallet
    """

    timestamp = request.headers['WalletPay-Timestamp']
    wallet_sign = request.headers['WalletPay-Signature']
    body = request.get_json()
    r_data = request.data

    logger.info(f'get_pay: timestamp = {timestamp}, wallet_sign = {wallet_sign}, body = {body}')

    sign = compute_signature(
        wpayStoreApiKey = wallet_api,
        httpMethod = "POST",
        uriPath = webhook,
        timestamp = timestamp,
        body = r_data
    )

    logger.info(f'get_pay: sign = {sign}')
    body = body[0]

    if wallet_sign != sign:
        raise InterruptedError('sing not equal')
    
    if body['type'] != 'ORDER_PAID':
        raise InterruptedError('Order failed')
    
    bill_id = body['payload']['externalId']
    amount = int(float(body['payload']['orderAmount']['amount']))


    bill = GetBillById().execute(bill_id)
    client_id = bill['client_id']
    assert int(bill['amount']) == amount
    
    UpdateBillStatus().execute(bill_id, 2)

    client = GetClientById().execute(client_id)

    new_amount = int(client['amount']) + amount
    UpdateClientAmount().execute(client_id, new_amount)

    return '', 200


def compute_signature(
    wpayStoreApiKey,
    httpMethod,
    uriPath,
    timestamp,
    body,
):
    base64body = base64.b64encode(body).decode()
    stringToSign = f"{httpMethod}.{uriPath}.{timestamp}.{base64body}"
    mac = hmac.new(wpayStoreApiKey.encode(), stringToSign.encode(), hashlib.sha256)
    byteArraySignature = mac.digest()
    return base64.b64encode(byteArraySignature).decode()

@pay_api.route('/api/v1.0/yoomoney_callback', methods=['POST'])
def get_pay_yoomoney():
    """обработчик callback с yoomoney
    Обновляет баланс пользователя взависимости от параметров с yoomoney
    """
    form_data = request.form.to_dict()
    amount = int(float(form_data['withdraw_amount']))
    bill_id = form_data['label']

    logger.info(f'get_pay(yoomoney): withdraw_amount = {amount}, bill_id = {bill_id}, form_data = {form_data}')

    if yoomoney_sign_check(form_data) is False:
        logger.error('Sign not equal in yoomoney')
        raise InterruptedError('Sign not equal in yoomoney')

    bill = GetBillById().execute(bill_id)
    client_id = bill['client_id']
    assert int(bill['amount']) == amount
    
    UpdateBillStatus().execute(bill_id, 2)

    client = GetClientById().execute(client_id)

    new_amount = int(client['amount']) + amount
    UpdateClientAmount().execute(client_id, new_amount)

    return '', 200


def yoomoney_sign_check(data: dict) -> bool:
    string_for_test = f"""{data['notification_type']}&{data['operation_id']}&{data['amount']}&{data['currency']}&{data['datetime']}&{data['sender']}&{data['codepro']}&{yoomoney_secret}&{data['label']}"""
    sha_code = hashlib.sha1(string_for_test.encode())
    sign = sha_code.hexdigest()
    logger.info(f'Yoomoney sign: sign = {sign}, sha1_hash = {data["sha1_hash"]}')
    return sign == data['sha1_hash']
