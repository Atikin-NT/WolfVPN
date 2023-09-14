/**
 * Есть пользователь в системе или нет
 * @param {int} user_id id пользователя в телеге 
 * @returns {boolean} есть пользователь в системе или нет
 */
async function is_user_in_system(user_id){
    let res = await Request(SERVER_URL + `/api/v1.0/check_user/${user_id}`, { method: "GET"});
    if (res == null) {
        tg.showAlert('Сервер не отвечает, напишите в тех поддержку');
        return;
    }
    if (!res['status']) {
        tg.showAlert('Ошибка сервера, напишите в тех поддержку');
        return;
    }

    return res['data']['user_exist']; 
}

/**
 * регистрация нового пользователя
 * @param {int} user_id id пользователя в телеге 
 * @param {string} username имя пользователя
 * @param {string} first_name ник пользователя
 */
async function user_register(user_id, username, first_name) {
    let name = username;
    if (username == null || username == undefined || username == ""){
        name = first_name;
    }
    let res = await Request(SERVER_URL + `/api/v1.0/add_user/`, { 
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
          },
        body: JSON.stringify({
            client_id: user_id,
            name: name
        })
    });

    if (!res['status']) {
        tg.showAlert('Ошибка сервера, напишите в тех поддержку');
    } else {
        window.location.replace("http://127.0.0.1:5000/main");
    }
}

async function main(){
    let tg = window.Telegram.WebApp;
    let user = tg.initDataUnsafe.user;

    if (await is_user_in_system(user.id)) {  // если пользователь есть в системе, то перекидываем на главную страницу
        window.location.replace(WEB_APP__URL + "/main");
    }
    
    // если пользователя нет в системе, то регистрируем по нажатию на кнопку, а потом перекидываем на главную
    tg.MainButton.setText('Join');
    tg.MainButton.show();
    tg.MainButton.onClick(function(){
        user_register(user.id, user.username, user.first_name);
    });
}

main();