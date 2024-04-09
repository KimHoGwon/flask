var vali_message = {
    title: {
        none: "제목을 입력해 주세요.",
    },
    content: {
        none: "내용을 입력해 주세요."
    }
};

function notice_submit() {
    for (var div of document.querySelectorAll('div.vali')) { div.remove(); }
    var submit_ok = true;
    var form = document.querySelector("form[role='form']");

    for (var element of form) {
        if (!element.value) {
            make_message_span(element, vali_message[element.name].none);
            submit_ok = false;
            continue;
        }

        switch (element.name) {
            case "title":
                if (element.value.length > 30) {
                    make_message_span(element, vali_message[element.name].length);
                    submit_ok = false;
                }
                break;
        }
    }
    return submit_ok;
}

function make_message_span(target, message) {
    var div = document.createElement('div');
    div.classList.add("vali");

    var span = document.createElement('span');
    span.style.color = 'red';
    span.innerHTML = message;

    div.append(span);

    target.after(div);
}

document.querySelector("button[btn-role='delete']").onclick = function (event) {
    var btn = event.currentTarget;

    $.ajax({
        url: "/notice/notice.id" + notice.id + "/delete",
        method: "post",
        success: function (url) {
            location.href = url;
        }
    });
}
