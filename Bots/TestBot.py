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

'''
units = np.array([])
workers = np.array([])
knights = np.array([])
rangers = np.array([])
mages = np.array([])
healers = np.array([])
factories = np.array([])
rockets = np.array([])
'''

units = {}
workers = {}
knights = {}
rangers = {}
mages = {}
healers = {}
factories = {}
rockets = {}

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
	
	def __init__(self):
		self.hi = 0
		#uCount = uCount + 1
		
	def actionType(self, type):
		self.type = type
	
class Worker(Unit):

	count = 0
	
	def __init__(self):
		super().__init__()
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
	
	#Builds a factory in the specified direction, if not build in any direction
	def blueprintFactory(self, unit, *direction):
		global factories
		
		if unit.location.is_on_map():
			if direction != ():
				directions = direction
			else:
				directions = list(bc.Direction)
			
			for d in directions:
				if gc.can_blueprint(unit.id, bc.UnitType.Factory, d):
					gc.blueprint(unit.id, bc.UnitType.Factory, d)
					print("Blueprinted")
					return True
					break
			
			print("Failed to blueprint")
			return False
		else:
			return False
	
	#Builds whatever factory is nearby	
	def buildFactory(self, unit):
		if unit.location.is_on_map():
			near = gc.sense_nearby_units(unit.location.map_location(), 1)
			for i in near:
				if gc.can_build(unit.id, i.id):
					gc.build(unit.id, i.id)
					print("Building")
		else:
			return False
			
	def mineKarbonite(self, unit, path):
		global EarthMap
		global karnoniteLocations
		global gc

		if unit.location.is_on_map():
			if len(path) != 0:
				if len(path) != 1:
					if gc.can_move(unit.id, path[0]) and gc.is_move_ready(unit.id):	
						gc.move_robot(unit.id, path[0])
						del path[0]
						print("Deleted: " + str(len(path)) + " : " + str(unit.id))
						return path
					else:
						return path
						print("CM: " + str(unit.id) + " Direction: " + str(path[0]))
						
				else:
					if gc.can_harvest(unit.id, path[0]):
						gc.harvest(unit.id, path[0])
						print("Harvesting..." + str(unit.id))
						return path
					else:
						print("Can't harvest more..." + str(unit.id) + " | " + str(len(karnoniteLocations)))
						return []
			elif len(karnoniteLocations) != 0:
				pLoc = unit.location.map_location()
				closestDist = pLoc.distance_squared_to(karnoniteLocations[0])
				closestLoc = 0
				for i in range(1, len(karnoniteLocations)):
					dist = pLoc.distance_squared_to(karnoniteLocations[i])
					if dist < closestDist:
						closestDist = dist
						closestLoc = i
				print("NL:" + str(closestLoc) + " " + str(karnoniteLocations[closestLoc]) + " : " + str(unit.id))
				loc = karnoniteLocations[closestLoc]
				karnoniteLocations = np.delete(karnoniteLocations, [closestLoc])
				
				return self.navigateToPoint(unit, loc)
			else:
				return []
		else:
			print("Unit not on map")
			return []
		
	def navigateToPoint(self, unit, dLoc):
		global EarthMap
		path = []
		if unit.location.is_on_map():
			pLoc = unit.location.map_location()
			
			while True:
				if pLoc.distance_squared_to(dLoc) == 0:
					n = 0
					for i in path:
						if type(i) == type(1):
							path[n] = self.convertToDirection(i)
						n = n + 1
					print("Path returned: " + str(len(path)))
					return path
				dir = self.convertDirection(pLoc.direction_to(dLoc))
				tLoc1 = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y)
				tLoc2 = bc.MapLocation(bc.Planet.Earth, pLoc.x, pLoc.y + dir[1])
				tLoc3 = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y + dir[1])
				
				if EarthMap.is_passable_terrain_at(tLoc1) and EarthMap.is_passable_terrain_at(tLoc2) and EarthMap.is_passable_terrain_at(tLoc3) and not gc.has_unit_at_location(tLoc1) and not gc.has_unit_at_location(tLoc2) and not gc.has_unit_at_location(tLoc3):
					path.append(pLoc.direction_to(dLoc))
					pLoc = tLoc3
				else:
					if not EarthMap.is_passable_terrain_at(tLoc1) or not gc.has_unit_at_location(tLoc1):
						nDir = pLoc.direction_to(tLoc1) - 1
						wallDir = pLoc.direction_to(tLoc1)
					elif not EarthMap.is_passable_terrain_at(tLoc2) or not gc.has_unit_at_location(tLoc2):
						nDir = pLoc.direction_to(tLoc2) - 1
						wallDir = pLoc.direction_to(tLoc2)
					else:
						nDir = pLoc.direction_to(tLoc3) - 1
						wallDir = pLoc.direction_to(tLoc3)
					
					#Finds the direction you can go along the obstacle
					while True:
						if pLoc.distance_squared_to(dLoc) == 0:
							n = 0
							for i in path:
								if type(i) == type(1):
									path[n] = self.convertToDirection(i)
								n = n + 1
							return path
						
						#This flips the compass around because each direction is 0 through 7
						if nDir < 0:
							nDir = nDir + 8
						dir = self.convertDirection(nDir)
						tLoc = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y + dir[1])
						
						if EarthMap.is_passable_terrain_at(tLoc) or not gc.has_unit_at_location(tLoc):
							path.append(nDir)
							pLoc = tLoc
							break
						else:
							nDir = nDir - 1
					
					#Move in that direction along the obstacle until it can head in the right direction again
					while True:
						if pLoc.distance_squared_to(dLoc) == 0:
							n = 0
							for i in path:
								if type(i) == type(1):
									path[n] = self.convertToDirection(i)
								n = n + 1
							return path
						dir = self.convertDirection(nDir)
						wallD = self.convertDirection(wallDir)
						
						tLoc = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y + dir[1])
						wallLoc = bc.MapLocation(bc.Planet.Earth, pLoc.x + wallD[0], pLoc.y + wallD[1])
						if EarthMap.is_passable_terrain_at(tLoc) and EarthMap.is_passable_terrain_at(wallLoc) == False or not gc.has_unit_at_location(tLoc1) and gc.has_unit_at_location(wallLoc):
							path.append(nDir)
							pLoc = tLoc
						elif EarthMap.is_passable_terrain_at(wallLoc) == True or not gc.has_unit_at_location(wallLoc):
							#Continue heading along the same wall
							path.append(wallDir)
							pLoc = wallLoc
							nDir = wallDir
							
							dir = self.convertDirection(pLoc.direction_to(dLoc))
							tLoc = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y + dir[1])
							
							#But if you can now continue toward the goal then do so
							if EarthMap.is_passable_terrain_at(tLoc) or not gc.has_unit_at_location(tLoc1):
								path.append(pLoc.direction_to(dLoc))
								pLoc = tLoc
								break
								
		else:
			return []
			
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
	
	def __init__(self):
		super().__init__()
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
		
class Ranger(Unit):

	count = 0
	
	def __init__(self):
		super().__init__()
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)

class Mage(Unit):
	
	count = 0
	
	def __init__(self):
		super().__init__()
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
		
class Healer(Unit):
	
	count = 0
	
	def __init__(self):
		super().__init__()
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
		
class Factory(Unit):
	
	count = 0
	
	def __init__(self):
		super().__init__()
		#count = count + 1
		
	def actionType(self, type):
		super().actionType(type)
		
	def unloadUnit(self, unit, *direction):
		if direction != ():
			directions = direction
		else:
			directions = list(bc.Direction)
		
		for d in directions:
			if gc.can_unload(unit.id, d):
				gc.unload(unit.id, d)
	
	def buildUnit(self, unit, type):
		if gc.can_produce_robot(unit.id, type):
			gc.produce_robot(unit.id, type)
			
	
class Rocket(Unit):
	
	count = 0
	
	def __init__(self):
		super().__init__()
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
	global gc
	
	w = Worker()
	f = Factory()
	
	for unit in gc.my_units():
		type = unit.unit_type
		#print(str(unit.id) + " | " + str(type))
		#Separates the units into separate arrays
		if type == bc.UnitType.Worker:
			if unit.id in workers:
				#Do some logic
				
				if len(factories) < maxFactory:
					print("Not enough factories")
					w.blueprintFactory(unit)
				else:
					workers[unit.id]["Path"] = w.mineKarbonite(unit, workers[unit.id]["Path"])
					
			else:
				workers[unit.id] = {"Path":[]}
		elif type == bc.UnitType.Knight:
			if unit.id in knights:
				#Do some logic
				knights[1] = 4
			else:
				knights[unit.id] = {}
		elif type == bc.UnitType.Ranger:
			if unit.id in rangers:
				#Do some logic
				rangers[1] = 4
			else:
				rangers[unit.id] = {}
		elif type == bc.UnitType.Mage:
			if unit.id in mages:
				#Do some logic
				mages[1] = 4
			else:
				mages[unit.id] = {}
		elif type == bc.UnitType.Healer:
			if unit.id in healers:
				#Do some logic
				healers[1] = 4
			else:
				healers[unit.id] = {}
		elif type == bc.UnitType.Factory:
			if unit.id in factories:
				#Do some logic
				factories[1] = 4
			else:
				factories[unit.id] = {}
		elif type == bc.UnitType.Rocket:
			if unit.id in rockets:
				#Do some logic
				rockets[1] = 4
			else:
				rockets[unit.id] = {}
	

while True:
	round = gc.round()
	#print("Round: " + str(round))

	try:
		totalUnits = len(gc.my_units())
		
		if round == 1:
			refreshUnits()
			totalUnits = len(gc.my_units())
		elif gc.planet() == bc.Planet.Earth:
			refreshUnits()
		
	except Exception as e:
		if error == False:
			print("Error:",e)
	
			#This shows where the error was
			traceback.print_exc()
			error = True
		
	gc.next_turn()
	
	sys.stdout.flush()
	sys.stderr.flush()
