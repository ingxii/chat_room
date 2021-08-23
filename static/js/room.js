var current_room = 0; //可以用来保持当前聊天室ID
var current_user = 0; //可以用来保持当前聊天室ID
var user_name = ''; //可以用来保持当前聊天室ID
var welcome = ''; //可以用来保持当前聊天室ID
var _minid = 0; // 保存最小的消息ID 用来获取历史消息
var scroll_y = 0;
// document.addEventListener('touchmove', function(e) { e.preventDefault(); }, false);


var room = {
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

        // 监控滚动区域的滚动
        myScroll.on('scrollEnd', function() {
            // console.log(myScroll)
            myScroll.refresh();


            var y = this.y >> 0; //取整
            if (y == 0 && SOCK) {

                // 获取最小的msg_id
                var nodes = $("[msg_id]");
                var minid = 0;
                for (index = 0; index < nodes.length; index++) {
                    var t = $(nodes[index]).attr('msg_id');
                    if (t > 0) {
                        minid = minid?Math.min(t, minid):t;
                    }
                }
                console.log("加载历史消息:", minid);
                // show_loading();
                if (minid > 0) {
                    console.log("加载历史消息:", minid);
                    SOCK.send('history', minid)
                }
            }
        });

        myScroll.on('scroll', function() {
            var y = this.y >> 0;
            console.log(y + "/" + myScroll.scrollerHeight);
        });

        myScroll.timer_refresh = null;
        myScroll.scrollToEnd = function() {

            if (myScroll.timer_refresh) {
                clearTimeout(myScroll.timer_refresh);
                myScroll.timer_refresh = null;
            }

            myScroll.timer_refresh = setTimeout(function() {
                myScroll.refresh();

                var node = $("[msg_id]:last");
                if (node.length > 0) {
                    // console.log(node[0]);
                    myScroll.scrollToElement(node[0], 100);
                }
            }, 0);
        };
    },

    initSock: function() {
        //
        var url = "ws://" + location.host + "/chatsocket";
        SOCK.init(url, current_room);
        SOCK.on_open = function(message) {
            // enter 的作用:强制进入房间,返回历史消息
            SOCK.send("enter", '1');
        };
        SOCK.on_close = function(message) {
            message = {};
            message.type = 'text';
            message.body = "<a href='javascript:window.location.reload()'>聊天已经断开, 点击重新连接</a>";
            SOCK.on_message(message);
        };
        SOCK.on_message = function(message) {
            console.log(message);

            if (typeof message.body != 'string' || message.body.length == 0) {
                console.warn('消息体为空');
                return false;
            }

            message.id = int(message.id); //
            message.from = int(message.from); //
            message.to = int(message.to); //
            message.addtime = int(message.addtime); //
            message.body = string(message.body); //
            message.username = string(message.username); //
            message.headimgurl = string(message.headimgurl); //
            message.type = string(message.type); //

            if (message.username.length == 0) {
                message.username = message.from > 0 ? '[匿名用户]' : '[系统消息]';
            }


            // 是否有重复的消息
            if (room.checkNode(message.id)) {
                return false;
            }

            room.add_node(message);

            // 是否在底部
            var is_bottom = myScroll.scrollerHeight == myScroll.wrapperHeight - myScroll.y >> 0;
            //在底部时候才会自动滚动
            if (is_bottom) {
                myScroll.scrollToEnd();
            }
        }

    },

    initEvent: function() {
        // 初始化消息发送
        $("#tb_send").click(function() {
            var text = $("#message").val();
            if (text.length == 0) return;
            SOCK.send("text", text.substr(0, 200));

            $('#message').select();
            $('#message').focus();
            $("#message").val("");
            input_change(0);
            $('#expressions ').hide();
        });

        $('#tb_express').click(function(e) {
            $('#expressions ').toggle();

        });

        $('#expressions li.td').click(function(e) {
            var id = $(this).attr('id') ? '[' + $(this).attr('id') + ']' : '';
            var text = $('#message').val() || '';
            console.log(text + '+' + id);
            $('#message').val(text + id);
            input_change(0);
        });

        // 初始化消息发送
        $("#tb_image input").change(function() {
            var input = this;

            if (!$(input).val()) {
                return;
            }
            var progress = document.querySelector("#progress");
            http.post(
                '/upload', {
                    _xsrf: document.getElementsByName("_xsrf")[0].value,
                    file: input.files[0]
                },
                function(res) {
                    $(input).val('');
                    if (res.status) {
                        SOCK.send('image', { src: res.src, org: res.org, height: res.height, width: res.width })
                    }
                    console.log(res);
                },
                progress);
        });

    },

    checkNode: function(msg_id) {
        var t = $("[msg_id=" + msg_id + "]");
        if (msg_id > 0 && t && t.length > 0) {
            return t[0];
        }
        return false;

    },
    // 查找比msg_id小的节点
    findBiggerNode: function(msg_id) {
        var nodes = $("[msg_id]");
        if (nodes.length == 0) {
            return 0;
        }

        // 考虑到最多数情况是获取新的消息 从最大的开始遍历成功了更高
        for (var index = 0; index < nodes.length; index++) {
            var element = nodes[index];
            var bigger = $(element).attr('msg_id');
            if (bigger > msg_id) {
                return bigger;
            }
        }
        return 0;
    },
    createList: function() {
        var list = $('<li class="from_l"><div class="date_time"><span class="month_num"></span></div><div class="msg_head"><img src="/static/images/head_default.png"></div><div class="msg_main"><div class="msg_name">[系统消息]</div><div class="msg_content"><div class="msg_text">[empty]</div></div></div></li>');

        return list[0];
    },
    add_node: function(message) {
        var ul = document.querySelector('ul.content');

        var list = room.createList();
        var node_name = list.querySelector('.msg_name');
        var node_time = list.querySelector('.month_num');
        var node_content = list.querySelector('.msg_content');
        var node_text = list.querySelector('.msg_text');
        var node_img = list.querySelector('.msg_head img');
        var cnt_width = $(node_content).width() > 0 ? $(node_content).width() : 237;


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


                // 非本房间消息不处理系统消息
                if (message.to != 0 && message.to != current_room) {
                    // 自己发送的消息(如客服消息),不提示
                    if (message.from != 0 && message.from != current_user) {
                        show_notice(message.username + ':[图片]', '/room?id=' + message.to);
                    }
                    return;
                }

                message.body = JSON.parse(message.body);
                var img = createElement('img', 'src', message.body.src);
                img.setAttribute('org', message.body.org);
                img.setAttribute('height', cnt_width * 0.55 / message.body.width * message.body.height);
                img.setAttribute('width', cnt_width * 0.55);
                $(node_content).html(img);
                // node_content.html("<>")
                // console.log(cnt_width + '/' + message.body.width + '*' + message.body.height);
                img.onclick = function() {
                    // console.log(this.getAttribute('org'));
                    mask_show(this.getAttribute('org'))
                };
                break;
      
            case 'text':

 
                // 非本房间消息不处理系统消息
                if (message.to != 0 && message.to != current_room) {
                    // 自己发送的消息(如客服消息),不提示
                    if (message.from != 0 && message.from != current_user) {
                        show_notice(message.username + ":" + message.body, '/room?id=' + message.to);
                    }
                    return;
                }

                // 默认当作text处理
                message.body = message.body.replace(/\[e([0-9]+)\]/g, function(a, b) {
                    return $("#e" + b).html();
                });

                $(node_text).html(message.body);
                break;

            default:

                return;
        }




        $(node_name).text(message.username);

        if (message.headimgurl.length > 0) {
            $(node_img).attr('src', message.headimgurl);
        }

        if (message.addtime > 0) {
            $(node_time).text(todatetime(message.addtime));
        }

        if (message.from == current_user) {
            list.className = 'from_r';
        }

        if (message.from == 0) {
            node_content.classList.add('red');
        }



        if (message.id == 0) {
            $(ul).append(list);
        } else {

            // 查找比自己大一点的ID，插入到他的后面
            // 否则插入列表最前面
            list.setAttribute('msg_id', message.id);
            var bigger = room.findBiggerNode(message.id);
            if (bigger > 0) {
                var node = $("[msg_id=" + bigger + "]");
                node.before(list);
            } else {
                $(ul).append(list);
            }
        }


        // 保存当前房间最新的ID (用户新消息提醒)
        setStorage(message.to, message.id);
    },
};

$(function() {

    console.log('$');
});

$(document).ready(function() {

    console.log('ready');

});

function loaded() {
    console.log('loaded');

    current_room = $("#current_room").val();
    current_user = $("#current_user").val();
    user_name = $("#user_name").val();
    welcome = $("#welcome").val();

    room.initScroller();
    room.initEvent();
    room.initSock();
}


function input_change(event) {
    // console.log(event);
    var text = $('#message').val() || '';
    if (text.length > 0) {
        $('#tb_image').hide();
        $('#tb_send').show();
    } else {
        $('#tb_image').show();
        $('#tb_send').hide();
    }
}

function mask_show(params) {

    $('.oimage').click(function(e) {
        mask_hide();
    });

    $('.oimage img').attr("src", params);
    $('.oimage').show();
    $('.mask').show();

}

function mask_hide(params) {
    $('.mask').hide();
    $('.oimage').hide();
}