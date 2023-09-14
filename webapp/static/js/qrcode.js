let tg = window.Telegram.WebApp;

if (tg.MainButton.isVisiable){
    tg.MainButton.hide();
}

tg.BackButton.show()
tg.BackButton.onClick(function(){
    window.location.replace("http://127.0.0.1:5000/main");
})

async function get_qr_code(user_id) {
    const host_id_split = document.URL.split('/');
    const host_id = host_id_split[host_id_split.length - 1];

    let res = await Request(SERVER_URL + `/api/v1.0/qrcode/`, {
        method: "POST",
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            client_id: user_id,
            host_id: host_id
        })
    });

    console.log(res);
}


async function main(){
    let tg = window.Telegram.WebApp;

    if (tg.MainButton.isVisiable){
        tg.MainButton.hide();
    }

    tg.BackButton.show()
    tg.BackButton.onClick(function(){
        window.location.replace("http://127.0.0.1:5000/main");
    })

    const user_id = tg.initDataUnsafe.user.id;

    get_qr_code(user_id);
}

main();