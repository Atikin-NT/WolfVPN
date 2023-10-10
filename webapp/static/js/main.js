let li_country = `<div class="country">
                        <img src="static/images/{country_id}.png"/>
                        <p>$country</p>
                    </div>
                    <div class="buttons">
                        <button class="action-qrcode" id="qrcode-{country_id}">
                            <img src="static/images/qrcode.svg"/>
                        </button>
                        <button class="action-download" id="download-{country_id}">
                            <img src="static/images/download.svg"/>
                        </button>
                        <button class="action-delete" id="delete-{country_id}">
                            <img src="static/images/delete.svg"/>
                        </button>
                    </div>`;

let ALL_USER_PEERS = [];
let PEER_CHOICE = -1;
const tg = window.Telegram.WebApp;
const USER = tg.initDataUnsafe.user;

// добавление новго подключения
function add_peer(){
    console.log('add peer');
    window.location.replace(`/add_peer`);
}

// показ qr кода
function qrcode(){
    let a = this.id.split('-')[1];
    window.location.replace(`/qrcode/${a}`);
}


// скачать подключение
async function download(){
    tg.showAlert('Бот выслал вам файл для подключения');
    const host_id = this.id.split('-')[1];
    let res = await Request(SERVER_URL + `/api/v1.0/download`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            client_id: USER.id,
            host_id: host_id,
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

}

async function delete_callback(a){
    if (a == false){
        return;
    }

    const host_id = PEER_CHOICE;
    let res = await Request(SERVER_URL + `/api/v1.0/remove_peer`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            client_id: USER.id,
            host_id: host_id,
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
    location.reload();
}

// удалить подключение
async function delete_fun(){
    PEER_CHOICE = this.id.split('-')[1];
    tg.showConfirm('Вы уверены?', delete_callback);
}

// активация купона
function coupon(){
    window.location.replace(`/coupon`);
}

// пополнить счет
function pay(){
    window.location.replace(`/pay`);
}

// история пополнения счета
function pay_history(){
    window.location.replace(`/bill`);
}

// тех поддержка
function help(){
    tg.openTelegramLink('https://t.me/wolf0vpn_help_bot');
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
    let user_amount = document.getElementById('user_amount');
    user_amount.innerHTML = `${user_info['amount']},00<span> ₽</span>`;

    let user_left_days = document.getElementById('user_left_days');
    user_left_days.textContent = user_info['day_left'];

    let user_peers = user_info['peers'];
    let current_peers = document.getElementById('current-peers-ul');

    for (let i = 0; i < user_peers.length; i++) {
        let peer = user_peers[i];
        let new_li = document.createElement("LI");
        let count_li = li_country.replaceAll('$country', peer['region']);
        count_li = count_li.replaceAll('{country_id}', peer['host_id']);
        new_li.innerHTML = count_li;
        console.log(new_li);
        current_peers.appendChild(new_li);
    }
}

async function main(){

    tg.MainButton.setText('Добавить подключение');
    tg.MainButton.show();
    tg.MainButton.onClick(function(){
        add_peer();
    });

    tg.BackButton.hide();

    let user_id = USER.id;

    const user_info = await get_user_info(user_id);  // получение информации о пользователе
    ALL_USER_PEERS = user_info['peers'];
    set_user_info(user_info);  // обновление информации на странице

    let qrcode_btns = document.getElementsByClassName('action-qrcode');
    let download_btns = document.getElementsByClassName('action-download');
    let delete_btns = document.getElementsByClassName('action-delete');
    let coupon_btns = document.getElementsByClassName('coupon');
    let pay_btns = document.getElementsByClassName('pay_btn');
    let help_btns = document.getElementsByClassName('help_btn');
    let bill_history = document.getElementsByClassName('bill-history');

    set_onclock_event(qrcode_btns, qrcode);
    set_onclock_event(download_btns, download);
    set_onclock_event(delete_btns, delete_fun);
    set_onclock_event(coupon_btns, coupon);
    set_onclock_event(pay_btns, pay);
    set_onclock_event(bill_history, pay_history);
    set_onclock_event(help_btns, help);
}

main();