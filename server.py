from twisted.internet import reactor
from twisted.internet.protocol import ServerFactory, connectionDone
from twisted.protocols.basic import LineOnlyReceiver


class ServerProtocol(LineOnlyReceiver):
    factory: 'Server'
    login: str = None

    def lineReceived(self, line: bytes):
        content = line.decode().strip()

        if content == "":
            return

        if self.login is not None:
            content = f"Message from {self.login}: {content}"
            self.factory.history.append(content)

            for user in self.factory.clients:
                if user is not self and user.login is not None:
                    user.sendLine(content.encode())
        else:
            if content.startswith("login:"):
                temp_login = content.replace("login:", "").lstrip()

                if temp_login != "" and self.is_login_free(temp_login):
                    self.login = temp_login
                    self.sendLine(f"Welcome, {self.login}!".encode())
                    self.send_history()
                else:
                    self.sendLine(f"Login '{temp_login}' is invalid or taken. Try another one.".encode())
            else:
                self.sendLine("Unauthorized.".encode())

    def connectionLost(self, reason=connectionDone):
        self.factory.clients.remove(self)

    def connectionMade(self):
        self.factory.clients.append(self)

    def is_login_free(self, login):
        for client in self.factory.clients:
            if login == client.login:
                return False

        return True

    def send_history(self):
        for message in self.factory.history[-10:]:
            self.sendLine(message.encode())


class Server(ServerFactory):
    protocol = ServerProtocol
    clients: list
    history: list

    def startFactory(self):
        self.clients = []
        self.history = []
        print("Server started")

    def stopFactory(self):
        print("Server closed")


reactor.listenTCP(1234, Server())
reactor.run()
