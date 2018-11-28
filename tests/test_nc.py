import pytest
import queue
import threading

from socketserver import StreamRequestHandler, TCPServer

from netconsole import Netconsole


class NetconsoleServerHandler(StreamRequestHandler):
    def handle(self):
        q = self.server.msg_queue

        while True:
            item = q.get(timeout=2.0)
            if item is None:
                self.server.done_queue.put(None)
                return

            self.wfile.write(item)
            self.wfile.flush()


class NetconsoleServer(TCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.msg_queue = queue.Queue()
        self.done_queue = queue.Queue()

        self.seq = 0

    # Python < 3.6 compatibility
    if not hasattr(TCPServer, "__enter__"):

        def __enter__(self):
            return self

        def __exit__(self, *args):
            self.server_close()

    def start(self):
        th = threading.Thread(target=self.serve_forever)
        th.start()

    #
    # Write routines: not particularly efficient, but they don't need to be
    #

    def _pack_frame(self, tag, buf):
        blen = len(buf) + 1
        msg = Netconsole._header.pack(blen, tag) + buf
        self.msg_queue.put(msg)

    def _pack_str(self, s):
        if not isinstance(s, bytes):
            s = bytes(s, "utf-8")
        return Netconsole._slen.pack(len(s)) + s

    def write_err(self, ts, numOcc, errCode, flags, details, location, callStack):
        seq = self.seq
        self.seq += 1

        buf = Netconsole._errorFrame.pack(ts, seq, numOcc, errCode, flags)
        buf += self._pack_str(details)
        buf += self._pack_str(location)
        buf += self._pack_str(callStack)
        self._pack_frame(Netconsole.TAG_ERROR, buf)

    def write_info(self, ts, msg):
        if not isinstance(msg, bytes):
            msg = bytes(msg, "utf-8")

        seq = self.seq
        self.seq += 1
        buf = Netconsole._infoFrame.pack(ts, seq) + msg
        self._pack_frame(Netconsole.TAG_INFO, buf)

    def write_done(self):
        self.msg_queue.put(None)


@pytest.fixture
def ncserver():
    with NetconsoleServer(("127.0.0.1", 0), NetconsoleServerHandler) as server:
        server.start()
        yield server
        server.shutdown()


def test_nc_basic(ncserver):

    host, port = ncserver.server_address
    q = queue.Queue()

    # start the client
    nc = Netconsole(printfn=q.put)
    nc.start(host, port, block=False)

    # send a normal message
    ncserver.write_info(1, "normal message")

    # send an error message
    ncserver.write_err(2, 1, 2, 0, "details", "location", "callstack")

    # send a normal message
    ncserver.write_info(3, "normal message")

    ncserver.write_done()

    # wait for 2 seconds for it to be sent
    ncserver.done_queue.get(timeout=2.0)

    # Retrieve 3 messages
    assert q.get() == "[1.00] normal message"
    assert q.get() == "[2.00] 2 details location callstack"
    assert q.get() == "[3.00] normal message"

    # Test reconnect
    ncserver.shutdown()
    ncserver.start()

    ncserver.write_info(4, "another message")
    ncserver.write_done()

    # wait for 2 seconds for it to be sent
    ncserver.done_queue.get(timeout=2.0)

    # Retrieve 1 message
    assert q.get() == "[4.00] another message"

    # shut it down
    nc.stop()
