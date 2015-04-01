#!/usr/bin/env python

# Copyright (c) Robert Blair Mason Jr. (rbmj) rbmj@verizon.net
# see LICENSE for license information.

import socket
import sys
import threading
import atexit
import time

#allow import in both python 2.x and 3.x
try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty
    
      
def _output_fn(s):
    sys.stdout.write(s) 

def _input_fn(q):
    def enqueue_output_file(f, q):
        for line in iter(f.readline, b''): #thanks to stackoverflow
            q.put((True, line))
    
    stdin_reader = threading.Thread(target = enqueue_output_file, args = (sys.stdin, q))
    stdin_reader.daemon = True
    stdin_reader.start()


def run(UDP_IN_PORT=6666, UDP_OUT_PORT=6668, init_event=None, bcast_address='255.255.255.255',
        output_fn=_output_fn, input_fn=_input_fn):
    '''
        :param init_event: a threading.event object, upon which the 'set'
                           function will be called when the connection has
                           succeeded.
                           
        :param output_fn:  This function gets called with a string each time
                           a line is received from the netconsole port
        :param input_fn:   This function is called once, with a python queue
                           object that input can be pushed into. Input must
                           be pushed as a tuple, with the first argument
                           as 'True' and the second argument as bytes or str
    '''

    #set up receiving socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind( ('',UDP_IN_PORT) )

    #set up sending socket - use separate socket to avoid race condition
    out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    out.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    out.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    out.bind( ('',UDP_OUT_PORT) ) #bind is necessary for escoteric reasons stated on interwebs

    #set up atexit handler to close sockets
    def atexit_func():
        sock.close()
        out.close()

    atexit.register(atexit_func)

    #set up threads to emulate non-blocking io
    #thread-level emulation required for compatibility with windows
    queue = Queue()

    def enqueue_output_sock(s, q):
        if init_event is not None:
            init_event.set()
        
        while True:
            q.put((False, s.recv(4096)))

    sock_reader = threading.Thread(target = enqueue_output_sock, args = (sock, queue))
    sock_reader.daemon = True
    sock_reader.start()
    
    input_fn(queue)
    
    if sys.version_info[0] == 2:
        def send_msg(msg):
            out.sendto(msg, (bcast_address, UDP_OUT_PORT))
        
        do_decode = lambda s: s
    else:
        def send_msg(msg):
            out.sendto(msg.encode('utf-8'), (bcast_address, UDP_OUT_PORT))
            
        do_decode = lambda s: str(s, 'utf-8')
    
    #main loop
    while True:
        
        is_input, msg = queue.get()
        
        if is_input:
            if bcast_address is None:
                sys.stderr.write("Error: Output not supported by netconsole without specifying a broadcast address\n")
            else:
                send_msg(msg)
        else:
            output_fn(do_decode(msg))


def main():
    bcast_address = None
    if len(sys.argv) > 1:
        bcast_address = sys.argv[1]

    run(bcast_address=bcast_address)

