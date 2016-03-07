# -*- coding: utf-8 -*-
import SocketServer
import time
import json
import re

"""
Variables and functions that must be used by all the ClientHandler objects
must be written here (e.g. a dictionary for connected clients)
"""


class ClientHandler(SocketServer.BaseRequestHandler):
    """
    This is the ClientHandler class. Everytime a new client connects to the
    server, a new ClientHandler object will be created. This class represents
    only connected clients, and not the server itself. If you want to write
    logic for the server, you must write it outside this class
    """

    # set in login method
    username = ""
    ip = ""
    port = 0
    connection = None

    def handle(self):
        """
        This method handles the connection between a client and the server.
        """
        self.ip = self.client_address[0]
        self.port = self.client_address[1]
        self.connection = self.request

        # Adds the connection to the list in server
        server.connectedClients.append(self)

        # Loop that listens for messages from the client
        while True:
            try:
                received0 = self.connection.recv(4096)
                # I do this to not get empty receives, it happened and crashed the program every time
                if not re.match("{.+", received0):
                    continue

                received = json.loads(received0)

                if received['request'] == 'login':
                    if self.username != "":
                        print("allrdy logged in")
                        self.error('You are allready logged in.')
                    else:
                        # If request from received payload was login -> do it
                        self.login(received['content'])

                elif received['request'] == 'logout':
                    # If request from received payload was logout -> do it
                    self.logout()

                elif received['request'] == 'names':
                    # If request from received payload was names -> provide list of all connected users names
                    self.names()

                elif received['request'] == 'help':
                    # If request from received payload was names -> provide list of all connected users names
                    self.help()

                elif received['request'] == 'msg':
                    # If request from received payload was names -> provide list of all connected users names
                    self.msg(received['content'])

                elif received['request'] == 'history':
                    # If request from received payload was names -> provide list of all connected users names
                    self.history()

            except Exception as e:
                print(e.message)
                self.logout()
                break

    # This logout method removes the client from the session.
    def logout(self):
        if self.username is None:
            return
        if self not in server.connectedClients:
            return
        if self in server.connectedClients:
            server.connectedClients.remove(self)
        if self.username in server.active_names:
            server.active_names.remove(self.username)
        self.connection.close()
        print self.username, 'logged out'

        # Create logout message to be broadcasted to remaining users
        message = {'timestamp': int(time.time()),
                   'sender': 'Server',
                   'response': 'info',
                   'content': self.username + ' logged out'}

        # Broadcast a logout message to remaining users
        for remainingUser in server.connectedClients:
            remainingUser.send(json.dumps(message))

    def names(self):
        if self.username not in server.active_names:
            self.error('log in to see names')
        else:
            names = ""
            for user in server.connectedClients:
                names += user.username + ", "
            names = names[:-2]
            payload = json.dumps({'timestamp': int(time.time()), 'sender': '[Server]', 'response': 'info', 'content': 'Connected users: '+names})
            self.send(payload)

    def login(self, message_content):
        # Check and set valid name
        if re.match("^[A-Za-z0-9_-]+$", message_content) and message_content not in server.active_names:
            self.username = message_content
            server.active_names.append(self.username)
            print self.username, 'connected'

            # Broadcast "user connected" message
            message = {'timestamp': int(time.time()), 'sender': 'Server', 'response': 'info',
                       'content': self.username + ' connected'}
            payload = json.dumps(message)

            for client in server.connectedClients:
                client.send(payload)

        else:
            if message_content in server.active_names:
                self.error('username taken')
            else:
                self.error('invalid username')

    def help(self):
        payload = json.dumps({'timestamp': int(time.time()), 'sender': '[Help]', 'response': 'info',
                              'content': 'Availeable commands: login "username", logout, names, help, '
                                         'msg "message"'})
        self.send(payload)

    def msg(self, message):
        if self.username == "":
            message = json.dumps({'timestamp': int(time.time()), 'sender': 'Server', 'response': 'err',
                                  'content': "log in to send messages"})
            self.send(message)

        else:
            message = json.dumps({'timestamp': int(time.time()), 'sender': self.username, 'response': 'msg',
                                  'content': message})

            # Add the message to the history
            server.history.append(message)

            for user in server.connectedClients:
                # if user != self:  - After re reading the task I guess I should remove this line?
                # The line makes the server not send the messageback to the one who sent it
                    # Only logged in users receive messages
                    if user.username in server.active_names:
                        user.send(message)

    def error(self, errormessage):

        message = json.dumps({'timestamp': int(time.time()), 'sender': 'Server', 'response': 'err',
                              'content': errormessage})
        self.send(message)

    def history(self):
        if self.username in server.active_names:
            for message in server.history:
                # The sleep prevents the program from crashing when sending multiple packets.
                time.sleep(0.2)
                self.send(message)
        else:
            message = json.dumps({'timestamp': int(time.time()), 'sender': 'Server', 'response': 'err',
                                  'content': "log in to see history"})
            self.send(message)

    def send(self, data):
            self.connection.send(data)


class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    """
    This class is present so that each client connected will be ran as a own
    thread. In that way, all clients will be served by the server.

    No alterations are necessary
    """
    allow_reuse_address = True

    # connectedClients stores all clients that are connected to the server at any given tim
    connectedClients = []
    active_names = []

    # History stores all messages sent since server restart.
    history = []

if __name__ == "__main__":
    """
    This is the main method and is executed when you type "python Server.py"
    in your terminal.

    No alterations are necessary
    """
    HOST, PORT = 'localhost', 9998
    print 'Server running...'

    # Set up and initiate the TCP server
    server = ThreadedTCPServer((HOST, PORT), ClientHandler)
    server.serve_forever()
