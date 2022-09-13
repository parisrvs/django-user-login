function displayRecoverModal(event) {
    event.preventDefault();
    const details_template = Handlebars.compile(document.querySelector('#recoverModalHandlebars').innerHTML);
    const details = details_template();
    document.querySelector("#recoverModalDiv").innerHTML = details;
    document.querySelector("#recoverModalBtn").click();

    const recoverModal = document.getElementById('recoverModal')
    const recoverFormInputText = document.getElementById('recoverFormInputText')
    recoverModal.addEventListener('shown.bs.modal', () => {
        recoverFormInputText.focus()
    })
}


function recover(event) {
    event.preventDefault();
    let email = document.querySelector("#recoverFormInputText").value.replace(/^\s+|\s+$/g, '');
    if (!email) {
        document.querySelector("#recoverError").innerHTML = "Incomplete Form";
        document.getElementById('recoverFormInputText').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/recover/');
    request.setRequestHeader("X-CSRFToken", csrftoken);
    
    disable();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            document.querySelector("#recoverModalCloseButton").click();
            displayRecoverVerificationModal(res.email, res.validity);
        } else {
            prevent_default = false;
            enable();
            document.getElementById('recoverFormInputText').focus();
            document.querySelector("#recoverError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('email', email);
    request.send(data);
    return false;
}


function displayRecoverVerificationModal(email, validity) {
    const details_template = Handlebars.compile(document.querySelector('#verifyRecoveryEmailModalHandlebars').innerHTML);
    const details = details_template({"email": email});
    document.querySelector("#verifyRecoveryEmailModalDiv").innerHTML = details;
    document.querySelector("#recoveryEmailVerificationModalBtn").click();
    start_countdown(validity, "recover_countdown");

    const recoveryEmailVerificationModal = document.getElementById('recoveryEmailVerificationModal')
    const verifyRecoveryEmailCodeInput = document.getElementById('verifyRecoveryEmailCodeInput')
    recoveryEmailVerificationModal.addEventListener('shown.bs.modal', () => {
        verifyRecoveryEmailCodeInput.focus()
    })
}


function cancelRecovery() {
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/recover/verify/cancel/');
    
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            clearInterval(countDownTimer);
            prevent_default = false;
        }
    };
    request.send();
    return false;
}


function resendVerificationCode_recover(event) {
    event.preventDefault();
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/recover/verify/resend-code/');
    disable();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            clearInterval(countDownTimer);
            start_countdown(res.validity, "recover_countdown");
            document.getElementById('verifyRecoveryEmailCodeInput').focus();
            document.querySelector("#verifyRecoveryError").innerHTML = "A new verification code was sent to your email address.";
        } else {
            prevent_default = false;
            enable();
            clearInterval(countDownTimer);
            document.getElementById('verifyRecoveryEmailCodeInput').focus();
            document.querySelector("#verifyRecoveryError").innerHTML = res.message;
        }
    };
    request.send();
    return false;
}


function verifyRecoveryEmail(event) {
    event.preventDefault();
    let code = document.querySelector("#verifyRecoveryEmailCodeInput").value.replace(/^\s+|\s+$/g, '');
    if (!code) {
        document.querySelector("#verifyRecoveryError").innerHTML = "Incomplete Form";
        document.getElementById('verifyRecoveryEmailCodeInput').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/recover/verify/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            clearInterval(countDownTimer);
            document.querySelector("#closeBtn_VerifyRecoveryModal").disabled = false;
            document.querySelector("#closeBtn_VerifyRecoveryModal").click();
            document.querySelector("#closeBtn_VerifyRecoveryModal").disabled = true;
            displayChangePasswordModal();
        } else {
            enable();
            document.querySelector("#verifyRecoveryError").innerHTML = res.message;
            document.getElementById('verifyRecoveryEmailCodeInput').focus();
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
    document.querySelector("#passwordChangeModalDiv").innerHTML = details;
    document.querySelector("#changePasswordModalButton").click();

    const changePasswordModal = document.getElementById('changePasswordModal')
    const recoverChangePassword = document.getElementById('recoverChangePassword')
    changePasswordModal.addEventListener('shown.bs.modal', () => {
        recoverChangePassword.focus()
    })
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
    request.open('POST', '/authentication/recover/verify/change-password/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
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