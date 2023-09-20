let tg = window.Telegram.WebApp;
const USER = tg.initDataUnsafe.user;


function isNotEmpty(field){
    var fieldData = field.value;
    console.log(fieldData);
    if (fieldData.length == 0 || fieldData == "" || fieldData.length != 7) {
        return false;
    } 
    return true;
}


async function activate(){
    let coupon_input = document.getElementById('coupon');
    if (isNotEmpty(coupon_input) == false){
        tg.showAlert('Заполните пожалуйста поле перед отправкой');
        return;
    }

    let res = await Request(SERVER_URL + `/api/v1.0/coupon_activate`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            client_id: USER.id,
            coupon: coupon_input.value,
        })
    });

    if (res == null) {
        tg.showAlert('Сервер не отвечает, напишите в тех поддержку');
        return;
    }
    if (!res['status']) {
        tg.showAlert('Такой купон уже активирован, попробуйте другой');
        return;
    }
    tg.showAlert('Купон успешно активирован!', function(){
        window.location.replace(WEB_APP__URL + '/main');
    });
}


async function main(){
    tg.MainButton.setText('Активировать купон');
    tg.MainButton.show();
    tg.MainButton.onClick(function(){
        activate();
    });

    tg.BackButton.show()
    tg.BackButton.onClick(function(){
        window.location.replace(WEB_APP__URL + '/main');
    })
}

main();