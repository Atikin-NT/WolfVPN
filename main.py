import base64
import hmac
import hashlib

def main():
    sign = compute_signature(
        wpayStoreApiKey = "your_secret_api_key_sYIpNypce5sls6Ik",
        httpMethod = "POST",
        uriPath = "/webhook/",
        timestamp = "168824905680291",
        body = """[{"eventDateTime":"2023-07-28T10:20:17.681338Z","eventId":10030477545046017,"type":"ORDER_PAID","payload":{"id":10030467668508673,"number":"XYTNJP2O","customData":"in exercitation culpa","externalId":"JDF23NN","orderAmount":{"amount":"0.100000340","currencyCode":"TON"},"selectedPaymentOption":{"amount":{"amount":"0.132653","currencyCode":"USDT"},"amountFee":{"amount":"0.001327","currencyCode":"USDT"},"amountNet":{"amount":"0.131326","currencyCode":"USDT"},"exchangeRate":"1.3265247467314987"},"orderCompletedDateTime":"2023-07-28T10:20:17.628946Z"}}]"""
    )
    print(sign) # MGfJzeEprADZbihhRcGcCY5pYTI/IEJ91ejyA+XOWAs=

def compute_signature(
    wpayStoreApiKey,
    httpMethod,
    uriPath,
    timestamp,
    body,
):
    base64body = base64.b64encode(body.encode()).decode()
    stringToSign = f"{httpMethod}.{uriPath}.{timestamp}.{base64body}"
    mac = hmac.new(wpayStoreApiKey.encode(), stringToSign.encode(), hashlib.sha256)
    byteArraySignature = mac.digest()
    return base64.b64encode(byteArraySignature).decode()

if __name__ == '__main__':
    main()
