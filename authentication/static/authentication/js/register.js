function displayRegisterModal(event) {
    event.preventDefault();
    const details_template = Handlebars.compile(document.querySelector('#registerModalHandlebars').innerHTML);
    const details = details_template();
    document.querySelector("#registerModalDiv").innerHTML = details;
    document.querySelector("#registerModalBtn").click();

    const registerModal = document.getElementById('registerModal')
    const registerFormInputFirstName = document.getElementById('registerFormInputFirstName')
    registerModal.addEventListener('shown.bs.modal', () => {
        registerFormInputFirstName.focus()
    })
}


function register(event) {
    event.preventDefault();
    
    let email = document.querySelector("#registerFormInputEmail").value.replace(/^\s+|\s+$/g, '');
    let username = document.querySelector("#registerFormInputUsername").value.replace(/^\s+|\s+$/g, '');
    let password = document.querySelector("#registerFormInputPassword1").value.replace(/^\s+|\s+$/g, '');
    let confirmPassword = document.querySelector("#registerFormInputPassword2").value.replace(/^\s+|\s+$/g, '');
    let first_name = document.querySelector("#registerFormInputFirstName").value.replace(/^\s+|\s+$/g, '');
    let last_name = document.querySelector("#registerFormInputLastName").value.replace(/^\s+|\s+$/g, '');

    if (!email || !username || !password || !confirmPassword || !first_name || !last_name) {
        document.querySelector("#registerError").innerHTML = "Incomplete Form";
        document.getElementById('registerFormInputFirstName').focus();
        return false;
    }

    if (password != confirmPassword) {
        document.querySelector("#registerError").innerHTML = "Passwords Don't Match";
        document.getElementById('registerFormInputFirstName').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/register/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            document.querySelector("#registerModalCloseButton").click();
            displayVerifyRegistrationModal(res.email, res.validity);
        } else {
            prevent_default = false;
            enable();
            document.querySelector("#registerError").innerHTML = res.message;
            document.getElementById('registerFormInputFirstName').focus();
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


function displayVerifyRegistrationModal(email, validity) {
    const details_template = Handlebars.compile(document.querySelector('#verifyRegistrationEmailModalHandlebars').innerHTML);
    const details = details_template({"email": email});
    document.querySelector("#verifyRegistrationEmailModalDiv").innerHTML = details;
    document.querySelector("#verifyRegistrationEmailModalBtn").click();
    start_countdown(validity, "register_countdown");

    const verifyRegistrationEmailModal = document.getElementById('verifyRegistrationEmailModal')
    const verifyRegistrationEmailCodeInput = document.getElementById('verifyRegistrationEmailCodeInput')
    verifyRegistrationEmailModal.addEventListener('shown.bs.modal', () => {
        verifyRegistrationEmailCodeInput.focus()
    })
    return;
}


function resendVerificationCode_register(event) {
    event.preventDefault();
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/register/verify/resend-code/');
    
    disable();
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            document.getElementById('verifyRegistrationEmailCodeInput').focus();
            document.querySelector("#verifyRegistrationError").innerHTML = "A new verification code was sent to your email address.";
            clearInterval(countDownTimer);
            start_countdown(res.validity, "register_countdown");
        } else {
            prevent_default = false;
            enable();
            clearInterval(countDownTimer);
            document.getElementById('verifyRegistrationEmailCodeInput').focus();
            document.querySelector("#verifyRegistrationError").innerHTML = res.message;
        }
    };
    request.send();
    return false;
}


function cancelregistration() {
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/register/verify/cancel/');
    
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


function verifyRegistrationEmail(event) {
    event.preventDefault();
    let code = document.querySelector("#verifyRegistrationEmailCodeInput").value.replace(/^\s+|\s+$/g, '');

    if (!code) {
        document.querySelector("#verifyRegistrationError").innerHTML = "Incomplete Form";
        document.getElementById('verifyRegistrationEmailCodeInput').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/register/verify/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable();

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable();
            prevent_default = false;
            clearInterval(countDownTimer);
            document.querySelector("#closeBtn_VerifyRegistrationModal").disabled = false;
            document.querySelector("#closeBtn_VerifyRegistrationModal").click();
            document.querySelector("#closeBtn_VerifyRegistrationModal").disabled = true;
            document.querySelector("#registrationSuccessModalBtn").click();
        } else {
            if (res.restart) {
                enable();
                prevent_default = false;
                clearInterval(countDownTimer);
                document.querySelector("#closeBtn_VerifyRegistrationModal").disabled = false;
                document.querySelector("#closeBtn_VerifyRegistrationModal").click();
                document.querySelector("#closeBtn_VerifyRegistrationModal").disabled = true;

                const details_template = Handlebars.compile(document.querySelector('#registerUnsuccessfulModalHandlebars').innerHTML);
                const details = details_template({"message": res.message});
                document.querySelector("#RegistrationUnsuccessfulModalDiv").innerHTML = details;
                document.querySelector("#RegistrationUnsuccessfulModalBtn").click();
            } else {
                enable();
                document.getElementById('verifyRegistrationEmailCodeInput').focus();
                document.querySelector("#verifyRegistrationError").innerHTML = res.message;
            }
        }
    };

    const data = new FormData();
    data.append('code', code);
    request.send(data);
    return false;
}