'''
Created on 22 Jul 2018

@author: Femi
'''
from twisted.internet import reactor, protocol
from twisted.protocols import basic
from twisted.internet.task import LoopingCall
from sys import exc_info
import traceback

import pygame
from pygame.locals import *

class ValueHolder:
    def __init__(self):
        self.connectionMade = False
        self.dataSent = False
        self.errorRaised = False
        self.factory = None
        self.gameOver = False
        self.gameStarted = False
        self.opponentChoice = None
        self.playerChoice = None
        self.reactorStarted = False
        self.inbox = []
        self.textQueue = []

class GameServerProtocol(basic.LineReceiver):
    
    def connectionMade(self):
        global g
        g.values.connectionMade = True
        g.values.textQueue.append("Connection Successful!")
    
    def dataReceived(self, data): 
        
        data = str(data, "utf-8")
        finalData = int(data)
        
        global g
        g.values.inbox.append(finalData)
        
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
        pygame.init()
        
        self.screen = pygame.display.set_mode((800, 660))
        pygame.display.set_caption('RPS - Host')

        self.values.font = pygame.font.SysFont("Times New Roman", 14)
        
        self.group = pygame.sprite.Group()
        self.activeSprites = []
        
        self.rPressed = False
        self.pPressed = False
        self.sPressed = False
    
    def main_loop(self):
        try:
            events = pygame.event.get() #Handle pygame events
    
            for event in events:
                if event.type == QUIT: #Handle quit game
                    self.quit_game()
                elif event.type == KEYDOWN:
                    if event.key == ord("r"):
                        self.rPressed = True
                    elif event.key == ord("p"):
                        self.pPressed = True
                    elif event.key == ord("s"):
                        self.sPressed = True
                    
            self.screen.fill((0, 0, 255))
            self.group.draw(self.screen)
            
            pygame.display.update()
                    
            if self.values.connectionMade and not self.values.gameStarted:
                text1 = "Welcome to the game!"
                text2 = " "
                text3 = "Press 'r' for 'rock', 'p' for paper, and 's' for scissors"
                text = [text1, text2, text3]
                for t in text:
                    self.values.textQueue.append(t)
                self.values.gameStarted = True
                
            elif self.values.gameStarted and not self.values.gameOver:
                if len(self.values.inbox) > 0 and self.values.playerChoice != None:
                    self.janken()
                else:
                    data = 0
                    if self.rPressed:
                        data = 1
                    elif self.pPressed:
                        data = 2
                    elif self.sPressed:
                        data = 3
                    self.rPressed = False
                    self.pPressed = False
                    self.sPressed = False
                    if data != 0:
                        self.values.playerChoice = data
                        self.send_data(data)  
            
            if len(self.values.textQueue) > 0:
                self.render_text()

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
                self.quit_game()

    def send_data(self, data):
        if self.values.connectionMade and self.values.factory != None:
            if len(self.values.factory.protocols) > 0:
                toSend = str(data)
                toSend = bytes(toSend, "utf-8")
                self.values.factory.protocols[0].send_data(toSend)
                self.values.dataSent = True
                
    def quit_game(self):
        pygame.quit()
        reactor.stop()
        
    def render_text(self):
        if len(self.activeSprites) > 0:
            y = self.activeSprites[-1].rect.y + 20
        else:
            y = 0
        toRender = []
        for text in self.values.textQueue:
            image = self.values.font.render(text, True, (255, 255, 255))
            toRender.append(image)
        self.values.textQueue = []
        for image in toRender:
            sprite = GameSprite(image, (0, y, image.get_width(), image.get_height()))
            self.activeSprites.append(sprite)
            self.group.add(sprite)
            
            y += 20
            
    def janken(self):
        self.values.opponentChoice = self.values.inbox.pop(-1)
        
        if self.values.opponentChoice == self.values.playerChoice:
            if self.values.playerChoice == 1:
                self.values.textQueue.append("Both use Rock! Draw!")
            elif self.values.playerChoice == 2:
                self.values.textQueue.append("Both use Paper! Draw!")
            else:
                self.values.textQueue.append("Both use Scissors! Draw!")
            self.values.playerChoice = None
        elif ((self.values.playerChoice == 1 and self.values.opponentChoice == 3) or
              (self.values.playerChoice == 2 and self.values.opponentChoice == 1) or
              (self.values.playerChoice == 3 and self.values.opponentChoice == 2)):
            if self.values.playerChoice == 1:
                self.values.textQueue.append("You used rock, opponent used scissors. You win!")
            elif self.values.playerChoice == 2:
                self.values.textQueue.append("You used paper, opponent used rock. You win!")
            else:
                self.values.textQueue.append("You used scissors, opponent used paper. You win!")
            self.values.gameOver = True
        else:
            if self.values.playerChoice == 1:
                self.values.textQueue.append("You used rock, opponent used paper. You lose!")
            elif self.values.playerChoice == 2:
                self.values.textQueue.append("You used paper, opponent used scissors. You lose!")
            else:
                self.values.textQueue.append("You used scissors, opponent used rock. You lose!")
            self.values.gameOver = True
                
        print(self.values.inbox)
        self.values.inbox = []
        

class GameSprite(pygame.sprite.Sprite):
    def __init__(self, image, rect):
        pygame.sprite.Sprite.__init__(self)
        self.image = image
        self.rect = pygame.Rect(rect)
                
g = Game()
lc = LoopingCall(g.main_loop)
lc.start(0.033)         
g.values.factory = GameServerFactory()
reactor.listenTCP(8000, g.values.factory)
if not g.values.errorRaised:
    g.values.reactorStarted = True
    reactor.run()
else:
    pygame.quit()