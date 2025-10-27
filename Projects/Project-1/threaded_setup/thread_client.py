from socket import socket, AF_INET, SOCK_STREAM

serverHost = 'localhost'
serverPort = 50007

class ThreadClient():
    def __init__(self, host: str=serverHost, port: int=serverPort):
        self.serverHost = host
        self.serverPort = port
        self.server_socket: None | socket = None

    def connectToServer(self):
        '''Establishes connection to the server'''
        if self.server_socket is not None:  # already connected
            print(f'Already connected to server at {self.server_socket.getpeername()}')
            return self.server_socket

        sock = socket(AF_INET, SOCK_STREAM)  # create socket

        try:
            sock.connect((self.serverHost, self.serverPort))    # connect to server
        except Exception as e:
            print('Error connecting to server:', e)
            return None
        
        print(f'Connected to server at {(self.serverHost, self.serverPort)}, waiting in queue...')
        
        reply = sock.recv(1024).decode()    # wait for server readiness message
        if reply == '200 OK':
            print('Server ready.')
        
        self.server_socket = sock   # update connected socket
        return sock

    def closeConnection(self) -> bool:
        '''Closes the connection to the server'''
        if self.server_socket is not None:
            self.server_socket.close()
            self.server_socket = None
            print('Connection closed')
            return True
        
        print('Connection already closed')
        return False

    def start_client(self):
        '''Starts the client, handles user input to send messages to server'''
        sock = self.connectToServer()
        if sock is None:
            print('Exiting client, connection failed')
            return
        
        try:
            while True:
                # read user input
                message = input('Enter message to send to server ("exit()" to quit, "reconnect()" to reconnect): ')
                
                if sock is None:    # if not connected, prompt to reconnect
                    print('No connection to server. Use "reconnect()" to reconnect or "exit()" to quit.')
                    continue
                
                if message.lower() == 'exit()':  # exit command
                    break
                
                if message.lower() == 'reconnect()':    # reconnect command
                    sock = self.connectToServer()
                    if sock is None:
                        print('Reconnection failed. Try again or exit.')
                    continue
                
                if message.strip() == '':   # empty message causes freeze so skip
                    print('Please enter a non-empty message.')
                    continue
                
                try:
                    sock.send(message.encode())  # send message to server
                except Exception as e:
                    print('Error sending message to server:', e)
                    continue

                try:
                    reply = sock.recv(1024).decode()    # receive server reply
                    while reply.endswith('\n') is False:  # keep receiving until full reply is obtained
                        reply += sock.recv(1024).decode()
                    
                    print('Server reply:\n', reply)
                        
                except Exception as e:
                    print('Error receiving server reply:', e)
        finally:
            self.closeConnection()

if __name__ == '__main__':
    client = ThreadClient()
    client.start_client()