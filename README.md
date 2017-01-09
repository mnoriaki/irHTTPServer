# irHTTPServer
This is an HTTP server code which I use with an Arduino based IR remote module (see https://github.com/mnoriaki/irRemote )
It can send IR signal through the module and execute commands from IR controllers and HTTP clients.

## Abstract
This HTTP server is written in Python using tornado HTTP server module. It can send IR seginals accessing HTTP server like
- http://localhost:8000/A/23CB260100204C0630D800000000100400A3  (send 23CB260100204C0630D800000000100400A3 in AHEA format and turn an air conditioner ON)
- http://localhost:8000/OCR04/ON  (turn Ohm's OCR-04 ON)
- http://localhost:8000/OCR04/OFF  (turn Ohm's OCR-04 OFF)
- http://localhost:8000/OCR05/ON  (turn Ohm's OCR-05 ON)
- http://localhost:8000/OCR05/OFF  (turn Ohm's OCR-05 OFF)
- http://localhost:8000/N/45B612ED  (send 458612ED in NEC format and toggle power of a Toshiba BD/HDD recorder)

It also send wake on LAN packet by
- http://localhost:8000/RD/ON (turn on a Toshiba BD/HDD recorder)
or turn of the recorder by 
- http://localhost:8000/RD/OFF (turn off a Toshiba BD/HDD recorder through web interface)
or capture an image by USB camera
- http://localhost:8000/web

The HTTP server also act as an IR remote server. 
It changes speaker volume if it recieves some signals from the IR remote module through serial port, 
turns off OCR-04, air conditioner and BD/HDD recorder if it recieves another signal.

Please read the script to see how to modify for your application.

## Running the script
Addition to the IR remote module, you need Python serial and tornado modules. 
You also need fswebcam if you want to take picture with a USB camera.

## homebridge
This HTTP server can use with homebridge (homebridge-http module). 
Example config.json file is shown in homebridge/config.json .
