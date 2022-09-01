var prevent_default = false;
window.addEventListener('beforeunload', function (e) {
    if (prevent_default) {
        e.preventDefault();
        e.returnValue = 'Are you sure you want to cancel this process?';
    }
    return;
});

function disable_buttons() {
    document.querySelectorAll('.toDisable').forEach(b => {
        b.disabled = true;
    });
    document.querySelectorAll(".spinner-border").forEach(s => {
        s.hidden = false;
    });
    document.querySelectorAll(".toDisableAnchorTag").forEach(a => {
        a.style.pointerEvents="none";
        a.style.cursor="default";
    });
}

function enable_buttons() {
    document.querySelectorAll('.toDisable').forEach(b => {
        b.disabled = false;
    });
    document.querySelectorAll(".spinner-border").forEach(s => {
        s.hidden = true;
    });
    document.querySelectorAll(".toDisableAnchorTag").forEach(a => {
        a.style.pointerEvents="auto";
        a.style.cursor="pointer";
    });
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