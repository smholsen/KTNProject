# -*- coding: utf-8 -*-
import socket
from MessageReceiver import MessageReceiver
import json


class Client:
    """
    This is the chat client class
    """

    host = ""
    server_port = 0
    thread = None

    def __init__(self, host, server_port):
        """
        This method is run when creating a new Client object
        """

        # Set up the socket connection to the server
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        self.host = host
        self.server_port = server_port
        
        # TODO: Finish init process with necessary code - I think done, maybe?
        self.run()

    def run(self):
        # Initiate the connection to the server
        self.connection.connect((self.host, self.server_port))
        # Sets up a unique thread
        self.thread = MessageReceiver(self, self.connection)

        # Start listening for messages
        self.thread.start()

        # Listen for and respond to input
        while True:
            inputvalue = raw_input().split(' ', 1)
            action = inputvalue[0]

            # command might only be 1 word
            try:
                content = inputvalue[1]
            except Exception as e:
                pass

            if action == 'login':
                if self.thread.isActive is False:
                    print('Re-Run the program to reconnect.')
                    return
                payload = json.dumps({'request': 'login', 'content': content})
                self.send_payload(payload)

            elif action == 'logout':
                payload = json.dumps({'request': 'logout'})
                self.send_payload(payload)
                self.disconnect()
                print('disconnected')

            elif action == 'names':
                payload = json.dumps({'request': 'names'})
                self.send_payload(payload)

            elif action == 'help':
                payload = json.dumps({'request': 'help'})
                self.send_payload(payload)

            elif action == 'msg':
                payload = json.dumps({'request': 'msg', 'content': content})
                self.send_payload(payload)

            elif action == 'history':
                payload = json.dumps({'request': 'history'})
                self.send_payload(payload)

            else:
                print('Unknown command, type "help" for help')

    def disconnect(self):

        self.connection.close()
        self.thread.isActive = False

        # Now it will not be possible to reconnect without re-running.

        pass

    def receive_message(self, message):
        # TODO: Handle incoming message
        # If there is no readable value just ignore
        try:
            message = json.loads(message)
        except Exception as e:
            return
        if message['response'] == 'msg':
            print message['sender'] + ':', message['content']
        elif message['response'] == 'info':
            print '[INFO]', message['content']
        elif message['response'] == 'err':
            print '[ERROR]', message['content']

    def send_payload(self, data):
        # TODO: Handle sending of a payload
        # Assuming data is now formatted as JSON
        # Send TCP Header

        self.connection.send(data)
        pass
        
    # More methods may be needed!


if __name__ == '__main__':
    """
    This is the main method and is executed when you type "python Client.py"
    in your terminal.

    No alterations are necessary
    """

    print('Type "login username" to log in')

    client = Client('localhost', 9998)


