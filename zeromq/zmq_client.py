"""
Tuna's ZeroMQ client module.

Classes:
zmq_client -- zmq client that uses (stub) proxy for communication.
"""

import zmq

class zmq_client ( ):
    """
    Sets zmq context, connects to (stub) proxy and sends messages.

    Public methods:
    log -- sends message to logging server.
    """

    def __init__ ( self ):
        self.zmq_context = zmq.Context ( )
        self.zmq_socket_req = self.zmq_context.socket ( zmq.REQ )
        self.zmq_socket_req.connect ( "tcp://127.0.0.1:5000" )
        
    def log ( self, msg ):
        """
        Sends (byte string) message to log_server through the (stub) proxy.
        """

        prefixed_msg = b"log: " + msg
        self.zmq_socket_req.send ( prefixed_msg )
        answer = self.zmq_socket_req.recv ( )
        if answer.decode("utf-8") != 'ACK':
            print ( u'Something is fishy!' )
            print ( u'Received: "%s".' % answer.decode("utf-8") )
            print ( u"Expected: 'ACK'" )

def main ( ):
    pass

if __name__ == "__main__":
    main ( )