let li_country = `<div class="country">
                        <input class="radio_btn" type="radio" name="country" value="{country_id}" {disabled}>
                        <img src="static/images/{country_id}.png"/>
                        <p>{country}</p>
                    </div>`;

let result_country = -1;  // итоговое значение страны для подключения

// получение информации о подключении
async function get_peers_info(){
    let res = await Request(SERVER_URL + `/api/v1.0/region_list`, {
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

// получение информации о пользователе
async function get_user_peers(user_id){
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

    return res['data']['peers'];
}

// загрузка на фронт информации о подключении
async function set_peers_info(peers_info, user_peers){
    let current_peers = document.getElementById('current-peers-ul');

    for (let i = 0; i < peers_info.length; i++) {
        let peer = peers_info[i];
        let disabled = '';
        if (is_host_in_user(user_peers, peer['id'])) {
            disabled = 'disabled';
        }
        let new_li = document.createElement("LI");
        let count_li = li_country.replaceAll('{country}', peer['region']);
        count_li = count_li.replaceAll('{country_id}', peer['id']);
        count_li = count_li.replaceAll('{disabled}', disabled);
        new_li.innerHTML = count_li;
        console.log(new_li);
        current_peers.appendChild(new_li);
    }
}

// проверка, есть ли этот хост у текущего пользователя
function is_host_in_user(user_peers, host_id){
    for(let i = 0; i < user_peers.length; i++){
        const peer = user_peers[i];
        if (peer['host_id'] == host_id) {
            return true;
        }
    }
    return false;
}

async function add_peer(user_id, host_id, username, first_name, tg) {
    let name = username;
    if (username == null || username == undefined || username == ""){
        name = first_name;
    }
    let res = await Request(SERVER_URL + `/api/v1.0/add_peer`, { 
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            client_id: user_id,
            host_id: host_id,
            username: name
        })
    });

    if (!res['status']) {
        tg.showAlert('Ошибка сервера, напишите в тех поддержку');
    } else {
        tg.showAlert('Все успешно!');
        window.location.replace(WEB_APP__URL + '/main');
    }
}

async function main(){
    let tg = window.Telegram.WebApp;
    const user = tg.initDataUnsafe.user;

    tg.MainButton.hide();
    tg.MainButton.setText('Подключить');
    tg.MainButton.onClick(function(){
        add_peer(user.id, result_country, user.username, user.first_name, tg);
    });

    tg.BackButton.show();
    tg.BackButton.onClick(function(){
        window.location.replace(WEB_APP__URL + '/main');
    })

    const peers_info = await get_peers_info();  // получение информации о хостах
    const user_peers = await get_user_peers(user.id);  // получаем какие хосты у текущего пользователя
    set_peers_info(peers_info, user_peers);  // обновление информации на странице

    let all_radio_btns = document.getElementsByClassName('radio_btn');
    for (var i = 0; i < all_radio_btns.length; i++) {
        all_radio_btns[i].addEventListener('change', function() {
            if (tg.MainButton.isVisible == false){
                tg.MainButton.show();
            }
            result_country = this.value;
        });
    }
}

main();