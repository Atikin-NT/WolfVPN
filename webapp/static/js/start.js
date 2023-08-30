let tg = window.Telegram.WebApp;

tg.MainButton.setText('Join');
tg.MainButton.show();
tg.MainButton.onClick(function(){
    window.location.replace("http://127.0.0.1:5000/main");
});