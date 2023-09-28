from flask import Blueprint, jsonify, request
from db.pay_history import GetClietnHistory, AddBill, UpdateBillStatus
from db.clients import GetClientById, UpdateClientAmount
from db.codes import GetCode, ActivateCode
import yoomoney
import utils
import configparser

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
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'amount' not in request_data or int(request_data['amount']) < 20 or int(request_data['amount']) > 500:
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
    except Exception as msg:
        answer['status'] = False
        answer['data'] = str(msg)
        return jsonify(answer)

    return jsonify(answer)


@pay_api.route('/api/v1.0/coupon_activate', methods=['POST'])
def coupon_activate():
    """активация купона

    Args(POST):
        client_id (int): id пользователя из телеги
        coupon (int): купон
    """
    answer = utils.json_template.copy()
    request_data = request.get_json()
    if 'client_id' not in request_data or 'coupon' not in request_data or len(request_data['coupon'].strip()) != 7:
        answer['status'] = False
        answer['data'] = 'Client id and coupon not presented'
        return jsonify(answer)

    client_id = int(request_data['client_id'])
    coupon = str(request_data['coupon'])

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
    except Exception as msg:
        answer['status'] = False
        answer['data'] = str(msg)
        return jsonify(answer)

    answer['data'] = 'ok'
    return jsonify(answer)