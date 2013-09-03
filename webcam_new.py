#!/usr/bin/python3

import gi
import thread
import threading
import socket
import sys
import time
import WebcamUI
import scipy.misc
import metrikz
import argparse
import math
import struct
import SNR
from os.path import expanduser
import os
import shutil
#a=scipy.misc.imread('test.bmp')
#b=scipy.misc.imread('test2.bmp')
#print "THE SNR!!!!! : " + str(metrikz.snr(a,b))


#for x = 1 to 100:
#	a = scipy.misc.imread('folder1/foo-' + x + '.bmp')
#	a = scipy.misc.imread('folder2/foo-' + x + '.bmp')
#	print "THE SNR!!!!! : " + str(metrikz.snr(a,b))

#  Setup the argument parser
parser = argparse.ArgumentParser(description='Video streaming Signal-to-noise ratio diagnostic utility.')
parser.add_argument('ip_address', help='IP address to connect to')
parser.add_argument('my_channel', help='Channel used by this computer')
parser.add_argument('partners_channel', help='Channel used by partners computer')

parser.add_argument('--server', help='Included flag if this computer is the server')
parser.add_argument('--bind_address', help='Server IP address to bind to the target port')
parser.add_argument('--quality', help='Quality set by the server between 1 and 100 where 100 is the highest quality')
parser.add_argument('--video_path', help='Specifies an alternate path from the ~/gstvids default')

args = parser.parse_args()

gi.require_version('Gst', '1.0')
from gi.repository import GObject, Gst


# Needed for window.get_xid(), xvimagesink.set_window_handle(), respectively:
from gi.repository import GdkX11, GstVideo


GObject.threads_init()
Gst.init(None)
#Gdk.threads_init()

# Define Globals
mutex = threading.Lock()
caps = "False"
webui = False
server_pipeline = False
client_pipeline = False
sock = False
hitServerException = False
serv = False


# Determine the Video Path
if (args.video_path == None):
    GST_VIDEO_PATH = expanduser("~") + "/gstvids"
    print GST_VIDEO_PATH
else:
    GST_VIDEO_PATH = args.video_path

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class Server:
    def __init__(self, ip_address, partners_quality, my_channel, video_path):
        # Create GStreamer pipeline
        self.pipeline = Gst.Pipeline()

	#  Determine the different ports from the given channel
	videoSinkPort = 5000 + int(my_channel)*10
	rtcpSinkPort = 5001 + int(my_channel)*10
	rtcpSourcePort = 5002 + int(my_channel)*10


	self.pipeline = Gst.parse_launch("rtpbin name=rtpbin filesrc name=filesrc location=" + video_path + "/processed_server.avi ! avidemux ! videoconvert ! videorate ! videoscale ! video/x-raw,format=I420,width=640,height=480,framerate=24/1 ! avenc_mpeg4 bitrate=" + str(partners_quality) + " ! rtpmp4vpay ! rtpbin.send_rtp_sink_0 rtpbin.send_rtp_src_0 ! udpsink name=udpsink_video port=" + str(videoSinkPort) + " host=" + ip_address + " rtpbin.send_rtcp_src_0 ! udpsink port=" + str(rtcpSinkPort) + " host=" + ip_address + " sync=false async=false udpsrc port=" + str(rtcpSourcePort) + " ! rtpbin.recv_rtcp_sink_0")
	print "You've sent quality level " + str(partners_quality)

    def run(self):
        try:
            global mutex, caps, server_pipeline
            # Create bus to get events from GStreamer pipeline
            self.bus = self.pipeline.get_bus()
            self.bus.enable_sync_message_emission()
            self.bus.connect('message::error', self.on_error)
	    self.bus.connect('message::eos', self.on_eos)
	    server_pipeline = self.pipeline
            print self.pipeline.set_state(Gst.State.PLAYING)
	    print "Sleeping for 15: Streaming data to the client..." 
	    time.sleep(15)
  	    stopServerPipeline()

        except: 
            e = sys.exc_info()[0]
            print "Error in run method of Server: " + str(e)



    def on_error(self, bus, msg):
        print('on_error():', msg.parse_error())
        
    def on_eos(self, bus, msg):
        print "Server recieved EOS!"
        return
	

class Client:
    def __init__(self, ip_address, partners_caps, partners_channel, video_path):
        print "IP_ADDRESS: " + ip_address
        print "PARTNERS_CAPS: " + partners_caps

	#  Determine the different ports from the given channel
	videoSourcePort = 5000 + int(partners_channel)*10
	rtcpSourcePort = 5001 + int(partners_channel)*10
	rtcpSinkPort = 5002 + int(partners_channel)*10


	partners_caps = partners_caps.replace(" ", "")
	self.pipeline = Gst.parse_launch("rtpbin name=rtpbin udpsrc name=udpsrc1 port=" + str(videoSourcePort) + " caps=" + partners_caps + " ! rtpbin.recv_rtp_sink_0 rtpbin. ! rtpmp4vdepay name=rtpmp4 ! avdec_mpeg4 name=decoder ! videoconvert ! videoscale ! videorate ! video/x-raw,width=640,height=480,framerate=24/1 ! avimux ! filesink location=" + video_path + "/client.avi udpsrc name=udpsrc2 port=" + str(rtcpSourcePort) + " ! rtpbin.recv_rtcp_sink_0 name=rtpbin4 rtpbin.send_rtcp_src_0 ! udpsink name=udpsink1 port=" + str(rtcpSinkPort) + " host=" + ip_address + " sync=false async=false")

        self.bus = self.pipeline.get_bus()
        self.bus.add_signal_watch()
        self.bus.connect('message::eos', self.on_eos)

    def run(self):
	global client_pipeline
	try:
	    client_pipeline = self.pipeline
            print self.pipeline.set_state(Gst.State.PLAYING)
	    # Wait to make sure the client has sufficient start time
	    print "Giving the client time to fully start..."
	    time.sleep(5)
	    # Tell the server that the pipeline has been started
	    sock.send(b'A') # single character A to prevent issues with buffering
	    # Wait for the video to finish
	    print "Sleep for 20: Recieving the video stream"
	    time.sleep(15)
	    stopClientPipeline()

        except: 
            e = sys.exc_info()[0]
            print "Error in run method of Client: " + str(e)

    def quit(self, window):
        t = True

    def on_eos(self, bus, msg):
        print "CLient recieved EOS!"
        return

def runServer(self, ip_address, partners_quality, my_channel, video_path):
    server = Server(ip_address, partners_quality, my_channel, video_path)
    server.run()
def runClient(self, ip_address, partners_caps, partners_channel, video_path):
    client = Client(ip_address, partners_caps, partners_channel, video_path)
    client.run()

def stopClientPipeline():
    print "Entered Stop Pipeline..."
    global server_pipeline, client_pipeline, sock, GST_VIDEO_PATH, hitServerException, mutex

    source = client_pipeline.get_by_name('udpsrc1')
    source.send_event(Gst.Event.new_eos())

    source = client_pipeline.get_by_name('udpsrc2')
    source.send_event(Gst.Event.new_eos())
	
    print "Sleep for 5: Finalizing the video file"    
    time.sleep(10)
    client_pipeline.set_state(Gst.State.NULL)
    print "Sleep for 15: Making sure the pipeline has stopped"
    time.sleep(15) # Make sure the pipeline stops

    print "Sending the recieved server file"
    print GST_VIDEO_PATH + "/client.avi"

    sendFile(GST_VIDEO_PATH + "/client.avi")
    sock.close()
    mutex.release()
    thread.exit()
        

def stopServerPipeline():
    print "Entered Stop Pipeline..."
    global server_pipeline, client_pipeline, sock, GST_VIDEO_PATH, hitServerException, serv
    source = server_pipeline.get_by_name('filesrc')
    source.send_event(Gst.Event.new_eos())

    source = server_pipeline.get_by_name('udpsrc0')
    source.send_event(Gst.Event.new_eos())
	
    #print "Sleep for 15: Waiting for client to finalize the video"    
    #time.sleep(15)
    server_pipeline.set_state(Gst.State.NULL)

    print "Recieving the streamed server file"
    print GST_VIDEO_PATH + "/recieved_server.avi"
    recieveFile(GST_VIDEO_PATH + "/recieved_server.avi")
    filesrc = GST_VIDEO_PATH + "/recieved_server.avi"
    filesink = GST_VIDEO_PATH + "/Recieved"
    print "Splicing the AVI into Images..."
    os.system('avconv -i ' + filesrc + ' -r 500 -s 640x480 -f image2 ' + filesink + '/%01d.bmp')
    snr = SNR.SNR()
    print "Starting the SNR Comparator..."
    avg_snr, min_snr = snr.compareFiles()
    writeToFile(str(args.quality) + " " + str(avg_snr) + " " + str(min_snr))
    print "Complete!"
    mutex.release()
    thread.exit()

def sendFile(path):
    global sock
    print "S1"
    sendfile = open(path, 'rb')
    print "S2"
    data = sendfile.read()
    print "S3"
    us32bit = struct.pack("I", sys.getsizeof(data))
    print "Sent Data Size: " + str(sys.getsizeof(data))
    sock.sendall(us32bit) # Send the length as a fixed size message
    print "S4"    
    sock.sendall(data)
    print "S5"
    # Get Acknowledgement
    sock.recv(1) # Just 1 byte
    print "S6"

def recieveFile(path):
    global sock
    print "R1"
    LENGTH_SIZE = 4 # length is a 4 byte int.
    # Recieve the file from the client
    writefile = open(path, 'wb')
    print "R2"
    us32bit = sock.recv(LENGTH_SIZE) # Read a fixed length integer, 2 or 4 bytes
    length = total_length = struct.unpack("I", us32bit)[0]
    print "Recieved Data Size: " + str(length)
    print "R3"
    while (length > 0):
        rec = sock.recv(min(1024, length))
        length -= min(1024, length)
        writefile.write(rec) 
        print "Total: " + str(total_length) + " :: Recieved: " + str(sys.getsizeof(rec)) + " :: Remaining: " + str(length)
    print "R4"
    sock.send(b'A') # single character A to prevent issues with buffering
    print "R5"

def writeToFile(text):
    global GST_VIDEO_PATH
    with open(GST_VIDEO_PATH + "/output.txt", "a") as myfile:
        myfile.write(text + "\n")

if (args.server):
    mutex.acquire()
    try:
        shutil.rmtree(GST_VIDEO_PATH + "/Recieved")
        os.mkdir(GST_VIDEO_PATH + "/Recieved")
        os.remove(GST_VIDEO_PATH + "/recieved_server.avi")
    except:
        print "Tried removing old files, but they may have been gone already."

    print "Server Started:  Waiting for client connection"
    serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv.bind((args.bind_address, 3000))
    serv.listen(1)
    sock, addr = serv.accept()
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    serv.close()
    "Waiting for client pipeline to start..."
    dummy = sock.recv(1024) # Wait for client started confirmation
    thread.start_new_thread(runServer, (None, args.ip_address, args.quality, args.my_channel, GST_VIDEO_PATH))
    
else:
    while (1 == 1):
        mutex.acquire() #  Wait until the current client thread is finished to start a new one
        try:
            os.remove(GST_VIDEO_PATH + "/client.avi")
        except:
            dummy = 0

    	try:
    	    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    	    sock.connect((args.ip_address, 3000))
    	    partners_caps = "application/x-rtp,media=video,clock-rate=90000,encoding-name=MP4V-ES,profile-level-id=1,config=000001b001000001b58913000001000000012000c48d8800f514043c1463000001b24c61766335332e33352e30,ssrc=536143025,payload=96"
    	    thread.start_new_thread(runClient, (None, args.ip_address, partners_caps, args.partners_channel, GST_VIDEO_PATH))
        except:
            print "Sleeping for 5: Failed to connect client..."
            time.sleep(5)
            mutex.release()

mutex.acquire()

