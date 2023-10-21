let li_bill = `<p>Сумма: <span>{amount} W</span></p>
                <p>Дата: <span>{date}</span></p>
                <p>Статус: <span>{status}</span></p>`;

let tg = window.Telegram.WebApp;
const USER = tg.initDataUnsafe.user;


// получение информации ою операциях
async function get_pay_info(user_id){
    let res = await Request(SERVER_URL + `/api/v1.0/bill_history`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            client_id: user_id
        })
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


// загрузка на фронт информации об операциях
function set_pay_info(user_info){
    let user_bills = user_info['bills'];
    let current_bills = document.getElementById('pay-ul');

    for (let i = 0; i < user_bills.length; i++) {
        let bill = user_bills[i];
        let new_li = document.createElement("LI");
        let bill_li = li_bill.replaceAll('{amount}', bill['amount']);
        bill_li = bill_li.replaceAll('{date}', bill['create_date']);

        let status_str = ((bill['status'] == 0) ? 'Ожидает подтверждения' : 'Выполнено');

        bill_li = bill_li.replaceAll('{status}', status_str);
        new_li.innerHTML = bill_li;
        current_bills.appendChild(new_li);
    }
}

async function main(){
    let tg = window.Telegram.WebApp;

    if (tg.MainButton.isVisiable){
        tg.MainButton.hide();
    }

    tg.BackButton.show()
    tg.BackButton.onClick(function(){
        window.location.replace(WEB_APP__URL + '/main');
    })


    const pay_info = await get_pay_info(USER.id);
    set_pay_info(pay_info);
}

main();