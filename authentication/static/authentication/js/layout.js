var prevent_default = false;
var countDownTimer;
window.addEventListener('beforeunload', function (e) {
    if (prevent_default) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to cancel this process?';
    }
    return;
});


function disable() {
    document.querySelectorAll(".disableButton").forEach(b => {
        b.disabled = true;
    });

    document.querySelectorAll(".disableAnchorTag").forEach(a => {
        a.style.pointerEvents="none";
        a.style.cursor="default";
    });

    document.querySelectorAll(".spinner-border").forEach(s => {
        s.hidden = false;
    });
}


function enable() {
    document.querySelectorAll(".disableButton").forEach(b => {
        b.disabled = false;
    });

    document.querySelectorAll(".disableAnchorTag").forEach(a => {
        a.style.pointerEvents="auto";
        a.style.cursor="pointer";
    });

    document.querySelectorAll(".spinner-border").forEach(s => {
        s.hidden = true;
    });
}


function start_countdown(validity, countdownID) {
    var countDownTime = new Date(`${validity}Z`).getTime();
    countDownTimer = setInterval(function() {
        var now = new Date().getTime();
        var distance = countDownTime - now;
        var minutes = Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
        var seconds = Math.floor((distance % (1000 * 60)) / 1000);

        document.getElementById(countdownID).innerHTML = minutes + "m " + seconds + "s ";
        if (distance < 0) {
            clearInterval(countDownTimer);
            document.getElementById(countdownID).innerHTML = "EXPIRED";
        }
    }, 1000);
}


function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}