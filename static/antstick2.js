/*
From https://stackoverflow.com/questions/38987784/how-to-convert-a-hexadecimal-string-to-uint8array-and-back-in-javascript
*/
const fromHexString = (hexString) =>
  Uint8Array.from(hexString.match(/.{1,2}/g).map((byte) => parseInt(byte, 16)));

const toHexString = (bytes) =>
  bytes.reduce((str, byte) => str + byte.toString(16).padStart(2, '0'), '');

// Function to prompt the user for a serial device matching the ANT USBStick2 vendor ID if it's plugged in
async function get_serial_device() {
    const usbVendorId = 0x0FCF;
    try {
        port = await navigator.serial.requestPort({filters: [{ usbVendorId }]});
        await port.open({ baudRate: 115200});
        return port;
    } catch (error) {
        console.log('Unable to get port!');
        console.log(error);
        return null;
    }
}

// Function to parse out the ANT+ messages in a UInt8Array of read bytes
function parse_data(bytes) {
    var msgs = []
    for (i = 0; i < bytes.length; i++) {
        if (bytes[i] == 0xa4) {
            if (bytes.length < i+3) 
                break;
            var msg = { sync: bytes[i]};
            msg.len = bytes[i+1];
            msg.type = bytes[i+2];
            console.log("Read a message of type: 0x" + msg.type.toString(16));
            msg.data = bytes.slice(i+3, i+3+msg.len);
            msg.chksum = bytes[i+4+msg.len];
            i += 4 + msg.len;
            msgs.push(msg);
        }
    }
    return msgs;
}

// Parses an ANT+ message to detect if it contains a HR value, and if so returns it, otherwise it returns -1.
function get_hr(msg) {
    if (msg.type == 0x4E && !isNaN(parseInt(msg.data[8]))) {
        console.log("Got HR: " + msg.data[8]);
        if (msg.data[8] != 255 && msg.data[8] != 0)
            return msg.data[8];
    }
    return -1;
}

var last_avg_hr = 0;
// A function to read in a block of messages and average any received HRs, otherwise returns 0
async function get_avg_hr(sd) {
    var hrs = [];
    msgs = await read_messages(sd);
    for (i = 0; i < msgs.length; i++) {
        hr = get_hr(msgs[i]);
        if (hr != -1)
            hrs.push(hr);
    }
    if (hrs.length > 0) {
        var old_last = last_avg_hr;
        last_avg_hr = parseInt(hrs.reduce((a, b) => a + b, 0) / hrs.length)
        if (isNaN(last_avg_hr)) 
            last_avg_hr = old_last;
        if (!closing)
            window.setTimeout(get_avg_hr, 2000, sd);
        return last_avg_hr;
    }
    return 0;
}

// Reads messages from a serial port
var reader = null;
async function read_messages(sd) {
    var msgs = [];
    if (sd.readable) {
        if (reader == null) {
            reader = sd.readable.getReader();
        }
        try {
            const { done, value } = await reader.read();
            if (!done) {
                msgs = parse_data(value);
                //console.log('Read message: ' + msgs);
            } else {
                console.log("Done!");
            }
        } catch (error) {
            console.log(error);
        }
    }
    
    return msgs;
}

// Function to write a hexstring to the serial port
var writer = null;
async function send_hexstring(sd, hstr) {
    bytes = fromHexString(hstr);
    if (writer == null)
        writer = sd.writable.getWriter();
    await writer.write(bytes);
    //writer.releaseLock();
}

// Clunky function to enable ANT+ RX scan mode
async function enable_rx_scan_mode(sd) {
    await send_hexstring(sd, 'a4014a30df');
    await send_hexstring(sd, 'a4014a30df');
    await send_hexstring(sd, 'a4094600b9a521fbbd72c34564');
    await send_hexstring(sd, 'a40342004000a5');
    await send_hexstring(sd, 'a405510000000000f0');
    await send_hexstring(sd, 'a402450039da');
    await send_hexstring(sd, 'a402660001c1');
    await send_hexstring(sd, 'a4026e00e028');
    await send_hexstring(sd, 'a4015b00fe');
}

// Function to attempt to cleanly close the serial port
var closing = false;
async function close_port(sd) {
    closing = true;
    if (reader != null)
        reader.releaseLock();
    if (writer != null)
        writer.releaseLock();
    await sd.close();
}
