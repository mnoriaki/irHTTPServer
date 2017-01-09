#!/usr/bin/env python
# coding: UTF-8

import datetime
import locale
import serial
import subprocess
import sys
import time
import threading
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web

from tornado.options import define, options
from wakeonlan import wol

volP = "amixer -Dhw:0 set 'Speaker Digital' 1dB+ && amixer -Dhw:0 set 'Speaker Digital' unmute "
volM = "amixer -Dhw:0 set 'Speaker Digital' 1dB- && amixer -Dhw:0 set 'Speaker Digital' unmute "
mute = "amixer -Dhw:0 set 'Speaker Digital' mute"
unMute = "amixer -Dhw:0 set 'Speaker Digital' unmute; "
tvinY = "amixer -Dhw:0 cset name='SPKOUTL Input 2 Volume' 40 && amixer -Dhw:0 cset name='SPKOUTR Input 2 Volume' 40 ; "
tvinN = "amixer -Dhw:0 cset name='SPKOUTL Input 2 Volume' 0 && amixer -Dhw:0 cset name='SPKOUTR Input 2 Volume' 0 ; "
fm = "/home/pi/bin/intec205 /dev/ttyACM0 fm"
am = "/home/pi/bin/intec205 /dev/ttyACM0 am"
off = "/home/pi/bin/intec205 /dev/ttyACM0 off"
radioinY = "/home/pi/bin/line.on"
radioinN = "/home/pi/bin/line.off"

define("port", default=8000, help="run on the given port", type=int)

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Hello, world")

class SecRequestHandler(tornado.web.RequestHandler):
    def get(self):
        d = datetime.datetime.today()
        body = str(d.second)
        self.set_header('Content-type', 'text/plain; charset=ascii')
        self.write(body)

class LogRequestHandler(tornado.web.RequestHandler):
    def get(self):
	print self
        d = datetime.datetime.today()
        logdat = d.strftime("%Y%m%d %H:%M:%S") +  ", " + self.request.remote_ip + ", " + self.request.uri.replace('/log/', '') + '\n'
	tornado.ioloop.IOLoop.instance().add_callback(WriteLog, logdat)
        self.set_header('Content-type', 'text/plain; charset=ascii')
        self.write(logdat)

class MyStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        # Disable cache
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')

class webCamHandler(tornado.web.RequestHandler):
    def get(self):
	# subprocess.call(["fswebcam", "-d", "/dev/video0", "-r", "1280x720", "/tmp/webcam.jpg"])
	subprocess.call(["fswebcam", "-d", "/dev/video0", "-r", "1280x720", "--no-banner", "/tmp/webcam.jpg"])
        self.set_header('Content-type', 'text/html; charset=ascii')
        self.write('<html><body><img src="webcam.jpg"></body></html>')

def WriteLog(dat):
        with open("log.txt", "a") as logfile:
            logfile.write(dat)

class AHEARequestHandler(tornado.web.RequestHandler):
    def get(self):
        print self
        cmd = "A" + self.request.uri.replace('/A/', '') + '\n'
        tornado.ioloop.IOLoop.instance().add_callback(SerialWrite, cmd)
        self.set_header('Content-type', 'text/plain; charset=ascii')
        self.write(cmd)

class NECRequestHandler(tornado.web.RequestHandler):
    def get(self):
        print self
        cmd = "N" + self.request.uri.replace('/N/', '') + '\n'
        tornado.ioloop.IOLoop.instance().add_callback(SerialWrite, cmd)
        self.set_header('Content-type', 'text/plain; charset=ascii')
        self.write(cmd)

class SonyRequestHandler(tornado.web.RequestHandler):
    def get(self):
        print self
        cmd = "S" + self.request.uri.replace('/S/', '') + '\n'
        tornado.ioloop.IOLoop.instance().add_callback(SerialWrite, cmd)
        self.set_header('Content-type', 'text/plain; charset=ascii')
        self.write(cmd)

class OCR04RequestHandler(tornado.web.RequestHandler):
    def get(self):
        cmd = self.request.uri.replace('/OCR04/', '')
	if cmd == "ON" or cmd == "on":
        	tornado.ioloop.IOLoop.instance().add_callback(SerialWrite, "o")
	if cmd == "OFF" or cmd == "off":
        	tornado.ioloop.IOLoop.instance().add_callback(SerialWrite, "O")
        self.set_header('Content-type', 'text/plain; charset=ascii')
        self.write(cmd)

class OCR05RequestHandler(tornado.web.RequestHandler):
    def get(self):
        cmd = self.request.uri.replace('/OCR05/', '')
	if cmd == "ON" or cmd == "on":
        	tornado.ioloop.IOLoop.instance().add_callback(SerialWrite, "p")
	if cmd == "OFF" or cmd == "off":
        	tornado.ioloop.IOLoop.instance().add_callback(SerialWrite, "P")
        self.set_header('Content-type', 'text/plain; charset=ascii')
        self.write(cmd)

def SerialWrite(dat):
    print(dat)
    s.write(dat)

# RDのネットリモコンの使い方メモ
# http://d.hatena.ne.jp/nyanonon/20070619%23p3
# 電源OFF
# curl --digest --user user:pass http://<IP address>/remote/remote.htm?key=12
class RDRequestHandler(tornado.web.RequestHandler):
    def get(self):
        cmd = self.request.uri.replace('/RD/', '')
	if cmd == "ON" or cmd == "on":
		wol.send_magic_packet('e8:9d:87:12:34:56')
	if cmd == "OFF" or cmd == "off":
        	subprocess.call('curl --digest --user user:pass http://192.168.1.10/remote/remote.htm?key=12 &', shell=True)
        self.set_header('Content-type', 'text/plain; charset=ascii')
        self.write(cmd)

class IntecRequestHandler(tornado.web.RequestHandler):
    def get(self):
	global fm, am, off, radioinY, radioinN
        cmd = self.request.uri.replace('/intec/', '')
	if cmd == "FM" or cmd == "fm":
		subprocess.call(radioinY, shell=True)
		subprocess.call(fm, shell=True)
	if cmd == "AM" or cmd == "am":
		subprocess.call(radioinY, shell=True)
		subprocess.call(am, shell=True)
	if cmd == "OFF" or cmd == "off":
		subprocess.call(radioinN, shell=True)
		subprocess.call(off, shell=True)

class SerialThread(threading.Thread):
	def run(self):
		while True:
			r = s.readline()
			r = r.strip()
        		d = datetime.datetime.today()
        		logdat = d.strftime("%Y%m%d %H:%M:%S") +  " " + r + '\n'
			print r
			handleRemote(r)
			sys.stdout.flush()
			WriteLog(logdat)

def handleRemote(r):
	global muting, tvin, radioin
	global volP, volM, mute, unMute, tvinY, tvinN
	global fm, am, off, radioinY, radioinN

	if r == "N 00FF46B9": # UP
		subprocess.call(volP, shell=True)
	if r == "N 00FF15EA": # DN
		subprocess.call(volM, shell=True)
	if r == "N 00FF40BF": # OK
		if muting == False:
			subprocess.call(mute, shell=True)
			muting = True
		else :
			subprocess.call(unMute, shell=True)
			muting = False
	# if r == "N 00FF43BC": # R
	# if r == "N 00FF44BB": # L
	if r == "N 00FF16E9": # 1
		if tvin == False:
			subprocess.call(tvinY, shell=True)
			tvin = True
		else :
			subprocess.call(tvinN, shell=True)
			tvin = False
	if r == "N 00FF19E6": # 2
		if radioin == False:
			subprocess.call(radioinY, shell=True)
			radioin = True
		else :
			subprocess.call(radioinN, shell=True)
			radioin = False
	# if r == "N 00FF0DF2": # 3
	if r == "N 00FF0CF3": # 4
		subprocess.call(radioinY, shell=True)
		subprocess.call(fm, shell=True)
	if r == "N 00FF18E7": # 5
		subprocess.call(radioinY, shell=True)
		subprocess.call(am, shell=True)
	if r == "N 00FF5EA1": # 6
		subprocess.call(radioinN, shell=True)
		subprocess.call(off, shell=True)

def main():
    tornado.options.parse_command_line()

    application = tornado.web.Application([
        (r"/log/.*", LogRequestHandler),
        (r"/A/.*", AHEARequestHandler),
        (r"/N/.*", NECRequestHandler),
        (r"/S/.*", SonyRequestHandler),
        (r"/intec/.*", IntecRequestHandler),
        (r"/OCR04/.*", OCR04RequestHandler),
        (r"/OCR05/.*", OCR05RequestHandler),
        (r"/RD/.*", RDRequestHandler),
        (r"/sec", SecRequestHandler),
        (r"/web", webCamHandler),
        (r"/(.*)", MyStaticFileHandler, {"path": ".", "default_filename": "index.html"}),
      #  (r"/(.*)", tornado.web.StaticFileHandler, {"path": ".", "default_filename": "index.html"}),
    ])
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()
    s.close()

muting = False
tvin = True
radioin = False
if __name__ == "__main__":
    s = serial.Serial("/dev/ttyUSB0",115200)
    st = SerialThread()
    st.start()
    main()
