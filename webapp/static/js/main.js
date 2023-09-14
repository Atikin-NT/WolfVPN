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

function set_onclock_event(btn_list, event){
    for (const element of btn_list){
        element.onclick = event;
    }
}

function qrcode(){
    let a = this.id.split('-')[1];
    window.location.replace(`/qrcode/${a}`);
}

function download(){
    tg.showAlert('Бот выслал вам файл для подключения');
}

function delete_fun(){
    tg.showConfirm('Вы уверены?', function(a){
        console.log(a);
    })
}

let bill_history = document.getElementById('bill-history');
bill_history.onclick = function(){
    window.location.replace("http://127.0.0.1:5000/bill");
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
    console.log(user_peers.length);

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
    let tg = window.Telegram.WebApp;

    if (tg.MainButton.isVisiable){
        tg.MainButton.hide();
    }

    tg.BackButton.hide();

    let user_id = tg.initDataUnsafe.user.id;

    const user_info = await get_user_info(user_id);  // получение информации о пользователе
    console.log(user_info);
    set_user_info(user_info);  // обновление информации на странице

    let qrcode_btns = document.getElementsByClassName('action-qrcode');
    let download_btns = document.getElementsByClassName('action-download');
    let delete_btns = document.getElementsByClassName('action-delete');

    set_onclock_event(qrcode_btns, qrcode);
    set_onclock_event(download_btns, download);
    set_onclock_event(delete_btns, delete_fun);
}

main();