const SERVER_URL = 'http://127.0.0.1:5001';
const WEB_APP__URL = 'http://127.0.0.1:5000';

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
    return json;
}