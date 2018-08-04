'''
Created on 27 Jul 2018

@author: Femi
'''
from twisted.internet import reactor, protocol
from twisted.protocols import basic
from twisted.internet.task import LoopingCall
from sys import exc_info
import traceback

class ValueHolder:
    def __init__(self):
        self.connectionMade = False
        self.dataSent = False
        self.errorRaised = False
        self.factory = None
        self.reactorStarted = False
        self.warriorSent = False

class GameServerProtocol(basic.LineReceiver):
    
    def connectionMade(self):
        print("Connection Successful!")
        global g
        g.values.connectionMade = True
        self.transport.write(b"Hey there! You're connected to the server.")
    
    def dataReceived(self, data):
        
        data = str(data, "utf-8")
        print("Message received:", data)
        
    def send_data(self, data):
        self.transport.write(data)
        
class GameServerFactory(protocol.ServerFactory):
    
    protocol = GameServerProtocol
    
    def buildProtocol(self, addr):
        proto = protocol.ServerFactory.buildProtocol(self, addr)
        self.protocols = [proto]
        return proto
        
class Game:
    def __init__(self):
        self.values = ValueHolder()
    
    def main_loop(self):
        try:
            if not self.values.warriorSent and self.values.factory != None:
                self.send_message("A warrior has invaded your game!")
                if self.values.dataSent:
                    self.values.warriorSent = True
                    self.values.dataSent = False
        except Exception:
            tb = exc_info()
            print("Error found in main loop")
            print()
            print("Error type:", tb[0])
            print("Error value:", tb[1])
            l = traceback.format_tb(tb[2])
            for line in l:
                print(line)
            self.values.errorRaised = True
            if self.values.reactorStarted:
                reactor.stop()

    def send_message(self, message):
        if self.values.connectionMade:
            if len(self.values.factory.protocols) > 0:
                data = bytes(message, "utf-8")
                self.values.factory.protocols[0].send_data(data)
                self.values.dataSent = True
                
g = Game()
lc = LoopingCall(g.main_loop)
lc.start(0.033)         
g.values.factory = GameServerFactory()
#g.values.factory.protocol = GameServerProtocol
reactor.listenTCP(8000, g.values.factory)
if not g.values.errorRaised:
    g.values.reactorStarted = True
    reactor.run()
else:
    pass
