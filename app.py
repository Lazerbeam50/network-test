from twisted.web import http
from twisted.internet import reactor

class Echo(http.HTTPChannel):
    
    def lineReceived(self, line):
        self.transport.write(line)
        
def main():
    factory = http.HTTPFactory()
    factory.protocol = Echo
    reactor.listenTCP(8080, factory)
    reactor.run()
    
if __name__ == '__main__':
    main()
