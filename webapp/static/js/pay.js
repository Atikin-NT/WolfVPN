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

function get_payment_type(){
    const wallet_type = document.getElementById('wallet');

    if (wallet_type.checked)
        return 'wallet';
    return 'yoomoney';
}


async function create_bill(){
    let amount_input = document.getElementById('amount');
    let payment_type = get_payment_type();
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
            type: payment_type,
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
    
    tg.MainButton.setText(`Pay via ${payment_type}`);
    tg.MainButton.color = '#FF0000';
    tg.MainButton.offClick();
    tg.MainButton.onClick(function(){
        open_bill(res['data']['bill']);
    });
}


// получение информации о пользователе
async function get_user_info(user_id){
    let res = await Request(SERVER_URL + `/api/v1.0/user/${user_id}`, {
        method: "GET"
    });
    if (res == null) {
        tg.showAlert('Сервер не отвечает, напишите в тех поддержку');
        return;
    }
    if (!res['status']) {
        tg.showAlert('Ошибка сервера, напишите в тех поддержку');
        return;
    }

    return res['data'];
}

// загрузка на фронт информации о пользователе
function set_user_info(user_info){
    let user_amount = document.getElementsByClassName('user_amount')[0];
    user_amount.innerHTML = `${user_info['amount']},00<span> W</span>`;
}

async function main(){
    tg.MainButton.setText('Получить квитанцию');
    tg.MainButton.show();
    tg.MainButton.onClick(function(){
        create_bill();
    });

    const user_info = await get_user_info(USER.id);
    set_user_info(user_info);

    tg.BackButton.show()
    tg.BackButton.onClick(function(){
        window.location.replace(WEB_APP__URL + '/main');
    });
}

main();