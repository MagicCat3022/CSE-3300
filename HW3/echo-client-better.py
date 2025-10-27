#!/usr/bin/env python3
#
# COMP 332, Fall 2018
# Wesleyan University
#
# Simple echo client that makes a connection to an echo server,
# sends a string to the server, then terminates
#
# Usage:
#   python3 echo_client.py <server_host> <server_port>
#

import socket
import sys

class EchoClient():

    def __init__(self, server_host, server_port):
        self.start(server_host, server_port)

    def start(self, server_host, server_port):

        # Try to connect to echo server
        try:
            server_sock = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
            server_sock.connect((server_host, server_port))
        except OSError as e:
            print ('Unable to connect to socket: ', e)
            if server_sock:
                server_sock.close()
            sys.exit(1)

        # Send message string to server over socket
        str_msg = 'Hello, world'
        bin_msg = str_msg.encode('utf-8')
        server_sock.sendall(bin_msg)

        # Get response data from server and print it
        bin_resp = server_sock.recv(1024)
        str_resp = bin_resp.decode('utf-8')
        print ('Client received', str_resp)

        # Close server socket
        server_sock.close()

def main():

    # Echo server socket parameters
    server_host = 'localhost'
    server_port = 50006

    # Parse command line parameters if any
    if len(sys.argv) > 1:
        server_host = sys.argv[1]
        server_port = int(sys.argv[2])

    # Create EchoClient object
    client = EchoClient(server_host, server_port)

if __name__ == '__main__':
    main()
