function displayRecoverModal(event) {
    event.preventDefault();
    const details_template = Handlebars.compile(document.querySelector('#recoverFormHandlebars').innerHTML);
    const details = details_template();
    document.querySelector("#recoverModal").innerHTML = details;

    const recoverModal = document.getElementById('recoverModal');
    const recoverEmail = document.getElementById('recoverEmail');
    recoverModal.addEventListener('shown.bs.modal', () => {
        recoverEmail.focus();
    })

    document.querySelector("#displayRevoverModal").click();
    return false;
}


function recover(event) {
    event.preventDefault();
    let email = document.querySelector("#recoverEmail").value.replace(/^\s+|\s+$/g, '');
    if (!email) {
        document.querySelector("#recoverError").innerHTML = "Incomplete Form";
        document.getElementById('recoverEmail').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/recover/');
    request.setRequestHeader("X-CSRFToken", csrftoken);
    
    disable_buttons();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            document.querySelector("#recoverModalCloseButton").click();
            displayRecoverVerificationModal(res.data);
        } else {
            prevent_default = false;
            enable_buttons();
            document.getElementById('recoverEmail').focus();
            document.querySelector("#recoverError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('email', email);
    request.send(data);
    return false;
}

function displayRecoverVerificationModal(data) {
    const details_template = Handlebars.compile(document.querySelector('#recoverVerifyHandlebars').innerHTML);
    const details = details_template({"data": data});
    document.querySelector("#recoverVerificationModal").innerHTML = details;

    const recoverVerificationModal = document.getElementById('recoverVerificationModal');
    const recoverVerifyCode = document.getElementById('recoverVerifyCode');
    recoverVerificationModal.addEventListener('shown.bs.modal', () => {
        recoverVerifyCode.focus();
    })

    document.querySelector("#recoverVerificationModalButton").click();
    return;
}


function cancelrecoverVerify() {
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/recover/verify/cancel/');
    
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            prevent_default = false;
        }
    };
    request.send();
    return false;
}


function recoverVerifyCodeResend(event) {
    event.preventDefault();
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/recover/verify/resend/');
    disable_buttons();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            document.getElementById('recoverVerifyCode').focus();
            document.querySelector("#recoverVerifyError").innerHTML = "A new verification code was sent to your email address.";
        } else {
            prevent_default = false;
            enable_buttons();
            document.getElementById('recoverVerifyCode').focus();
            document.querySelector("#recoverVerifyError").innerHTML = res.message;
        }
    };
    request.send();
    return false;
}


function recoverVerify(event) {
    event.preventDefault();
    let code = document.querySelector("#recoverVerifyCode").value.replace(/^\s+|\s+$/g, '');
    if (!code) {
        document.querySelector("#recoverVerifyError").innerHTML = "Incomplete Form";
        document.getElementById('recoverVerifyCode').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/recover/verify/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            document.querySelector("#recoverVerificationModalCloseButton").disabled = false;
            document.querySelector("#recoverVerificationModalCloseButton").click();
            document.querySelector("#recoverVerificationModalCloseButton").disabled = true;
            displayChangePasswordModal();
        } else {
            enable_buttons();
            recoverVerifyCode.focus();
            document.querySelector("#recoverVerifyError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('code', code);
    request.send(data);
    return false;
}


function displayChangePasswordModal() {
    const details_template = Handlebars.compile(document.querySelector('#changePasswordHandlebars').innerHTML);
    const details = details_template();
    document.querySelector("#changePasswordModal").innerHTML = details;

    const changePasswordModal = document.getElementById('changePasswordModal');
    const recoverChangePassword = document.getElementById('recoverChangePassword');
    changePasswordModal.addEventListener('shown.bs.modal', () => {
        recoverChangePassword.focus();
    })

    document.querySelector("#changePasswordModalButton").click();
    return;
}


function changepassword(event) {
    event.preventDefault();
    let password1 = document.querySelector("#recoverChangePassword").value.replace(/^\s+|\s+$/g, '');
    let password2 = document.querySelector("#recoverChangePassword1").value.replace(/^\s+|\s+$/g, '');

    if (!password1 || !password2) {
        document.querySelector("#changePasswordError").innerHTML = "Incomplete Form";
        document.getElementById('recoverChangePassword').focus();
        return false;
    }

    if (password1 != password2) {
        document.querySelector("#changePasswordError").innerHTML = "Passwords Don't Match";
        document.getElementById('recoverChangePassword').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/recover/verify/changepassword/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#changePasswordModalCloseButton").disabled = false;
            document.querySelector("#changePasswordModalCloseButton").click();
            document.querySelector("#changePasswordModalCloseButton").disabled = true;
            document.querySelector("#recoverSuccessModalButton").click();
        } else {
            enable_buttons();
            document.getElementById('recoverChangePassword').focus();
            document.querySelector("#changePasswordError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('password2', password2);
    data.append('password1', password1);
    request.send(data);
    return false;
}