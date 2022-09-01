document.addEventListener("DOMContentLoaded", ()=>{
    load();
});


function load() {
    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#PersonDetailsHandlebars').innerHTML);
            const details = details_template(res.user);
            document.querySelector("#userdetails").innerHTML = details;
        } else {
            location.reload();
        }
    };

    request.send();
    return false;
}


function triggerEditDetailsFormModal(event, user_id, person_id) {
    event.preventDefault();

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/getUser/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#editPersonalDetailsHandlebars').innerHTML);
            const details = details_template(res.user);
            document.querySelector("#editPersonalDetailsModal").innerHTML = details;
            document.querySelector("#triggerEditPersonalDetailsModalBtn").click();
            
            const editPersonalDetailsModal = document.getElementById('editPersonalDetailsModal')
            const editDetailsFirstName = document.getElementById('editDetailsFirstName')
            editPersonalDetailsModal.addEventListener('shown.bs.modal', () => {
                editDetailsFirstName.focus();
            })
        } else {
            alert("Invalid Request");
        }
    };

    const data = new FormData();
    data.append('user_id', user_id);
    data.append('person_id', person_id);
    request.send(data);
    return false;
}


function editPersonalDetails(event, user_id, person_id) {
    event.preventDefault();

    let first_name = document.querySelector("#editDetailsFirstName").value.replace(/^\s+|\s+$/g, '');
    let last_name = document.querySelector("#editDetailsLastName").value.replace(/^\s+|\s+$/g, '');
    let mobile = document.querySelector("#editDetailsMobile").value.replace(/^\s+|\s+$/g, '');
    let username = document.querySelector("#editDetailsUsername").value.replace(/^\s+|\s+$/g, '');
    let gender = document.querySelector("#editDetailsGender").value;
    let birth_day = document.querySelector("#editDetailsDOB").value;

    if (!first_name || !last_name | !username) {
        document.querySelector("#editDetailsError").innerHTML = "Incomplete Form";
        document.getElementById('editDetailsFirstName').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/editUser/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#editPersonalDetailsModalCloseBtn").click();
            load();
        } else {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#editDetailsError").innerHTML = res.message;
            document.getElementById('editDetailsFirstName').focus();
        }
    };

    const data = new FormData();
    data.append('user_id', user_id);
    data.append('person_id', person_id);
    data.append('first_name', first_name);
    data.append('last_name', last_name);
    data.append('mobile', mobile);
    data.append('username', username);
    data.append('gender', gender);
    data.append('birth_day', birth_day);
    request.send(data);
    return false;
}



function triggerAddAddressFormModal(event, user_id, person_id) {
    event.preventDefault();
    const details_template = Handlebars.compile(document.querySelector('#addAddressHandlebars').innerHTML);
    const details = details_template({"user_id": user_id, "person_id": person_id});
    document.querySelector("#addAddressModal").innerHTML = details;

    const addAddressModal = document.getElementById('addAddressModal')
    const addAddressFirstName = document.getElementById('addAddressFirstName')
    addAddressModal.addEventListener('shown.bs.modal', () => {
        addAddressFirstName.focus();
    })

    document.querySelector("#displayAddAddressModalButton").click();
    return false;
}


function add_address(event, user_id, person_id) {
    event.preventDefault();
    let first_name = document.querySelector("#addAddressFirstName").value.replace(/^\s+|\s+$/g, '');
    let last_name = document.querySelector("#addAddressLastName").value.replace(/^\s+|\s+$/g, '');
    let email = document.querySelector("#addAddressEmail").value.replace(/^\s+|\s+$/g, '');
    let mobile = document.querySelector("#addAddressMobile").value.replace(/^\s+|\s+$/g, '');
    let address1 = document.querySelector("#addAddressAddress1").value.replace(/^\s+|\s+$/g, '');
    let address2 = document.querySelector("#addAddressAddress2").value.replace(/^\s+|\s+$/g, '');
    let city = document.querySelector("#addAddressCity").value.replace(/^\s+|\s+$/g, '');
    let state = document.querySelector("#addAddressState").value.replace(/^\s+|\s+$/g, '');
    let pincode = document.querySelector("#addAddressPincode").value.replace(/^\s+|\s+$/g, '');
    let country = document.querySelector("#addAddressCountry").value.replace(/^\s+|\s+$/g, '');
    let landmark = document.querySelector("#addAddressLandmark").value.replace(/^\s+|\s+$/g, '');
    let homephone = document.querySelector("#addAddressHomephone").value.replace(/^\s+|\s+$/g, '');

    if (!first_name | !last_name || !email || !mobile || !address1 || !city || !state || !pincode || !country || !landmark) {
        document.querySelector("#addAddressError").innerHTML = "Incomplete Form";
        document.getElementById('addAddressFirstName').focus();
        return false;
    }
    disable_buttons();
    prevent_default = true;

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/addAddress/');
    request.setRequestHeader("X-CSRFToken", csrftoken);
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#addAddressModalCloseBtn").click();
            load();
        } else {
            enable_buttons();
            prevent_default = false;
            document.getElementById('addAddressFirstName').focus();
            document.querySelector("#addAddressError").innerHTML = res.message;
        }
    };

    const data = new FormData();
    data.append('first_name', first_name);
    data.append('last_name', last_name);
    data.append('email', email);
    data.append('mobile', mobile);
    data.append('address1', address1);
    data.append('city', city);
    data.append('state', state);
    data.append('pincode', pincode);
    data.append('country', country);
    data.append('landmark', landmark);
    data.append('address2', address2);
    data.append('homephone', homephone);
    data.append('user_id', user_id);
    data.append('person_id', person_id);
    request.send(data);
    return false;
}


function triggerEditAddress(event, address_id, user_id, person_id) {
    console.log(user_id, person_id);
    event.preventDefault();

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/getAddress/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            const details_template = Handlebars.compile(document.querySelector('#editAddressHandlebars').innerHTML);
            const details = details_template(res.address);
            document.querySelector("#editAddressModal").innerHTML = details;
            
            const editAddressModal = document.getElementById('editAddressModal')
            const editAddressFirstName = document.getElementById('editAddressFirstName')
            editAddressModal.addEventListener('shown.bs.modal', () => {
                editAddressFirstName.focus();
            })

            document.querySelector("#triggerEditAddressModalBtn").click();
        } else {
            alert("Invalid Request");
        }
    };

    const data = new FormData();
    data.append('address_id', address_id);
    data.append('user_id', user_id);
    data.append('person_id', person_id);
    request.send(data);
    return false;
}


function editAddress(event, address_id, user_id, person_id) {
    event.preventDefault();
    let first_name = document.querySelector("#editAddressFirstName").value.replace(/^\s+|\s+$/g, '');
    let last_name = document.querySelector("#editAddressLastName").value.replace(/^\s+|\s+$/g, '');
    let email = document.querySelector("#editAddressEmail").value.replace(/^\s+|\s+$/g, '');
    let mobile = document.querySelector("#editAddressMobile").value.replace(/^\s+|\s+$/g, '');
    let address1 = document.querySelector("#editAddressAddress1").value.replace(/^\s+|\s+$/g, '');
    let address2 = document.querySelector("#editAddressAddress2").value.replace(/^\s+|\s+$/g, '');
    let city = document.querySelector("#editAddressCity").value.replace(/^\s+|\s+$/g, '');
    let state = document.querySelector("#editAddressState").value.replace(/^\s+|\s+$/g, '');
    let pincode = document.querySelector("#editAddressPincode").value.replace(/^\s+|\s+$/g, '');
    let country = document.querySelector("#editAddressCountry").value.replace(/^\s+|\s+$/g, '');
    let landmark = document.querySelector("#editAddressLandmark").value.replace(/^\s+|\s+$/g, '');
    let homephone = document.querySelector("#editAddressHomephone").value.replace(/^\s+|\s+$/g, '');

    if (!first_name | !last_name || !email || !mobile || !address1 || !city || !state || !pincode || !country || !landmark) {
        document.querySelector("#editAddressError").innerHTML = "Incomplete Form";
        document.getElementById('editAddressFirstName').focus();
        return false;
    }
    disable_buttons();
    prevent_default = true;

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/editAddress/');
    request.setRequestHeader("X-CSRFToken", csrftoken);
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#editAddressModalCloseBtn").click();
            load();
        } else {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#editAddressError").innerHTML = res.message;
            document.getElementById('editAddressFirstName').focus();
        }
    };

    const data = new FormData();
    data.append('address_id', address_id);
    data.append('first_name', first_name);
    data.append('last_name', last_name);
    data.append('email', email);
    data.append('mobile', mobile);
    data.append('address1', address1);
    data.append('city', city);
    data.append('state', state);
    data.append('pincode', pincode);
    data.append('country', country);
    data.append('landmark', landmark);
    data.append('address2', address2);
    data.append('homephone', homephone);
    data.append('user_id', user_id);
    data.append('person_id', person_id);
    request.send(data);
    return false;
}


function deleteAddress(event, address_id, user_id, person_id) {
    event.preventDefault();
    let c = confirm("Are you sure?");
    if (c) {
        const csrftoken = getCookie('csrftoken');
        const request = new XMLHttpRequest();
        request.open('POST', '/authentication/account/deleteAddress/');
        request.setRequestHeader("X-CSRFToken", csrftoken);

        disable_buttons();
        prevent_default = true;
        let s = document.querySelector(`#deleteAddressAnchorTagSpinner${address_id}`);
        s.hidden = false;
        request.onload = () => {
            const res = JSON.parse(request.responseText);
            if (res.success) {
                enable_buttons();
                s.hidden = true;
                prevent_default = false;
                load();
            } else {
                enable_buttons();
                s.hidden = true;
                prevent_default = false;
                alert(res.message);
            }
        };

        const data = new FormData();
        data.append('address_id', address_id);
        data.append('user_id', user_id);
        data.append('person_id', person_id);
        request.send(data);
    }
    return false;
}


function triggerEmailAddressEditing(event, email, user_id, person_id) {
    event.preventDefault();

    const details_template = Handlebars.compile(document.querySelector('#editEmailHandlebars').innerHTML);
    const details = details_template({
        "email": email,
        "user_id": user_id,
        "person_id": person_id
    });
    document.querySelector("#editEmailModal").innerHTML = details;
    document.querySelector("#triggereditEmailModalBtn").click();
    
    const editEmailModal = document.getElementById('editEmailModal')
    const editEmailNew = document.getElementById('editEmailNew')
    editEmailModal.addEventListener('shown.bs.modal', () => {
        editEmailNew.focus();
    })

    return false;
}


function editEmailAddress(event, email, user_id, person_id) {
    event.preventDefault();
    let current_email = document.querySelector("#editEmailCurrent").value;
    let new_email = document.querySelector("#editEmailNew").value.replace(/^\s+|\s+$/g, '');
    let password = document.querySelector("#editEmailPassword").value.replace(/^\s+|\s+$/g, '');

    if (!current_email || !new_email || !password || current_email != email) {
        document.querySelector("#editEmailError").innerHTML = "Incomplete Form";
        document.getElementById('editEmailNew').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/editEmail/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            document.querySelector("#editEmailModalCloseButton").click();
            displayEditEmailVerifyModal(new_email, user_id, person_id);
        } else {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#editEmailError").innerHTML = res.message;
            document.getElementById('editEmailNew').focus();
        }
    };

    const data = new FormData();
    data.append('user_id', user_id);
    data.append('person_id', person_id);
    data.append('email', email);
    data.append('new_email', new_email);
    data.append('password', password);
    
    request.send(data);
    return false;
}


function displayEditEmailVerifyModal(email, user_id, person_id) {
    const details_template = Handlebars.compile(document.querySelector('#editEmailVerifyHandlebars').innerHTML);
    const details = details_template({"user_id": user_id, "person_id": person_id, "email": email});
    document.querySelector("#editEmailVerifyModal").innerHTML = details;

    const editEmailVerifyModal = document.getElementById('editEmailVerifyModal')
    const editEmailVerifyCode = document.getElementById('editEmailVerifyCode')
    editEmailVerifyModal.addEventListener('shown.bs.modal', () => {
        editEmailVerifyCode.focus();
    })

    document.querySelector("#triggereditEditEmailVerifyModalBtn").click();
    return;
}


function cancelEditEmailVerify() {
    const request = new XMLHttpRequest();
    request.open('GET', '/authentication/account/editEmail/cancel/');
    
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            prevent_default = false;
        }
    };
    request.send();
    return false;
}


function editEmailVerifyCodeResend(event, user_id, person_id, new_email) {
    event.preventDefault();

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/editEmail/ResendCode/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            document.querySelector("#editEmailVerifyError").innerHTML = "A new verification code is sent to your email address.";
            document.getElementById('editEmailVerifyCode').focus();
        } else {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#editEmailVerifyError").innerHTML = res.message;
            document.getElementById('editEmailVerifyCode').focus();
        }
    };

    const data = new FormData();
    data.append('user_id', user_id);
    data.append('person_id', person_id);
    data.append('new_email', new_email);
    
    request.send(data);
    return false;
}

function editEmailVerify(event, user_id, person_id, new_email) {
    event.preventDefault();
    let code = document.querySelector("#editEmailVerifyCode").value.replace(/^\s+|\s+$/g, '');

    if (!code) {
        document.querySelector("#editEmailVerifyError").innerHTML = "Incomplete Form";
        document.getElementById('editEmailVerifyCode').focus();
        return false;
    }
    
    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/editEmail/verify/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#editEmailVerifyModalCloseButton").disabled = false;
            document.querySelector("#editEmailVerifyModalCloseButton").click();
            document.querySelector("#editEmailVerifyModalCloseButton").disabled = true;
            load();
        } else {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#editEmailVerifyError").innerHTML = res.message;
            document.getElementById('editEmailVerifyCode').focus();
        }
    };

    const data = new FormData();
    data.append('user_id', user_id);
    data.append('person_id', person_id);
    data.append('new_email', new_email);
    data.append('code', code);

    request.send(data);
    return false;
}


function displayUpdatePasswordModal(event, user_id) {
    event.preventDefault();

    const details_template = Handlebars.compile(document.querySelector('#updatePasswordHandlebars').innerHTML);
    const details = details_template({"user_id": user_id});
    document.querySelector("#updatePasswordModal").innerHTML = details;

    const updatePasswordModal = document.getElementById('updatePasswordModal')
    const updatePasswordCurrent = document.getElementById('updatePasswordCurrent')
    updatePasswordModal.addEventListener('shown.bs.modal', () => {
        updatePasswordCurrent.focus();
    })

    document.querySelector("#updatePasswordModalButton").click();
    return;
}

function updatepassword(event, user_id) {
    event.preventDefault();

    let current_password = document.querySelector("#updatePasswordCurrent").value.replace(/^\s+|\s+$/g, '');
    let new_password = document.querySelector("#updatePasswordNew").value.replace(/^\s+|\s+$/g, '');
    let new_password1 = document.querySelector("#updatePasswordNew1").value.replace(/^\s+|\s+$/g, '');

    if (!current_password || !new_password || !new_password1) {
        document.querySelector("#updatePasswordError").innerHTML = "Incomplete Form";
        document.getElementById('updatePasswordCurrent').focus();
        return false;
    }

    if (new_password != new_password1) {
        document.querySelector("#updatePasswordError").innerHTML = "Passwords Don't Match";
        document.getElementById('updatePasswordCurrent').focus();
        return false;
    }

    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/updatepassword/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;

    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#updatePasswordModalCloseButton").click();
            document.querySelector("#updatePasswordSuccessModalButton").click();
        } else {
            enable_buttons();
            prevent_default = false;
            document.querySelector("#updatePasswordError").innerHTML = res.message;
            document.getElementById('updatePasswordCurrent').focus();
        }
    };

    const data = new FormData();
    data.append('user_id', user_id);
    data.append('current_password', current_password);
    data.append('new_password', new_password);
    data.append('new_password1', new_password1);

    request.send(data);
    return false;

}


function makeAddressPrimary(event, address_id ,user_id, person_id) {
    event.preventDefault();
    const csrftoken = getCookie('csrftoken');
    const request = new XMLHttpRequest();
    request.open('POST', '/authentication/account/makeAddressPrimary/');
    request.setRequestHeader("X-CSRFToken", csrftoken);

    disable_buttons();
    prevent_default = true;
    let s = document.querySelector(`#makeAddressPrimaryAnchorTagSpinner${address_id}`);
    s.hidden = false;
    request.onload = () => {
        const res = JSON.parse(request.responseText);
        if (res.success) {
            enable_buttons();
            s.hidden = true;
            prevent_default = false;
            load();
        } else {
            enable_buttons();
            s.hidden = true;
            prevent_default = false;
            alert(res.message);
        }
    };

    const data = new FormData();
    data.append('address_id', address_id);
    data.append('user_id', user_id);
    data.append('person_id', person_id);
    request.send(data);
    return false;
}

