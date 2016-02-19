# -*- coding: utf-8 -*-
from threading import Thread


class MessageReceiver(Thread):
    """
    This is the message receiver class. The class inherits Thread, something that
    is necessary to make the MessageReceiver start a new thread, and it allows
    the chat client to both send and receive messages at the same time
    """

    client = None
    connection = None
    isActive = True

    def __init__(self, client, connection):
        """
        This method is executed when creating a new MessageReceiver object
        """

        # Flag to run thread as a deamon
        Thread.__init__(self)
        self.daemon = True

        # TODO: Finish initialization of MessageReceiver - Dont know what more is needed, if anything

        self.client = client
        self.connection = connection

    def run(self):
        # TODO: Make MessageReceiver receive and handle payloads
        # Loop while the connection is alive
        while self.isActive:

            # Sets the variable msg = to what is received from the connection

            # I am a lazy piece of shit so I just ignore the exception (which occurs when logging out)
            try:
                msg = self.connection.recv(4096)

            except Exception as e:
                print(e.message)
                print('An error occured with connection to the server, please try to re-run')
                break

            # If there is no message, break out of the loop.
            if msg is None:
                break

            # If there is a message, then pass it on
            else:
                self.client.receive_message(msg)
        pass
