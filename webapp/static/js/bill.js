let tg = window.Telegram.WebApp;
tg.BackButton.show();

tg.BackButton.onClick(function(){
    window.location.replace("http://127.0.0.1:5000/main");
});