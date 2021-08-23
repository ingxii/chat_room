var SOCK = {
    socket: null,
    target: null,
    // 连接成功时
    _onopen: function(event) {
        // 进入房间才能收到该房间的消息
        SOCK.on_open(event);
    },

    // 收到消息时
    _onmessage: function(event) {
        var message = JSON.parse(event.data)

        message.id = +message.id || 0;
        message.add_time = +message.add_time || 0;
        message.from = +message.from || 0;
        message.to = +message.to || 0;


        SOCK.on_message(message);
    },

    // 连接被断开时
    _onclose: function(event) {

    },

    on_close: function(message) {

    },
    on_open: function(message) {

    },
    on_message: function(message) {

    },
    // 发送消息
    send: function(type, body, target) {
        target = +target || SOCK.target || 0;
        if (!target) { return; }

        var message = {
            type: type, //消息类型
            body: body, //消息内容
            to: target, //发送的目标
        };

        SOCK.socket.send(JSON.stringify(message));
    },

    init: function(host, target) {
        SOCK.target = +target || 0;
        SOCK.socket = new WebSocket(host);
        SOCK.socket.onmessage = SOCK._onmessage;
        SOCK.socket.onopen = SOCK._onopen;
        SOCK.socket.onclose = SOCK._onclose;
    },
};