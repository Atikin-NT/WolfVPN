from flask import Blueprint, jsonify, request
from db.pay_history import AddBill, UpdateBillStatus, GetBillById
from db.clients import GetClientById, UpdateClientAmount
from db.codes import GetCode, ActivateCode
import db.exeption as ex
import yoomoney
import utils
import configparser
import logging

config = configparser.ConfigParser()
config.read('./config.ini')
yoomoney_config = config['yoomoney']

pay_api = Blueprint('pay_api', __name__)


@pay_api.route('/api/v1.0/create_bill', methods=['POST'])
def create_bill():
    """создание чека юмани

    Args(POST):
        client_id (int): id пользователя из телеги
        amount (int): сумма чека
    """
    logging.info('create_bill')
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'amount' not in request_data or int(request_data['amount']) < 20 or int(request_data['amount']) > 500:
        logging.error(f'invalid params in create_bill: request_data = {request_data}')
        answer['status'] = False
        answer['data'] = 'Client id and amount not presented'
        return jsonify(answer)

    client_id = int(request_data['client_id'])
    amount = int(request_data['amount'])

    try:
        bill_id = AddBill().execute(client_id, amount)
        quickpay = yoomoney.Quickpay(
            receiver=yoomoney_config['receiver'],
            quickpay_form="shop",
            targets="WolfVPN",
            paymentType="SB",
            sum=amount,
            label=f'{bill_id}_{client_id}_{amount}'
        )

        answer['data'] = {'bill': quickpay.redirected_url}
    except (ex.ClientNotExist, ValueError) as e:
        logging.error(f'Add bill and quickpay: client_id = {client_id}, amount = {amount}, ex = {e}')
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
    logging.info('coupon_activate')
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'coupon' not in request_data or len(request_data['coupon'].strip()) != 7:
        logging.error(f'invalid params in coupon_activate: request_data = {request_data}')
        answer['status'] = False
        answer['data'] = 'Client id and coupon not presented'
        return jsonify(answer)

    client_id = int(request_data['client_id'])
    coupon = str(request_data['coupon'])
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
        logging.error(f'activate code and update amount: client_id = {client_id}, coupon = {coupon}, ex = {e}')
        answer['status'] = False
        answer['data'] = str(e)
    
    return jsonify(answer)


@pay_api.route('/api/v1.0/yoomoney_callback', methods=['POST'])
def get_pay():
    """обработчик callback с yoomoney
    Обновляет баланс пользователя взависимости от параметров с юмани
    """
    withdraw_amount = int(request.form.get("withdraw_amount").split('.')[0])
    label = request.form.get("label")
    bill_id, client_id, amount = label.split('_')
    bill_id = int(bill_id)
    client_id = int(client_id)
    amount = int(amount)

    logging.info(f'get_pay: label = {label}, withdraw_amount = {withdraw_amount}')

    bill = GetBillById().execute(bill_id)
    assert int(bill['amount']) == amount
    
    UpdateBillStatus().execute(bill_id, 2)

    client = GetClientById().execute(client_id)

    new_amount = int(client['amount']) + amount
    UpdateClientAmount().execute(client_id, new_amount)

    return '', 200