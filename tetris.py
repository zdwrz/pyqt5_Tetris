#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, time, threading, random

from PyQt5 import QtCore, uic, QtWidgets
from PyQt5.QtGui import QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt, QPoint

Ui_game_screen, QtBaseClass = uic.loadUiType("tetris_main.ui" )
BLOCK_SIZE = 40
SCREEN_WIDTH = 600
# SCREEN_HIGHT = 800
BACKGROUND_COLOR = QColor(0, 0, 0, 80)
BOARDER_COLOR = QColor(0,10,10,20)
BLOCK_BOARDER_COLOR = QColor(100,100,200,255)
LEFT="LEFT"
RIGHT="RIGHT"
DOWN="DOWN"
SHAPE_TYPES = ["L","S","Z","I","O","T"]
GAME_WIDTH = 11
GAME_HEIGHT = 18
COLORS = [QColor(153,0,153,127),QColor(0,153,120,127),QColor(153,153,0,127),QColor(153,0,0,127)]
preColor = 0
SPEED = 200
class TPoint(QPoint):
	def __init__(self, x, y):
		super().__init__(x,y)
	def setColor(self, color):
		self.color = color

def getRandomColor():
	global preColor
	preColor += 1
	if preColor == len(COLORS):
		preColor = 0
	return COLORS[preColor]

def checkOverlapping(dotsA, dotsB):
	lst3 = [value for value in dotsA if value in dotsB] 
	# print(dotsA, dotsB,lst3)
	return len(lst3) > 0
	
class Shape:
	def __init__(self, type, locX, locY):
		self.locationX = locX
		self.locationY = locY
		self.dots = []
		self.isActive = True
		self.type = type
		if type == "L":
			self.dots.append( [TPoint(0,0), TPoint(0,1), TPoint(0,2), TPoint(1,2)] )
			self.dots.append( [TPoint(0,2), TPoint(1,2), TPoint(2,2), TPoint(2,1)] )
			self.dots.append( [TPoint(0,0), TPoint(1,0), TPoint(1,1), TPoint(1,2)] )
			self.dots.append( [TPoint(0,1), TPoint(0,2), TPoint(1,1), TPoint(2,1)] )
			self.maxTypeNo = 4
		elif type == "I":
			self.dots.append( [TPoint(1,0), TPoint(1,1), TPoint(1,2), TPoint(1,3)] )
			self.dots.append( [TPoint(0,1), TPoint(1,1), TPoint(2,1), TPoint(3,1)] )
			self.maxTypeNo = 2
		elif type == "Z":
			self.dots.append( [TPoint(0,0), TPoint(1,0), TPoint(1,1), TPoint(2,1)] )
			self.dots.append( [TPoint(0,1), TPoint(0,2), TPoint(1,0), TPoint(1,1)] )
			self.maxTypeNo = 2
		elif type == "S":
			self.dots.append( [TPoint(0,1), TPoint(1,0), TPoint(1,1), TPoint(2,0)] )
			self.dots.append( [TPoint(0,0), TPoint(0,1), TPoint(1,1), TPoint(1,2)] )
			self.maxTypeNo = 2
		elif type == "O":
			self.dots.append( [TPoint(0,1), TPoint(1,0), TPoint(1,1), TPoint(0,0)] )
			self.maxTypeNo = 1
		elif type == "T":
			self.dots.append( [TPoint(0,1), TPoint(1,0), TPoint(1,1), TPoint(2,1)] )
			self.dots.append( [TPoint(0,1), TPoint(1,0), TPoint(1,1), TPoint(1,2)] )
			self.dots.append( [TPoint(0,1), TPoint(1,2), TPoint(1,1), TPoint(2,1)] )
			self.dots.append( [TPoint(0,0), TPoint(0,1), TPoint(0,2), TPoint(1,1)] )
			self.maxTypeNo = 4
		self.currentDots = 0
		self.color = getRandomColor()
		for i in range(len(self.dots)):
			for d in self.dots[i]:
				d.setColor(self.color)

	def turn(self):
		if not self.isActive:
			return
		minLeft = min(self.dots[0 if self.currentDots + 1 == self.maxTypeNo else self.currentDots + 1], key=lambda d:d.x())
		maxRight = max(self.dots[0 if self.currentDots + 1 == self.maxTypeNo else self.currentDots + 1], key=lambda d:d.x())
		maxBottom = max(self.dots[0 if self.currentDots + 1 == self.maxTypeNo else self.currentDots + 1], key=lambda d:d.y())
		if self.locationX + minLeft.x() >= 0:
			if self.locationX + maxRight.x() + 1 <= GAME_WIDTH:
				if self.locationY + maxBottom.y() + 1 <= GAME_HEIGHT:
					if self.currentDots == self.maxTypeNo - 1:
						self.currentDots = 0
					else: self.currentDots += 1

	def move(self, direction):
		if not self.isActive:
			return
		if(direction == LEFT):
			minLeft = min(self.dots[self.currentDots], key=lambda d:d.x())
			if self.locationX + minLeft.x() > 0:
				self.locationX -= 1
		elif direction == RIGHT:
			maxRight = max(self.dots[self.currentDots], key=lambda d:d.x())
			if self.locationX + maxRight.x() + 1 < GAME_WIDTH:
				self.locationX += 1
		elif direction == DOWN:
			maxBottom = max(self.dots[self.currentDots], key=lambda d:d.y())
			if self.locationY + maxBottom.y() + 1 < GAME_HEIGHT:
				self.locationY += 1
			else: 
				self.isActive = False
				return False #Means this shape is inactive
		return True

class GameCore:
	def __init__(self, width, height):
		self.game_width = width
		self.game_height = height
		self.stack = []
		self.stackMap = {}
		self.shapeQueue = [Shape(SHAPE_TYPES[random.randint(0,5)],int(GAME_WIDTH/2) - 1,0),\
			Shape(SHAPE_TYPES[random.randint(0,5)],int(GAME_WIDTH/2) - 1,0)]
		self.activeShape = self.getNextShape()
		self.score = 0

	def turnShape(self):
		nextShape = Shape(self.activeShape.type, self.activeShape.locationX, self.activeShape.locationY)
		nextShape.currentDots = self.activeShape.currentDots
		nextShape.dots = self.activeShape.dots
		nextShape.turn()
		nextDots = []
		for d in nextShape.dots[nextShape.currentDots]:
			nextDots.append(TPoint(d.x()+self.activeShape.locationX, d.y()+self.activeShape.locationY))
		if not checkOverlapping(nextDots, self.stack):
			self.activeShape.turn()

	def moveActiveShape(self, direction):
		nextDots = []
		for d in self.activeShape.dots[self.activeShape.currentDots]:
			if(direction == LEFT):
				newP = TPoint(d.x() + self.activeShape.locationX - 1, d.y() + self.activeShape.locationY)
				nextDots.append(newP)	
			elif(direction == RIGHT):
				newP = TPoint(d.x() + self.activeShape.locationX + 1, d.y() + self.activeShape.locationY)
				nextDots.append(newP)	
			elif(direction == DOWN):
				newP = TPoint(d.x() + self.activeShape.locationX, d.y() + self.activeShape.locationY + 1)
				nextDots.append(newP)	
		if not checkOverlapping(nextDots, self.stack):
			if not self.activeShape.move(direction):
				self.consolidateShape()
		else: #has overlapping
			if self.activeShape.locationY == 0:
				return False
			if direction == DOWN:
				self.consolidateShape()
		return True

	def getNextShape(self):
		self.shapeQueue.append(Shape(SHAPE_TYPES[random.randint(0,5)],int(GAME_WIDTH/2) - 1,0))
		res = self.shapeQueue[0]
		self.shapeQueue.remove(res)
		return res

	def consolidateShape(self):
		for d in self.activeShape.dots[self.activeShape.currentDots]:
			newP = TPoint(d.x()+self.activeShape.locationX, d.y()+self.activeShape.locationY)
			newP.setColor(d.color)
			self.stack.append(newP)
			line = self.stackMap.get(newP.y())
			if not line :
				line = []
			line.append(newP)
			self.stackMap[newP.y()] = line	
		self.activeShape = self.getNextShape()
		# check complete line
		# print(self.stackMap)
		for i in range(GAME_HEIGHT):
			if self.stackMap.get(i) and len(self.stackMap.get(i)) == GAME_WIDTH:
				self.score += 1
				for d in self.stackMap.get(i):
					self.stack.remove(d)
				self.shiftDown(i)

	def shiftDown(self,lineNo):
		for d in self.stack:
			if d.y() < lineNo:
				d.setY(d.y()+1)
		#RE-GENERATE MAP
		self.stackMap.clear()
		for d in self.stack:
			line = self.stackMap.get(d.y())
			if not line :
				line = []
			line.append(d)
			self.stackMap[d.y()] = line	

				
class GameWindow(QtWidgets.QMainWindow, Ui_game_screen):
	def __init__(self):
		QtWidgets.QMainWindow.__init__(self)	
		# Ui_game_screen.__init__(self)
		self.setupUi(self)
		self.setWindowTitle("Tetris")
		self.game = GameCore(GAME_WIDTH,GAME_HEIGHT)
		self.pen_backgroud = QPen()
		self.pen_backgroud.setColor(BACKGROUND_COLOR)
		self.pen_boarder = QPen()
		self.pen_boarder.setColor(BOARDER_COLOR)
		self.startXOffSet = (SCREEN_WIDTH - self.game.game_width * BLOCK_SIZE) / 2
		self.timer = QtCore.QTimer()
		self.timer.timeout.connect(self.gameRun)
		self.timer.start(SPEED)

	def gameRun(self):
		if not self.game.moveActiveShape(DOWN):
			self.timer.stop() ## Game OVER
		self.update()

	def paintShape(self, shape, qp):
		for i in range(len(shape.dots[shape.currentDots])):
			qp.fillRect(self.startXOffSet + shape.locationX * BLOCK_SIZE + shape.dots[shape.currentDots][i].x() * BLOCK_SIZE, shape.locationY * BLOCK_SIZE + shape.dots[shape.currentDots][i].y() * BLOCK_SIZE,\
				 BLOCK_SIZE,BLOCK_SIZE, shape.color )
			qp.setPen(BLOCK_BOARDER_COLOR)
			qp.drawRect(self.startXOffSet + shape.locationX * BLOCK_SIZE + shape.dots[shape.currentDots][i].x() * BLOCK_SIZE, shape.locationY * BLOCK_SIZE + shape.dots[shape.currentDots][i].y() * BLOCK_SIZE,\
				 BLOCK_SIZE,BLOCK_SIZE)

	def paintEvent(self, e):
		qp = QPainter()
		qp.begin(self)
		#BACKGROUND
		qp.setPen(self.pen_backgroud)
		qp.fillRect(self.startXOffSet, 0,self.game.game_width * BLOCK_SIZE, self.game.game_height * BLOCK_SIZE, BACKGROUND_COLOR)
		#BOARDER
		qp.setPen(self.pen_boarder)
		for i in range(self.game.game_width):
			qp.drawLine(self.startXOffSet + BLOCK_SIZE * i, 0, self.startXOffSet  + BLOCK_SIZE * i, self.game.game_height * BLOCK_SIZE)
		for i in range(self.game.game_height):
			qp.drawLine(self.startXOffSet,BLOCK_SIZE * i, self.startXOffSet  + self.game.game_width * BLOCK_SIZE, BLOCK_SIZE * i)
		#Active Shape
		self.paintShape(self.game.activeShape, qp)#, start_x + 2 * BLOCK_SIZE, 10 * BLOCK_SIZE)
		#Stack
		for d in self.game.stack:
			qp.fillRect(self.startXOffSet +  d.x() * BLOCK_SIZE,  d.y() * BLOCK_SIZE,\
				 BLOCK_SIZE,BLOCK_SIZE, d.color )
			qp.setPen(BOARDER_COLOR)
			qp.drawRect(self.startXOffSet + d.x() * BLOCK_SIZE, d.y() * BLOCK_SIZE,\
				 BLOCK_SIZE,BLOCK_SIZE)
		#Shape Queue
		for i in self.game.shapeQueue[0].dots[self.game.shapeQueue[0].currentDots]:
			qp.fillRect(10 + 20 * i.x() , 10 + i.y() * 20, 20,20, self.game.shapeQueue[0].color )
			qp.setPen(BLOCK_BOARDER_COLOR)
			qp.drawRect(10 + 20 * i.x() , 10 + i.y() * 20, 20,20)
		for i in self.game.shapeQueue[1].dots[self.game.shapeQueue[1].currentDots]:
			qp.fillRect(10 + 10 * i.x() , 100 + i.y() * 10, 10,10, self.game.shapeQueue[1].color )
		#Score
		qp.setPen(COLORS[1])
		qp.drawText(30, 250, str(self.game.score))
		qp.end()

	def keyPressEvent(self, event):
		key_press = event.key()
		if ( key_press == Qt.Key_W or key_press == Qt.Key_Up ):
			self.game.turnShape()
		elif ( key_press == Qt.Key_D or key_press == Qt.Key_Right ):
			self.game.moveActiveShape(RIGHT)
		elif ( key_press == Qt.Key_A or key_press == Qt.Key_Left ):
			self.game.moveActiveShape(LEFT)
		elif ( key_press == Qt.Key_S or key_press == Qt.Key_Down ):
			self.game.moveActiveShape(DOWN)
		elif ( key_press == Qt.Key_Space):
			if self.timer.isActive():self.timer.stop()
			else: self.timer.start()
		self.update()

if __name__ == "__main__":
	app = QtWidgets.QApplication(sys.argv)
	gameWindow = GameWindow()
	gameWindow.show()
	sys.exit(app.exec_())