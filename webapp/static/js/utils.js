// const SERVER_URL = 'http://127.0.0.1:8000';
// const WEB_APP__URL = 'http://127.0.0.1:5000';

const SERVER_URL = 'https://wolfvpn.ru:8443';
const WEB_APP__URL = 'https://wolfvpn.ru';
/**
 *  Выполнение запроса
 * @param {string} url адрес для запроса
 * @param {object} data словарь параметров
 * @returns {object} json ответ. Если ответ != 2xx, то ответ null
 */
async function Request(url, data){
    let response = await fetch(url, data);
    let json = null;
    if (response.ok) {
        json = await response.json();
    }
    console.log(json);
    return json;
}

function set_onclock_event(btn_list, event){
    for (const element of btn_list){
        element.onclick = event;
    }
}

function get_day_str(day_count){
    switch (day_count % 10) {
        case 1:
            return "день";
        case 2:
        case 3:
        case 4:
            return "дня";
        default:
            return "дней";
    }
}