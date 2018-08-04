from twisted.internet import reactor, protocol
import os

class Echo(protocol.Protocol):
    """This is just about the simplest possible protocol"""
    
    def dataReceived(self, data):
        "As soon as any data is received, write it back."
        self.transport.write(data)


def main():
    """This runs the protocol on port 8000"""
    ip   = os.environ['OPENSHIFT_PYTHON_IP']
    port = int(os.environ['OPENSHIFT_PYTHON_PORT'])
    print(ip)
    print(port)
    factory = protocol.ServerFactory()
    factory.protocol = Echo
    reactor.listenTCP(port, factory, interface=ip)
    reactor.run()

# this only runs if the module was *not* imported
if __name__ == '__main__':
    main()
