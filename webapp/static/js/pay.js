let tg = window.Telegram.WebApp;
const USER = tg.initDataUnsafe.user;


function isNotEmpty(field){
    var fieldData = field.value;
    console.log(fieldData);
    if (fieldData.length == 0 || fieldData == "") {
        return false;
    } 
    return true;
}


function open_bill(bill_url){
    tg.openLink(bill_url);
    tg.showAlert('После успешной оплаты ваш счет пополнится автоматически. Если этого не так, то напишите в тех поддержку.', function() {
        window.location.replace(WEB_APP__URL + '/main');
    })
}


async function create_bill(){
    let amount_input = document.getElementById('amount');
    if (isNotEmpty(amount_input) == false){
        tg.showAlert('Заполните пожалуйста поле перед отправкой');
        return;
    }

    let res = await Request(SERVER_URL + `/api/v1.0/create_bill`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            client_id: USER.id,
            amount: amount_input.value,
        })
    });

    if (res == null) {
        tg.showAlert('Сервер не отвечает, напишите в тех поддержку');
        return;
    }
    if (!res['status']) {
        tg.showAlert('Произошла ошибка на сервере, напишите в тех поддержку');
        return;
    }
    
    tg.MainButton.setText('Оплатить квитанцию');
    tg.MainButton.color = '#FF0000';
    tg.MainButton.onClick(function(){
        open_bill(res['data']['bill']);
    });
}


async function main(){
    tg.MainButton.setText('Получить квитанцию');
    tg.MainButton.show();
    tg.MainButton.onClick(function(){
        create_bill();
    });

    tg.BackButton.show()
    tg.BackButton.onClick(function(){
        window.location.replace(WEB_APP__URL + '/main');
    });
}

main();