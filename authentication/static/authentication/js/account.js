document.addEventListener("DOMContentLoaded", ()=>{
    get_user();
});


function get_user() {
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/account/get-user/');
    
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            last_login = new Date(Date.parse(res.user.last_login))
            date_joined = new Date(Date.parse(res.user.date_joined))
            res.user.last_login = last_login.toLocaleString()
            res.user.date_joined = date_joined.toLocaleString()

            const details_template = Handlebars.compile(document.querySelector('#accountDetailsHandlebars').innerHTML);
            const details = details_template(res.user);
            document.querySelector("#userInfo").innerHTML = details;
        } else {
            alert(re.message);
        }
    };
    request.send();
    return false;
}


function displayUpdateDetailsModal(event) {
    event.preventDefault();
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/account/get-user/');
    
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#editAccountDetailsHandlebars').innerHTML);
            const details = details_template(res.user);
            document.querySelector("#editAccountDetailsModalDiv").innerHTML = details;
            document.querySelector("#editAccountDetailsModalBtn").click();

            const editAccountDetailsModal = document.getElementById('editAccountDetailsModal')
            const editAccountDetailsFormInputFirstName = document.getElementById('editAccountDetailsFormInputFirstName')
            editAccountDetailsModal.addEventListener('shown.bs.modal', () => {
                editAccountDetailsFormInputFirstName.focus()
            })
        } else {
            alert(re.message);
        }
    };
    request.send();
    return false;
}


function editDetails(event, user_id) {
    event.preventDefault();
    let first_name = document.querySelector("#editAccountDetailsFormInputFirstName").value.replace(/^\s+|\s+$/g, '');
    let last_name = document.querySelector("#editAccountDetailsFormInputLastName").value.replace(/^\s+|\s+$/g, '');
    let username = document.querySelector("#editAccountDetailsFormInputUsername").value.replace(/^\s+|\s+$/g, '');

    if (!first_name || !last_name || !username) {
        document.querySelector("#editDetailsError").innerHTML = "Incomplete Form";
        document.querySelector("#editAccountDetailsFormInputFirstName").focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/edit-details/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            prevent_default = false;
            enable();
            document.querySelector("#editAccountDetailsModalCloseBtn").click();
            get_user();
        } else {
            enable();
            prevent_default = false;
            document.querySelector("#editAccountDetailsFormInputFirstName").focus();
            document.querySelector("#editDetailsError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('first_name', first_name);
    data.append('last_name', last_name);
    data.append('username', username);
    data.append('user_id', user_id);
    request.send(data);
    return false;
}


function displayUpdateEmailModal(event, user_id) {
    event.preventDefault();
    const details_template = Handlebars.compile(document.querySelector('#editEmailHandlebars').innerHTML);
    const details = details_template({"user_id": user_id});
    document.querySelector("#editEmailModalDiv").innerHTML = details;
    document.querySelector("#editEmailModalBtn").click();

    const editEmailModal = document.getElementById('editEmailModal')
    const editEmailFormInputPassword = document.getElementById('editEmailFormInputPassword')
    editEmailModal.addEventListener('shown.bs.modal', () => {
        editEmailFormInputPassword.focus()
    })
}


function editEmail(event, user_id) {
    event.preventDefault();
    let password = document.querySelector("#editEmailFormInputPassword").value.replace(/^\s+|\s+$/g, '');
    let new_email = document.querySelector("#editEmailFormInputNewEmail").value.replace(/^\s+|\s+$/g, '');

    if (!password) {
        document.querySelector("#editEmailError").innerHTML = "Incomplete Form";
        document.querySelector("#editEmailFormInputPassword").focus();
        return false;
    } else if (!new_email) {
        document.querySelector("#editEmailError").innerHTML = "Incomplete Form";
        document.querySelector("#editEmailFormInputNewEmail").focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/edit-email/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            document.querySelector("#editEmailModalCloseBtn").click();
            displayEditEmailVerificationModal(res.context, res.validity);
        } else {
            enable();
            prevent_default = false;
            document.querySelector("#editEmailFormInputPassword").focus();
            document.querySelector("#editEmailError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('password', password);
    data.append('user_id', user_id);
    data.append('new_email', new_email);
    request.send(data);
    return false;
}


function displayEditEmailVerificationModal(context, validity) {
    const details_template = Handlebars.compile(document.querySelector('#verifyEditEmailHandlebars').innerHTML);
    const details = details_template(context);
    document.querySelector("#verifyEditEmailModalDiv").innerHTML = details;
    document.querySelector("#editEmailVerificationModalBtn").click();

    start_countdown(validity, "editEmail_countdown");

    const editEmailVerificationModal = document.getElementById('editEmailVerificationModal')
    const editEmailVerificationCodeInput = document.getElementById('editEmailVerificationCodeInput')
    editEmailVerificationModal.addEventListener('shown.bs.modal', () => {
        editEmailVerificationCodeInput.focus()
    })
}


function cancelEmailEditing() {

    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/account/edit-email/cancel/');
    
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            prevent_default = false;
            clearInterval(countDownTimer);
        }
    };
    request.send();
    return false;
}


function resendEditEmailVerificationCode(event, new_email) {
    event.preventDefault();
    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/edit-email/verify/resend-code/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            document.querySelector("#editEmailVerificationError").innerHTML = "A new verifiction code was sent to your new email address.";
            document.querySelector("#editEmailVerificationCodeInput").focus();
            clearInterval(countDownTimer);
            start_countdown(res.validity, "editEmail_countdown");
        } else {
            enable();
            clearInterval(countDownTimer);
            prevent_default = false;
            document.querySelector("#editEmailVerificationCodeInput").focus();
            document.querySelector("#editEmailVerificationError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('new_email', new_email);
    request.send(data);
    return false;
}


function editEmailVerification(event, new_email, username, current_email) {
    event.preventDefault();

    let code = document.querySelector("#editEmailVerificationCodeInput").value.replace(/^\s+|\s+$/g, '');
    if (!code) {
        document.querySelector("#editEmailVerificationCodeInput").focus();
        document.querySelector("#editEmailVerificationError").innerHTML = "Incomplete Form";
        return false;
    }
    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/edit-email/verify/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            prevent_default = false;
            document.querySelector("#editEmailVerificationModalCloseBtn").disabled = false;
            document.querySelector("#editEmailVerificationModalCloseBtn").click();
            document.querySelector("#editEmailVerificationModalCloseBtn").disabled = true;
            clearInterval(countDownTimer);
            get_user();
        } else {
            enable();
            document.querySelector("#editEmailVerificationCodeInput").focus();
            document.querySelector("#editEmailVerificationError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('new_email', new_email);
    data.append('code', code);
    data.append('username', username);
    data.append('current_email', current_email);
    request.send(data);
    return false;
}


function displayChangePasswordModal(event, user_id) {
    event.preventDefault();

    const details_template = Handlebars.compile(document.querySelector('#changePasswordHandlebars').innerHTML);
    const details = details_template({"user_id": user_id});
    document.querySelector("#changePasswordModalDiv").innerHTML = details;
    document.querySelector("#changePasswordModalBtn").click();

    const changePasswordModal = document.getElementById('changePasswordModal')
    const changePasswordFormInputCurrentPassword = document.getElementById('changePasswordFormInputCurrentPassword')
    changePasswordModal.addEventListener('shown.bs.modal', () => {
        changePasswordFormInputCurrentPassword.focus()
    })
}


function changepassword(event, user_id) {
    event.preventDefault();
    let current_password = document.querySelector("#changePasswordFormInputCurrentPassword").value.replace(/^\s+|\s+$/g, '');
    let new_password_1 = document.querySelector("#changePasswordFormInputNewPassword1").value.replace(/^\s+|\s+$/g, '');
    let new_password_2 = document.querySelector("#changePasswordFormInputNewPassword2").value.replace(/^\s+|\s+$/g, '');
    if (!current_password || !new_password_1 || !new_password_2) {
        document.querySelector("#changePasswordError").innerHTML = "Incomplete Form";
        document.querySelector("#changePasswordFormInputCurrentPassword").focus();
        return false;
    }

    if (new_password_1 != new_password_2) {
        document.querySelector("#changePasswordError").innerHTML = "New passwords don't match.";
        document.querySelector("#changePasswordFormInputCurrentPassword").focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/change-password/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    prevent_default = true;
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            prevent_default = false;
            document.querySelector("#changePasswordModalCloseBtn").click();
            document.querySelector("#changePasswordSuccessModalBtn").click();
        } else {
            enable();
            prevent_default = false;
            document.querySelector("#changePasswordFormInputCurrentPassword").focus();
            document.querySelector("#changePasswordError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('user_id', user_id);
    data.append('current_password', current_password);
    data.append('new_password_1', new_password_1);
    data.append('new_password_2', new_password_2);
    request.send(data);
    return false;
}


function displayCloseAccountModal(event, user_id) {
    event.preventDefault();
    const details_template = Handlebars.compile(document.querySelector('#closeAccountHandlebars').innerHTML);
    const details = details_template({"user_id": user_id});
    document.querySelector("#closeAccountModalDiv").innerHTML = details;
    document.querySelector("#closeAccountModalBtn").click();

    const closeAccountModal = document.getElementById('closeAccountModal')
    const closeAccountFormInputPassword = document.getElementById('closeAccountFormInputPassword')
    closeAccountModal.addEventListener('shown.bs.modal', () => {
        closeAccountFormInputPassword.focus()
    })
    return false;
}


function closeAccount(event, user_id) {
    event.preventDefault();
    let password = document.querySelector("#closeAccountFormInputPassword").value.replace(/^\s+|\s+$/g, '');

    if (!password) {
        document.querySelector("#closeAccountFormError").innerHTML = "Incomplete Form";
        document.querySelector("#closeAccountFormInputPassword").focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/close/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            document.querySelector("#closeAccountModalCloseBtn").click();
            displayCloseAccountVerificationModal(res.id, res.validity);
        } else {
            enable();
            prevent_default = false;
            document.querySelector("#closeAccountFormInputPassword").focus();
            document.querySelector("#closeAccountFormError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('user_id', user_id);
    data.append('password', password);
    request.send(data);
    return false;
}


function displayCloseAccountVerificationModal(user_id, validity) {
    const details_template = Handlebars.compile(document.querySelector('#closeAccountVarificationHandlebars').innerHTML);
    const details = details_template({"user_id": user_id});
    document.querySelector("#closeAccountVerificationModalDiv").innerHTML = details;
    document.querySelector("#closeAccountVerificationModalBtn").click();

    start_countdown(validity, "closeAccount_countdown");

    const closeAccountVerificationModal = document.getElementById('closeAccountVerificationModal')
    const closeAccountVerificationFormInputCode = document.getElementById('closeAccountVerificationFormInputCode')
    closeAccountVerificationModal.addEventListener('shown.bs.modal', () => {
        closeAccountVerificationFormInputCode.focus()
    })
}


function cancelAccountClosure() {

    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/account/close/cancel/');
    
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            prevent_default = false;
            clearInterval(countDownTimer);
        }
    };
    request.send();
    return false;

}


function resendCloseAccountVerificationCode(event) {
    event.preventDefault();
    
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/account/close/verify/resend-code/');
    
    disable();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            document.querySelector("#closeAccountVerificationFormError").innerHTML = "A new verifiction code was sent to your new email address.";
            document.querySelector("#closeAccountVerificationFormInputCode").focus();
            clearInterval(countDownTimer);
            start_countdown(res.validity, "closeAccount_countdown");
        } else {
            enable();
            clearInterval(countDownTimer);
            prevent_default = false;
            document.querySelector("#closeAccountVerificationFormInputCode").focus();
            document.querySelector("#closeAccountVerificationFormError").innerHTML = res.message;
        }
    };
    
    request.send();
    return false;
}


function close_account(event, user_id) {
    event.preventDefault();

    let code = document.querySelector("#closeAccountVerificationFormInputCode").value.replace(/^\s+|\s+$/g, '');
    if (!code) {
        document.querySelector("#closeAccountVerificationFormError").innerHTML = "Incomplete Form";
        document.querySelector("#closeAccountVerificationFormInputCode").focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/close/verify/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            prevent_default = false;
            clearInterval(countDownTimer);
            document.querySelector("#closeAccountVerificationModalCloseBtn").disabled = false;
            document.querySelector("#closeAccountVerificationModalCloseBtn").click();
            document.querySelector("#closeAccountVerificationModalCloseBtn").disabled = true;
            location.reload();
        } else {
            enable();
            document.querySelector("#closeAccountVerificationFormError").innerHTML = res.message;
            document.querySelector("#closeAccountVerificationFormInputCode").focus();
        }
    };

    const data = new FormData();
    data.append('user_id', user_id);
    data.append('code', code);
    request.send(data);
    return false;
}