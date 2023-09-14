let li_country = `<div class="country">
                        <input class="radio_btn" type="radio" name="country" value="{country_id}">
                        <img src="static/images/{country_id}.png"/>
                        <p>$country</p>
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

// загрузка на фронт информации о подключении
function set_peers_info(peers_info){
    let current_peers = document.getElementById('current-peers-ul');
    // console.log(user_peers.length);

    for (let i = 0; i < peers_info.length; i++) {
        let peer = peers_info[i];
        let new_li = document.createElement("LI");
        let count_li = li_country.replaceAll('$country', peer['region']);
        count_li = count_li.replaceAll('{country_id}', peer['id']);
        new_li.innerHTML = count_li;
        console.log(new_li);
        current_peers.appendChild(new_li);
    }
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
    console.log(res);

    if (!res['status']) {
        tg.showAlert('Ошибка сервера, напишите в тех поддержку');
    } else {
        tg.showAlert('Все успешно!');
        // window.location.replace("http://127.0.0.1:5000/main");
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

    const peers_info = await get_peers_info();  // получение информации о пользователе
    console.log(peers_info);
    set_peers_info(peers_info);  // обновление информации на странице

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