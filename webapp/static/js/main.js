let tg = window.Telegram.WebApp;

if (tg.MainButton.isVisiable){
    tg.MainButton.hide();
}

tg.BackButton.hide();

let qrcode_btns = document.getElementsByClassName('action-qrcode');
let download_btns = document.getElementsByClassName('action-download');
let delete_btns = document.getElementsByClassName('action-delete');

function set_onclock_event(btn_list, event){
    for (const element of btn_list){
        element.onclick = event;
    }
}

function qrcode(){
    window.location.replace("http://127.0.0.1:5000/qrcode");
}

function download(){
    tg.showAlert('Бот выслал вам файл для подключения');
}

function delete_fun(){
    tg.showConfirm('Вы уверены?', function(a){
        console.log(a);
    })
}

set_onclock_event(qrcode_btns, qrcode);
set_onclock_event(download_btns, download);
set_onclock_event(delete_btns, delete_fun);

let bill_history = document.getElementById('bill-history');
bill_history.onclick = function(){
    window.location.replace("http://127.0.0.1:5000/bill");
}