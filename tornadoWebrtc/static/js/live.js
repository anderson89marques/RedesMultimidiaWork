/**
 * Created by anderson on 06/02/16.
 */

var ws = new WebSocket(location.href.replace('http', 'ws').replace('live', 'ws'));
console.log('ws://' + location.host + '/ws');
console.log("^");
console.log(location.href.replace('http', 'ws').replace('live', 'ws'));

var initiator;
var pc;

var app = angular.module("liveApp", []);

//redefini a ferramenta de expressão do angular pôs conflitava com o do tornado :D
app.config(function ($interpolateProvider) {
        $interpolateProvider.startSymbol('{[{').endSymbol('}]}')
    });

app.controller("liveAppCtrl", function($scope){

    $scope.msg = "WebRTC";
    var role;
    $scope.call = function (papel) {
        $('#btn-call').addClass('btn-active');
        initiator = true;
        role = papel;
        init();
    }

    $scope.receive = function (papel) {
        $('#btn-receive').addClass('btn-active');
        initiator = false;
        role = papel;
        init();
    }

    function init() {
        var constraints = {
            audio: $('#audio').prop('checked'),
            video: $('#video').prop('checked')
        };

        console.log(role);
        if(role  === "role_teacher"){
            getUserMedia(constraints, connect, fail);
        }else{
            connect();
        }

        /*
        if (constraints.audio || constraints.video) {
            getUserMedia(constraints, connect, fail);
        } else {
            connect();
        }
        */
    }

    //para tentar conectar com vários usuários e caso o remote já esteja ok
    //não seja reconectado o que dar erro de status do sdp
    //Solução temporaria.
    var isRemotePlying = false;

    pc = new RTCPeerConnection(null);
    function connect(stream) {

        if (stream) {
            pc.addStream(stream);
            $('#local').attachStream(stream);
        }

        pc.onaddstream = function(event) {

            if(!isRemotePlying){
                console.log('Adicionando Remote Stream...');
                $('#remote').attachStream(event.stream);
                isRemotePlying = true;
            }
        };
        pc.onicecandidate = function(event) {
            if (event.candidate) {
                ws.send(JSON.stringify(event.candidate));
            }
        };
        ws.onmessage = function (event) {
            var signal = JSON.parse(event.data);

            if(!isRemotePlying){
                if (signal.sdp) {
                if (initiator) {
                    receiveAnswer(signal);
                } else {
                    receiveOffer(signal);
                }
                } else if (signal.candidate) {
                    pc.addIceCandidate(new RTCIceCandidate(signal));
                }
            }

        };

        if (initiator) {
            createOffer();
        } else {
            log('waiting for offer...');
        }
        logStreaming(false);
    }


    function createOffer() {
        log('creating offer...');
        pc.createOffer(function(offer) {
            log('created offer...');
            pc.setLocalDescription(offer, function() {
                log('sending to remote...');
                ws.send(JSON.stringify(offer));
            }, fail);
        }, fail);
    }


    function receiveOffer(offer) {
        log('received offer...');
        pc.setRemoteDescription(new RTCSessionDescription(offer), function() {
            log('creating answer...');
            pc.createAnswer(function(answer) {
                log('created answer...');
                pc.setLocalDescription(answer, function() {
                    log('sent answer');
                    ws.send(JSON.stringify(answer));
                }, fail);
            }, fail);
        }, fail);
    }


    function receiveAnswer(answer) {
        log('received answer');
        pc.setRemoteDescription(new RTCSessionDescription(answer));
    }


    function log() {
        $('#status').text(Array.prototype.join.call(arguments, ' '));
        console.log.apply(console, arguments);
    }


    function logStreaming(streaming) {
        $('#streaming').text(streaming ? '[streaming]' : '[..]');
    }


    function fail() {
        $('#status').text(Array.prototype.join.call(arguments, ' '));
        $('#status').addClass('error');
        console.error.apply(console, arguments);
    }


    jQuery.fn.attachStream = function(stream) {
        this.each(function() {
            this.src = URL.createObjectURL(stream);
            this.play();
        });
    };

});