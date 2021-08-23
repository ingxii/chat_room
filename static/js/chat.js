var current_user = 0;
var welcome = ''; //可以用来保持当前聊天室ID
var user_name = ''; //可以用来保持当前聊天室ID

var chat = {
    initScroller: function() {
        // 初始化滚动
        window.myScroll = new IScroll('#wrapper', {
            // topOffset: 50,
            probeType: 3,
            click: true,
            mouseWheel: true,
            checkDOMChanges: true,
            // bounceLock: true,
            bounce: true,
            disablePointer: true,
            // disableTouch:false,
            // disableMouse:false,
        });


    },
    initSock: function() {
        //
        var url = "ws://" + location.host + "/chatsocket";
        SOCK.init(url);
        SOCK.on_open = function(message) {
            var rooms = $('.content li[room_id]');
            if (rooms) {
                for (index = 0; index < rooms.length; index++) {
                    element = rooms[index];

                    var room_id = int(element.getAttribute('room_id'));
                    if (room_id) {
                        SOCK.send("history", '0', room_id); // enter消息强行进入房间,并且获取历史消息
                    }
                }

            }
        };
        SOCK.on_close = function(message) {
            console.warn('断开连接');
        };
        SOCK.on_message = function(message) {
            console.log(message);
            if (typeof message.body != 'string' || message.body.length == 0) {
                console.warn('消息体为空');
                return false;
            }

            message.id = int(message.id); //
            message.from = int(message.from); //
            message.addtime = int(message.addtime); //
            message.body = string(message.body); //
            message.username = string(message.username); //
            message.headimgurl = string(message.headimgurl); //
            message.type = string(message.type); //

            if (message.username.length == 0) {
                message.username = message.from > 0 ? '[匿名用户]' : '[系统消息]';
            }


            // 房间是否已经存在
            if (chat.checkRoom(message.to)) {
                // return false;
            } else {
                chat.createRoom(message);
            }

            chat.update_room(message);

        }

    },
    checkRoom: function(room_id) {
        var t = $("[room_id=" + room_id + "]");
        if (room_id > 0 && t && t.length > 0) {
            return t[0];
        }
        return false;
    },

    createRoom: function(message) {
        var list = $('<li class="tr" room_id="' + message.to + '"><span class="td c_head"><img src="/static/images/head_default.png"></span><span class="td c_body"><a href="/room?id=' + message.to + '"><div class="head">' + message.username + '</div><div class="body"></div></a></span><span class="td c_foot "><div class="msg_hint" ></div></span></li>');

        $('ul.content').append(list);

        return list[0];
    },

    update_room: function(message) {
        var room = chat.checkRoom(message.to);
        if (!room) {
            return;
        }

        // 为了计算node_content的宽度移到这里
        switch (message.type) {
            case 'enter':
                // 客服的自动回复消息
                if (string(welcome).length > 0 && int(message.from) != int(current_user)) {
                    welcome = welcome.replace(/\[c\]/g, message.username);
                    welcome = welcome.replace(/\[s\]/g, user_name);
                    SOCK.send('text', welcome, message.to);
                }
                return;

            case 'image':
            case 'text':
                // 新消息数提醒
                var msg_hint = room.querySelector('.msg_hint');
                var msg_body = room.querySelector('.body');

                if (message.type == 'image') {
                    msg_body.innerText = message.username + ':[图片]'
                } else {
                    msg_body.innerText = message.username + ':' + message.body;
                }

                // 自己发送的消息(如客服消息),不计数
                if (message.from && message.from != current_user && message.id > getStorage(message.to, 0)) {
                    // getStorage(message.to)表示当前房间已经保存的消息ID
                    var num = int(msg_hint.innerText);
                    msg_hint.innerText = Math.min(++num, 99);
                    if (num > 0) {
                        msg_hint.style.display = 'block';
                    }

                }

                break;
            default:
                return;
        }
    },

};

function loaded() {
    console.log('loaded');
    current_user = $("#current_user").val();
    welcome = $("#welcome").val();
    user_name = $("#user_name").val();

    chat.initSock();
    chat.initScroller();
}