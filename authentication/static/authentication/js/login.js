function login(event) {
    event.preventDefault();
    let email = document.querySelector("#loginInputEmail").value.replace(/^\s+|\s+$/g, '');
    let password = document.querySelector("#loginInputPassword").value.replace(/^\s+|\s+$/g, '');

    if (!email || !password) {
        document.querySelector("#loginError").innerHTML = "Incomplete Form";
        document.querySelector("#loginInputEmail").focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            prevent_default = false;
            enable_buttons();
            window.location.replace(res.next);
        } else {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#loginInputEmail").focus();
            document.querySelector("#loginError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('email', email);
    data.append('password', password);
    request.send(data);
    return false;
}