function displayRegisterModal(event) {
    event.preventDefault();

    const details_template = Handlebars.compile(document.querySelector('#registerFormHandlebars').innerHTML);
    const details = details_template();
    document.querySelector("#registerModal").innerHTML = details;

    const registerModal = document.getElementById('registerModal');
    const registerFirstName = document.getElementById('registerFirstName');
    registerModal.addEventListener('shown.bs.modal', () => {
        registerFirstName.focus();
    })

    document.querySelector("#displayRegisterModalButton").click();
    return false;
}


function register(event) {
    event.preventDefault();
    let email = document.querySelector("#registerEmail").value.replace(/^\s+|\s+$/g, '');
    let username = document.querySelector("#registerUsername").value.replace(/^\s+|\s+$/g, '');
    let password = document.querySelector("#registerPassword").value.replace(/^\s+|\s+$/g, '');
    let confirmPassword = document.querySelector("#registerConfirmPassword").value.replace(/^\s+|\s+$/g, '');
    let first_name = document.querySelector("#registerFirstName").value.replace(/^\s+|\s+$/g, '');
    let last_name = document.querySelector("#registerLastName").value.replace(/^\s+|\s+$/g, '');

    if (!email || !username || !password || !confirmPassword || !first_name || !last_name) {
        document.querySelector("#registerError").innerHTML = "Incomplete Form";
        document.getElementById('registerFirstName').focus();
        return false;
    }

    if (password != confirmPassword) {
        document.querySelector("#registerError").innerHTML = "Passwords Don't Match";
        registerEmail.focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/register/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            document.querySelector("#registerModalCloseButton").click();
            displayRegisterVerificationModal(res.email);
        } else {
            prevent_default = false;
            enable_buttons();
            document.getElementById('registerFirstName').focus();
            document.querySelector("#registerError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('username', username);
    data.append('email', email);
    data.append('password', password);
    data.append('confirmPassword', confirmPassword);
    data.append('first_name', first_name);
    data.append('last_name', last_name);
    request.send(data);
    return false;
}


function displayRegisterVerificationModal(email) {
    const details_template = Handlebars.compile(document.querySelector('#registerVerificationFormHandlebars').innerHTML);
    const details = details_template({"email": email});
    document.querySelector("#registerVerificationModal").innerHTML = details;
    
    const registerVerificationModal = document.getElementById('registerVerificationModal');
    const registerVerifyCode = document.getElementById('registerVerifyCode');
    registerVerificationModal.addEventListener('shown.bs.modal', () => {
        registerVerifyCode.focus();
    })

    document.querySelector("#registerVerificationModalButton").click();
}

function cancelRegisterVerify() {
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/register/verify/cancel/');
    
    disable_buttons();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            prevent_default = false;
        }
    };
    request.send();
    return false;
}


function registerVerifyCodeResend(event) {
    event.preventDefault();
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/register/verify/resend/');
    disable_buttons();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            document.getElementById('registerVerifyCode').focus();
            document.querySelector("#registerVerifyError").innerHTML = "A new verification code was sent to your email address.";
        } else {
            prevent_default = false;
            enable_buttons();
            document.getElementById('registerVerifyCode').focus();
            document.querySelector("#registerVerifyError").innerHTML = res.message;
        }
    };
    request.send();
    return false;
}

function registerVerify(event) {
    event.preventDefault();
    let code = document.querySelector("#registerVerifyCode").value.replace(/^\s+|\s+$/g, '');
    if (!code) {
        document.querySelector("#registerVerifyError").innerHTML = "Incomplete Form";
        document.getElementById('registerVerifyCode').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/register/verify/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#registerVerificationModalCloseButton").disabled = false;
            document.querySelector("#registerVerificationModalCloseButton").click();
            document.querySelector("#registerVerificationModalCloseButton").disabled = true;
            document.querySelector("#registerSuccessModalButton").click();
        } else {
            if (res.restart) {
                enable_buttons();
                prevent_default = false;
                document.querySelector("#registerVerificationModalCloseButton").disabled = false;
                document.querySelector("#registerVerificationModalCloseButton").click();
                document.querySelector("#registerVerificationModalCloseButton").disabled = true;

                const details_template = Handlebars.compile(document.querySelector('#registerUnsuccessfulModalHandlebars').innerHTML);
                const details = details_template({"message": res.message});
                document.querySelector("#registerUnsuccessModal").innerHTML = details;
                document.querySelector("#registerUnsuccessModalButton").click();
            } else {
                enable_buttons();
                document.getElementById('registerVerifyCode').focus();
                document.querySelector("#registerVerifyError").innerHTML = res.message;
            }
        }
    };

    const data = new FormData();
    data.append('code', code);
    request.send(data);
    return false;
}