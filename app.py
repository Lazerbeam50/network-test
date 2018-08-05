from twisted.internet import reactor, protocol

class Echo(protocol.Protocol):
    
    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        self.transport.write(data)


def main():
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(31563, factory)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
