#!/usr/bin/env python

# example radiobuttons.py

import gi
from gi.repository import GObject, Gtk, Gst
import sys
import thread
import threading
import time

class WebcamUI:
    mutex2 = threading.Lock()
    ip_address = "Dummy"
    quality = "F"
    movie_window = False
    server_pipeline  = False
    client_pipeline = False
    def IPcallback(self, widget, data=None):
        self.ip_address = entry.get_text()
	print entry.get_text()
	

    def Qcallback(self, widget, data=None):
        if(widget.get_active() == True):
	    if "High Quality" == "%s" % (data):
		self.quality = "H"
	    elif "Low Quality" == "%s" % (data):
		self.quality = "L"
    
    def Submission(self, widget, data=None):
	stopbutton.set_visible(True)
	stopbutton.show()
	pause.show()
	print "Quality: " + self.quality + ", " + "IP Address: " + entry.get_text()
        self.ip_address = entry.get_text()
        self.mutex2.release()
	return self.quality, entry.get_text()


    def close_application(self, widget, event, data=None):
        #print dir(Gst)
        #print "Blocking the Queue..."
        #queue = self.client_pipeline.get_by_name("blockqueue")
        #queue_pad = self.client_pipeline.get_static_pad('source')
        #print dir(queue_pad)
        #filesink = self.client_pipeline.get_by_name("udpsrc")
        print "First hang"
        #pad = filesink.get_static_pad('sink')
        #print dir(pad)
        #print dir(pad)
        #Gst.Pad.send_event(pad, Gst.Event.new_eos())
        #Gst.Element.send_event(self.client_pipeline, Gst.Event.new_eos())
        #self.client_pipeline.send_event(Gst.Event.new_eos())
	
	#blockqueue = self.client_pipeline.get_by_name('blockqueue')
        #filesink = self.client_pipeline.get_by_name('filesink')
        #avimux = self.client_pipeline.get_by_name('avimux')
        #blockqueue.unlink(avimux)
	#pad = avimux.get_static_pad('video_0')
        #for pad in avimux.pads:
	#	print pad.name
        #pad.event_default(Gst.Event.new_eos())
	#time.sleep(5)

	#source = self.server_pipeline.get_by_name('filesrc')
	#source.send_event(Gst.Event.new_eos())

	#source = self.server_pipeline.get_by_name('udpsrc0')
	#source.send_event(Gst.Event.new_eos())

	#src = self.server_pipeline.iterate_sources()
	#one, two = src.next()
	#print two.name

	#time.sleep(10)
        #print "Stopping the client..."
        #self.client_pipeline.set_state(Gst.State.NULL)
        #print "Stopping the Gtk..."
        #Gtk.main_quit()
        #print "SENT EOSS"
        return

    def __init__(self):
        self.mutex2.acquire()
	global entry
	global pause
	global stopbutton
        self.window = Gtk.Window(title="RadioButtonThing")

        self.window.connect("delete_event", self.close_application)

        #self.window.set_border_width(45)
	self.window.set_default_size(1000, 640)
	self.window.set_title("Video Conference")

        box1 = Gtk.VBox(False, 0)
        self.window.add(box1)
        box1.show()

	box3 = Gtk.HBox(False, 10)
	box3.set_border_width(10)
	box1.pack_end(box3, False, False, 0)
	box3.show()
	
        box2 = Gtk.HBox(False, 0)
        box1.pack_end(box2, False, False, 0)
        box2.show()

	#label = Gtk.Label("Connection and Quality:")
	#label.connect("populate-popup", self.IPcallback)
	#box3.pack_start(label, True, True, 0)
	#label.set_visible(True)
	
	#Create Label for Entering IP
	label = Gtk.Label("Enter an IP to connect to:")
	#label.connect("populate-popup", self.IPcallback)
	box3.pack_start(label, True, True, 0)
	label.set_visible(True)
	
	#create text field for entering IP to connect to
	entry = Gtk.Entry()
	entry.connect("toggle-overwrite", self.IPcallback)
	entry.set_sensitive(True)
	entry.set_max_length(25)
	box3.pack_start(entry, True, True, 0)
	entry.show()

	#Label for quality selection
	Qlabel = Gtk.Label("Choose the Quality you would like:")
	#label.connect("populate-popup", self.IPcallback)
	box3.pack_start(Qlabel, True, True, 0)
	Qlabel.set_visible(True)

	#Radiobutton for H quality
        button = Gtk.RadioButton.new_with_label_from_widget(None, "High Quality")
        button.connect("toggled", self.Qcallback, "High Quality")
        box3.pack_start(button, True, True, 0)
        button.show()

	#radiobutton for L quality
        button = Gtk.RadioButton.new_with_label_from_widget(button, "Low Quality")
        button.connect("toggled", self.Qcallback, "Low Quality")
        button.set_active(True)
        box3.pack_start(button, True, True, 0)
        button.show()

	#Video window added to box1
	self.movie_window = Gtk.DrawingArea()
	box1.pack_start(self.movie_window, True, True, 10)
	self.movie_window.set_visible(True)
	self.movie_window.show()

	#Stop button to close window
	stopbutton = Gtk.Button("Stop")
	stopbutton.set_border_width(5)
	stopbutton.connect_object("clicked", self.close_application, self.window, None)
	box2.pack_end(stopbutton, True, True, 0)

	#Pause button for updating pipeline??
	pause = Gtk.Button("Pause")
	pause.set_border_width(5)
	pause.connect_object("clicked", self.close_application, self.window, None)
	box2.pack_end(pause, True, True, 0)
	
        separator = Gtk.HSeparator()
        box1.pack_end(separator, False, True, 0)
        separator.show()

        #box2 = Gtk.HBox(False, 10)
        #box2.set_border_width(10)
        #box1.pack_end(box2, False, True, 0)
       # box2.show()

        button = Gtk.Button("Submit")
        button.connect_object("clicked", self.Submission, self.window,
                              None)
	#button.connect_object("clicked", self.close_application, self.window,
        #                      None)
        box3.pack_end(button, False, False, 0)
        button.show()
        self.window.show()

