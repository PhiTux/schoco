let dec = new TextDecoder();

onmessage = function (event) {
    postMessage(dec.decode(event.data));
};