#First bot testing MINE
#NEWWWW
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

EarthMap = gc.starting_map(bc.Planet.Earth)
karnoniteLocations = np.array([])

#Scan for karbonite
for x in range(EarthMap.width - 1):
	for y in range(EarthMap.height - 1):
		if EarthMap.initial_karbonite_at(bc.MapLocation(bc.Planet.Earth, x, y)) > 0:
			karnoniteLocations = np.append(karnoniteLocations, bc.MapLocation(bc.Planet.Earth, x, y))
			

totalUnits = 0
previousUnits = 0
maxFactory = 1

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
		self.path = []
		self.first = True
		self.pathCount = 0
		self.closestLoc = 0
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
	
	#Builds a factory in the specified direction, if not build in any direction
	def blueprintFactory(self, *direction):
		global factories
		
		if self.unit.location.is_on_map():
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
		else:
			return False
	
	#Builds whatever factory is nearby	
	def buildFactory(self):
		if self.unit.location.is_on_map():
			near = gc.sense_nearby_units(self.unit.location.map_location(), 1)
			for i in near:
				if gc.can_build(self.unit.id, i.id):
					gc.build(self.unit.id, i.id)
					print("Building")
		else:
			return False
			
	def mineKarbonite(self):
		global EarthMap
		global karnoniteLocations
		global gc
		
		if self.unit.location.is_on_map():
			if self.path != []:
				if self.pathCount < len(self.path):
					if gc.can_move(self.id, self.path[self.pathCount]) and gc.is_move_ready(self.id):	
						gc.move_robot(self.id, self.path[self.pathCount])
						self.pathCount = self.pathCount + 1
					else:
						print("Can't Move : " + str(self.id) + " Direction: " + str(self.path[self.pathCount]))
						
				else:
					if gc.can_harvest(self.id, self.path[len(self.path) - 1]):
						gc.harvest(self.id, self.path[len(self.path) - 1])
						print("Harvesting..." + str(self.id))
					else:
						self.path = []
						self.pathCount = 0
						print("Can't harvest more..." + str(self.id))
			else:
				pLoc = self.unit.location.map_location()
				closestDist = pLoc.distance_squared_to(karnoniteLocations[0])
				self.closestLoc = 0
				for i in range(1, len(karnoniteLocations)):
					dist = pLoc.distance_squared_to(karnoniteLocations[i])
					if dist < closestDist:
						closestDist = dist
						self.closestLoc = i
				self.navigateToPoint(karnoniteLocations[self.closestLoc])
				print("NewLoc: " + str(self.closestLoc) + " " + str(karnoniteLocations[self.closestLoc]) + " : " + str(self.id))
				karnoniteLocations = np.delete(karnoniteLocations, [self.closestLoc])
				
		else:
			return False
		
	def navigateToPoint(self, dLoc):
		global EarthMap
		if self.unit.location.is_on_map():
			pLoc = self.unit.location.map_location()
			
			while True:
				if pLoc.distance_squared_to(dLoc) == 0:
					n = 0
					for i in self.path:
						if type(i) == type(1):
							self.path[n] = self.convertToDirection(i)
						print(str(i) + " : " + str(self.id))
						n = n + 1
					return True
				#print(str(pLoc) + " <> " + str(dLoc) + " : " + str(self.id))		
				dir = self.convertDirection(pLoc.direction_to(dLoc))
				print(dir)
				tLoc1 = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y)
				tLoc2 = bc.MapLocation(bc.Planet.Earth, pLoc.x, pLoc.y + dir[1])
				tLoc3 = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y + dir[1])
				
				if EarthMap.is_passable_terrain_at(tLoc1) and EarthMap.is_passable_terrain_at(tLoc2) and EarthMap.is_passable_terrain_at(tLoc3):
					self.path.append(pLoc.direction_to(dLoc))
					pLoc = tLoc3
				else:
					if not EarthMap.is_passable_terrain_at(tLoc1):
						nDir = pLoc.direction_to(tLoc1) - 1
						wallDir = pLoc.direction_to(tLoc1)
					elif not EarthMap.is_passable_terrain_at(tLoc2):
						nDir = pLoc.direction_to(tLoc2) - 1
						wallDir = pLoc.direction_to(tLoc2)
					else:
						nDir = pLoc.direction_to(tLoc3) - 1
						wallDir = pLoc.direction_to(tLoc3)
					
					print("Walllllll: " + str(wallDir))
					#Finds the direction you can go along the obstacle
					while True:
						if pLoc.distance_squared_to(dLoc) == 0:
							n = 0
							for i in self.path:
								if type(i) == type(1):
									self.path[n] = self.convertToDirection(i)
								print(str(i) + " : " + str(self.id))
								n = n + 1
							return True
						#print(str(pLoc) + " <> " + str(dLoc) + " : " + str(self.id) + " Finding new direction")			
						#This flips the compass around because each direction is 0 through 7
						if nDir < 0:
							nDir = nDir + 8
						dir = self.convertDirection(nDir)
						tLoc = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y + dir[1])
						
						if EarthMap.is_passable_terrain_at(tLoc):
							self.path.append(nDir)
							pLoc = tLoc
							break
						else:
							nDir = nDir - 1
					
					#Move in that direction along the obstacle until it can head in the right direction again
					while True:
						if pLoc.distance_squared_to(dLoc) == 0:
							n = 0
							for i in self.path:
								if type(i) == type(1):
									self.path[n] = self.convertToDirection(i)
								print(str(i) + " : " + str(self.id))
								n = n + 1
							return True
						#print(str(pLoc) + " <> " + str(dLoc) + " : " + str(self.id) + " Along Wall " + str(nDir) + " ; " + str(wallDir))		
						dir = self.convertDirection(nDir)
						wallD = self.convertDirection(wallDir)
						
						tLoc = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y + dir[1])
						wallLoc = bc.MapLocation(bc.Planet.Earth, pLoc.x + wallD[0], pLoc.y + wallD[1])
						if EarthMap.is_passable_terrain_at(tLoc) and EarthMap.is_passable_terrain_at(wallLoc) == False:
							self.path.append(nDir)
							pLoc = tLoc
						elif EarthMap.is_passable_terrain_at(wallLoc) == True:
							#Continue heading along the same wall
							self.path.append(wallDir)
							pLoc = wallLoc
							nDir = wallDir
							
							dir = self.convertDirection(pLoc.direction_to(dLoc))
							tLoc = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y + dir[1])
							
							#But if you can now continue toward the goal then do so
							if EarthMap.is_passable_terrain_at(tLoc):
								self.path.append(pLoc.direction_to(dLoc))
								pLoc = tLoc
								break
								
		else:
			return False
			
	def convertDirection(self, dir):
		if dir == bc.Direction.North:
			return [0,1]
		elif dir == bc.Direction.Northeast:
			return [1,1]
		elif dir == bc.Direction.East:
			return [1,0]
		elif dir == bc.Direction.Southeast:
			return [1,-1]
		elif dir == bc.Direction.South:
			return [0,-1]
		elif dir == bc.Direction.Southwest:
			return [-1,-1]
		elif dir == bc.Direction.West:
			return [-1,0]
		elif dir == bc.Direction.Northwest:
			return [-1,1]
		else:
			return [0,0]
			
	def convertToDirection(self, n):
		if n == 0:
			return bc.Direction.North
		elif n == 1:
			return bc.Direction.Northeast
		elif n == 2:
			return bc.Direction.East
		elif n == 3:
			return bc.Direction.Southeast
		elif n == 4:
			return bc.Direction.South
		elif n == 5:
			return bc.Direction.Southwest
		elif n == 6:
			return bc.Direction.West
		elif n == 7:
			return bc.Direction.Northwest
		elif n == 8:
			return bc.Direction.Center
		
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
		
	def unloadUnit(self, *direction):
		if direction != ():
			directions = direction
		else:
			directions = list(bc.Direction)
		
		for d in directions:
			if gc.can_unload(self.unit.id, d):
				gc.unload(self.unit.id, d)
	
	def buildUnit(self, type):
		if gc.can_produce_robot(self.unit.id, type):
			gc.produce_robot(self.unit.id, type)
			
	
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
	#print("Round: " + str(round))

	try:
		totalUnits = len(gc.my_units())
		
		if round == 1:
			refreshUnits()
			totalUnits = len(gc.my_units())
			previousUnits = len(gc.my_units())
		elif gc.planet() == bc.Planet.Earth:
			
			for w in workers:
				if factories.size < maxFactory:
					w.blueprintFactory()
				else:
					w.mineKarbonite()
				#w.buildFactory()
				
			for f in factories:
				#To select what unit to build do bc.UnitType."Whatever"
				f.buildUnit(bc.UnitType.Worker)
				#If you don't put any direction it'll just unload in an empty square
				f.unloadUnit()
		
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
