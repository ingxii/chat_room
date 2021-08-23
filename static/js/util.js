function createElement(node, cls, name) {
    var div = document.createElement(node);
    div.setAttribute(cls, name);
    return div;
}


function int(params) {
    return +params || 0;
}

function string(params) {
    return typeof params == 'string' ? params : '';
}

function todatetime(timestamp) {
    timestamp = +timestamp || 0;
    var date = new Date(timestamp * 1000); //如果date为13位不需要乘1000
    var Y = date.getFullYear() + '-';
    var M = (date.getMonth() + 1 < 10 ? '0' + (date.getMonth() + 1) : date.getMonth() + 1) + '-';
    var D = (date.getDate() < 10 ? '0' + (date.getDate()) : date.getDate()) + ' ';
    var h = (date.getHours() < 10 ? '0' + date.getHours() : date.getHours()) + ':';
    var m = (date.getMinutes() < 10 ? '0' + date.getMinutes() : date.getMinutes()) + ':';
    var s = (date.getSeconds() < 10 ? '0' + date.getSeconds() : date.getSeconds());
    return Y + M + D + h + m + s;
}


var http = function(param) { return this; };
http.post = function(tarUrl, param, callback, prog) {
    var me = {};

    // FormData 对象
    var form = new FormData();
    for (var key in param) {
        form.append(key, param[key]);
    };

    if (prog) {
        prog.style.display = 'block';
    }

    var xhr = new XMLHttpRequest();
    xhr.onload = function(d) {
        if (prog) {
            prog.style.display = 'none';
        }

        if (xhr.status == 200) {

            res = JSON.parse(this.responseText);
            if (res.status) {
                if (callback) {
                    return callback(res)
                };
            } else {
                console.log(res);
                alert("发送失败")
            }
        } else {
            alert("发送异常")
        }

        return callback()
    };

    if (prog) {
        prog.callback = function(event) {
            if (event.lengthComputable) {
                prog.style.display = 'block';
                prog.max = event.total;
                prog.value = event.loaded;
            }
        };
        xhr.upload.addEventListener("progress", prog.callback, false);
    } else {
        console.log('没有进度条');
    }

    xhr.open("POST", tarUrl, true);
    xhr.send(form);

};

function show_notice(text, href = 'javascript:;') {
    var notice = document.querySelector('#msg_notice');
    var link = document.querySelector('#msg_notice a');
    if (!notice || !link) {
        return;
    }     

    link.innerHTML = text;
    link.setAttribute('href', href);

    notice.style.display = 'block';

    if (notice.timer) {
        clearTimeout(notice.timer);
        notice.timer = null;
    }

    notice.timer = setTimeout(() => {
        notice.style.display = 'none';
    }, 5000);
}

function setStorage(name, value) {
    if (window.localStorage) {
        window.localStorage[name] = value;
    }
}

function getStorage(name, def = null) {
    if (window.localStorage && window.localStorage[name]) {
        return window.localStorage[name];
    }
    return def;
}