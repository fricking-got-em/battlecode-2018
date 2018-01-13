#First bot testing MINE
import battlecode as bc
import random
import sys
import traceback
import numpy as np

import os
print(os.getcwd())

print("Starting...")
gc = bc.GameController()
dir = list(bc.Direction)

myTeam = gc.team()

error = False
units = np.array([])
workers = np.array([])
knights = np.array([])
rangers = np.array([])
mages = np.array([])
healers = np.array([])
factories = np.array([])
rockets = np.array([])

totalUnits = 0
previousUnits = 0

class Unit:
	
	uCount = 0
	
	def __init__(self, id, unit):
		self.id = id
		self.unit = unit
		#uCount = uCount + 1
		
	def actionType(self, type):
		self.type = type
	
class Worker(Unit):

	count = 0
	
	def __init__(self, id, unit):
		super().__init__(id, unit)
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
	
	#Builds a factory in the specified direction, if not build in any direction
	def blueprintFactory(self, *direction):
		global factories
		
		if direction != ():
			directions = direction
		else:
			directions = list(bc.Direction)
		
		for d in directions:
			if gc.can_blueprint(self.unit.id, bc.UnitType.Factory, d):
				gc.blueprint(self.unit.id, bc.UnitType.Factory, d)
				print("Blueprinted")
				return True
				break
		
		print("Failed to blueprint")
		return False
	
	#Builds whatever factory is nearby	
	def buildFactory(self):
		near = gc.sense_nearby_units(unit.location.map_location(), 1)
		for i in near:
			if gc.can_build(unit.id, i.id):
				gc.build(unit.id, i.id)
				print("Building")
		
		
class Knight(Unit):

	count = 0
	
	def __init__(self, id, unit):
		super().__init__(id, unit)
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
		
class Ranger(Unit):

	count = 0
	
	def __init__(self, id, unit):
		super().__init__(id, unit)
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)

class Mage(Unit):
	
	count = 0
	
	def __init__(self, id, unit):
		super().__init__(id, unit)
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
		
class Healer(Unit):
	
	count = 0
	
	def __init__(self, id, unit):
		super().__init__(id, unit)
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
		
class Factory(Unit):
	
	count = 0
	
	def __init__(self, id, unit):
		super().__init__(id, unit)
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
		
class Rocket(Unit):
	
	count = 0
	
	def __init__(self, id, unit):
		super().__init__(id, unit)
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)

#Adds the new units created to their respectice unit lists
def refreshUnits():
	global workers
	global knights
	global rangers
	global mages
	global healers
	global factories
	global rockets
	
	#This seems super inefficient but I can't think of a better way to do it
	units = np.array([])
	workers = np.array([])
	knights = np.array([])
	rangers = np.array([])
	mages = np.array([])
	healers = np.array([])
	factories = np.array([])
	rockets = np.array([])
	
	for unit in gc.my_units():
		type = unit.unit_type
		
		#Adds the units to one respective unit array
		np.append(units, Unit(unit.id, unit))
		
		#Separates the units into separate arrays
		if type == bc.UnitType.Worker:
			workers = np.append(workers, [Worker(unit.id, unit)])
		elif type == bc.UnitType.Knight:
			knights = np.append(knights, [Knight(unit.id, unit)])
		elif type == bc.UnitType.Ranger:
			rangers = np.append(rangers, [Ranger(unit.id, unit)])
		elif type == bc.UnitType.Mage:
			mages = np.append(mages, [Mage(unit.id, unit)])
		elif type == bc.UnitType.Healer:
			healers = np.append(healers, [Healer(unit.id, unit)])
		elif type == bc.UnitType.Factory:
			factories = np.append(factories, [Factory(unit.id, unit)])
		elif type == bc.UnitType.Rocket:
			rockets = np.append(rockets, [Rocket(unit.id, unit)])
	

while True:
	round = gc.round()
	print("Round: " + str(round))

	try:
		totalUnits = len(gc.my_units())
		
		if round == 1:
			refreshUnits()
			totalUnits = len(gc.my_units())
			previousUnits = len(gc.my_units())
		elif gc.planet() == bc.Planet.Earth:
			print("Workers: " + str(np.size(workers)))
			print(gc.karbonite())
			workers[0].blueprintFactory(dir[0])
		
		if totalUnits != previousUnits:
			refreshUnits()
			previousUnits = len(gc.my_units())
			print("Units Refreshed: " + str(totalUnits))
		
		
	except Exception as e:
		if error == False:
			print("Error:",e)
	
			#This shows where the error was
			traceback.print_exc()
			error = True
		
	gc.next_turn()
	
	sys.stdout.flush()
	sys.stderr.flush()
