import time, _thread as thread
import threading
from socket import socket, AF_INET, SOCK_STREAM
from concurrent.futures import ThreadPoolExecutor

myHost = 'localhost'
myPort = 50007

def now():
    return time.ctime(time.time())

class ThreadServer():
    def __init__(self, host: str=myHost, port: int=myPort):
        self.host = host
        self.port = port
        self.word_set = self.get_word_list()
        
    def get_word_list(self) -> list[str]:
        '''Loads word list from file into a set'''
        word_list = []
        
        with open('../wordlist.txt', 'r') as f:
            words = f.read().splitlines()   # Read lines without trailing newlines and store each line as an element in a list
            for word in words:
                word_list.append(word)  # add each word to the list

        return word_list

    def checkWord(self, word: str, target: str) -> bool:
        '''Checks if a word matches the target pattern'''
        target_len = len(target)
        word_len = len(word)
        if word_len != target_len:
            return False
        
        for i in range(word_len):
            if target[i] == '?':        # wildcard character can be ignored since it can be anything
                continue

            if word[i] != target[i]:    # if any mismatch (not wildcard), word can NOT be a match
                return False
            
        return True

    def findQuery(self, target: str) -> tuple[list[str], int]:
        '''Return all words matching the target pattern in the word set and the number of matches'''
        word_list = []  # list of words that match the target pattern
        matches = 0     # number of words that match the target pattern
        for word in self.word_set:
            if self.checkWord(word, target):
                word_list.append(word)
                matches += 1

        return word_list, matches

    def handleClient(self, connection: socket):
        '''Handles single client connection'''
        try:
            connection.send('200 OK'.encode())  # initial handshake to inform client that server is ready
            
            while True:
                try:
                    data = connection.recv(1024)    # receive data from client (their pattern query)
                except Exception as e:
                    print('Error receiving data from client:', e)
                    break
                if not data: break

                words, matches = self.findQuery(data.decode())  # find all words matching the client's pattern query
                
                reply = f" (Total matches: {matches})\n"    # format reply message
                if matches > 0:
                    reply += ', '.join(words)
                reply += '\n'
                
                connection.send(reply.encode()) # send reply to client
                
            print('Client at', connection.getpeername(), 'disconnected at', now())  # log disconnection of client and time
        
        finally:    # ensure connection is closed and logged
            print('Closing connection...')
            connection.close()  

    def dispatcher(self):
        '''Starts the server, listen for incoming connections, handle clients concurrently using threads'''
        print('Starting server on %s:%s' % (myHost, myPort))
        
        try:    # start server socket and listen for connections
            client_socket = socket(AF_INET, SOCK_STREAM)
            client_socket.bind((self.host, self.port))
            client_socket.listen(5)
            client_socket.settimeout(1.0)  # set timeout to allow periodic checks for shutdown
            print('Server started up on %s at %s' % (self.host, now()))
        except Exception as e:
            print('Error starting server:', e)
            return

        with ThreadPoolExecutor(max_workers=1) as executor:
            try:
                while True:
                    try:
                        connection, address = client_socket.accept()    # accept incoming client connection
                    except TimeoutError:    # allow loop to continue on timeout
                        continue
                    print(f'Server connected with {address} at {now()}')
                    executor.submit(self.handleClient, connection)  # handle client connection in a separate thread
            except KeyboardInterrupt:
                print('Server shutting down...')
            finally:
                client_socket.close()  # stop accepting new connections
                executor.shutdown(wait=True)    # wait for any current clients to finish
                print('Server socket closed.')

if __name__ == '__main__':
    server = ThreadServer()
    server.dispatcher()