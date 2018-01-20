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
maxFactory = 0

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
			
	def mineKarbonite(self, unit, path, dest):
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
						return [path, dest]
					elif path[0] == bc.Direction.Center:
						del path[0]
						return [path, dest]
					else:
						print("CM: " + str(unit.id) + " Direction: " + str(path))
						#return [self.navigateToPoint(unit, dest), dest]
						return [path, dest]
						
				else:
					if gc.can_harvest(unit.id, path[0]):
						gc.harvest(unit.id, path[0])
						print("Harvesting..." + str(unit.id))
						return [path, dest]
					else:
						print("Can't harvest more..." + str(unit.id) + " | " + str(len(karnoniteLocations)))
						return [[], dest]
			elif len(karnoniteLocations) != 0:
				pLoc = unit.location.map_location()
				closestDist = pLoc.distance_squared_to(karnoniteLocations[0])
				closestLoc = 0
				for i in range(1, len(karnoniteLocations)):
					dist = pLoc.distance_squared_to(karnoniteLocations[i])
					if dist < closestDist and not gc.has_unit_at_location(karnoniteLocations[i]):
						closestDist = dist
						closestLoc = i
				#print("NL:" + str(closestLoc) + " " + str(karnoniteLocations[closestLoc]) + " : " + str(unit.id))
				loc = karnoniteLocations[closestLoc]
				karnoniteLocations = np.delete(karnoniteLocations, [closestLoc])
				
				return [self.navigateToPoint(unit, loc), loc]
			else:
				return [[], dest]
		else:
			print("Unit not on map")
			return [[], dest]
	
	def navigateToPoint(self, unit, dLoc):
		global EarthMap
		branches = []
		locs = []
		if unit.location.is_on_map():
			pLoc = unit.location.map_location()
			locs.append(pLoc)
			while True:
				lNum = len(locs)-1
				if self.atLocation(locs[lNum],dLoc):
					return self.convertLocs(locs)
				
				dir = self.convertDirection(locs[lNum].direction_to(dLoc))
				testLoc = bc.MapLocation(bc.Planet.Earth, locs[lNum].x + dir[0], locs[lNum].y + dir[1])
				
				if self.move(locs[lNum], dir) != bc.MapLocation(bc.Planet.Earth, -1, -1):
					locs.append(testLoc)
					#print(testLoc)
				else:
					#Gives all of the key points necessary to get to the destination
					kP = self.followWall(locs[lNum], dLoc, unit)
					allLocations = [[unit.location.map_location()]]
					for points in kP:
						allLocations = self.canMoveToDestination(allLocations[0], None, dLoc, unit, None, None)
					#The 1st part of the array are the locations
					return self.convertLocs(allLocations[0])
	
	def convertLocs(self, locs):
		path = []
		for i in range(len(locs)-1):
			path.append(locs[i].direction_to(locs[i+1]))
		return path
			
	def followWall(self, loc, dLoc, unit):
		branches = []
		nBranches = []
		temp = []
		walls = self.checkWalls(loc)
		if len(walls) == 0:
			print("No walls. How")
		elif len(walls) == 1:
			b = Branch(walls[0], loc)
			nBranches = nBranches + b.extend()
		elif len(walls) == 2:
			print("Welp")
			#That should be the corner piece between the two walls
			b = Branch(int((walls[0] + walls[1])/(2), loc))
			nBranches = nBranches + b.extend()
		else:
			print("I dunno")
		
		while True:
			temp = []
			for i in range(0, len(nBranches), 2):
				#Every other value is the direction in which to extend the branch
				dest = self.canMoveToDestination([], nBranches[i].getStartingLocation(), dLoc, unit, nBranches[i], nBranches[i + 1])
				print("Destination: " + str(dLoc))
				if dest[1] == False:
					temp = temp + dest[2]
				else:
					keyLocations = [dLoc] + nBranches[i].getPath([])
					print("KeyLocations: " + str(keyLocations))
					return keyLocations
					
			nBranches = temp
			branches.append(temp)
				
	def canMoveToDestination(self, tLocs, sLoc, dLoc, unit, branch, branchDirection):
		global EarthMap
		locs = list(tLocs)
		if unit.location.is_on_map():
			if len(locs) == 0:
				pLoc = sLoc
				locs.append(sLoc)
			else:
				pLoc = unit.location.map_location()
				locs.append(pLoc)
			while True:
				lNum = len(locs)-1
				if self.atLocation(locs[lNum],dLoc):
					return [locs, True]
				
				dir = self.convertDirection(locs[lNum].direction_to(dLoc))
				testLoc = bc.MapLocation(bc.Planet.Earth, locs[lNum].x + dir[0], locs[lNum].y + dir[1])
				
				if self.move(locs[lNum], dir) != bc.MapLocation(bc.Planet.Earth, -1, -1):
					locs.append(testLoc)
				else:
					test2 = bc.MapLocation(bc.Planet.Earth, locs[lNum].x + dir[0], locs[lNum].y)
					test3 = bc.MapLocation(bc.Planet.Earth, locs[lNum].x, locs[lNum].y + dir[1])
						
					if EarthMap.is_passable_terrain_at(test2) and EarthMap.is_passable_terrain_at(testLoc) and not gc.has_unit_at_location(test2) and not gc.has_unit_at_location(testLoc):
						locs.append(test2)
						locs.append(testLoc)
					elif EarthMap.is_passable_terrain_at(test3) and EarthMap.is_passable_terrain_at(testLoc) and not gc.has_unit_at_location(test3) and not gc.has_unit_at_location(testLoc):
						locs.append(test3)
						locs.append(testLoc)
					else:
						if locs[lNum] == pLoc:
							return [locs, False, branch.extend(branchDirection)]
						else:
							newBranches = []
							walls = self.checkWalls(locs[lNum])
							if len(walls) == 0:
								print("No walls. How")
							elif len(walls) == 1:
								b = Branch(walls[0], locs[lNum])
								newBranches = newBranches + b.extend()
							elif len(walls) == 2:
								print("Welp")
								#That should be the corner piece between the two walls
								wall = int((walls[0] + walls[1])/(2))
								b = Branch(wall, locs[lNum])
								newBranches = newBranches + b.extend()
							else:
								print("I dunno")
							return [locs, False, newBranches]
							
	def move(self, loc, dir):
		test1 = bc.MapLocation(bc.Planet.Earth, loc.x + dir[0], loc.y + dir[1])
		test2 = bc.MapLocation(bc.Planet.Earth, loc.x + dir[0], loc.y)
		test3 = bc.MapLocation(bc.Planet.Earth, loc.x, loc.y + dir[1])
		
		if EarthMap.is_passable_terrain_at(test1) and EarthMap.is_passable_terrain_at(test2) and EarthMap.is_passable_terrain_at(test3) and not self.checkUnit(dir, loc):
			return test1
		else:
			return bc.MapLocation(bc.Planet.Earth, -1, -1)
	
	def atLocation(self, pLoc, dLoc):
		if pLoc.distance_squared_to(dLoc) == 0:
			return True
		else:
			return False
	
	def checkUnit(self, dir, pLoc):
		if dir[0] != 0:
			loc = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y)
			if gc.has_unit_at_location(loc):
				return True
		if dir[1] != 0:
			loc = bc.MapLocation(bc.Planet.Earth, pLoc.x, pLoc.y + dir[1])
			if gc.has_unit_at_location(loc):
				return True	
		if dir[0] != 0 and dir[1] != 0:
			loc = bc.MapLocation(bc.Planet.Earth, pLoc.x + dir[0], pLoc.y + dir[1])
			if gc.has_unit_at_location(loc):
				return True	
		return False
		
	def checkWalls(self, pLoc):
		global EarthMap
		global gc
		
		walls = []
		
		directions = list(bc.Direction)
		
		#Then check the diagonal directions
		for i in range(0, len(directions)-1, 2):
			direction = self.convertDirection(directions[i])
			loc = bc.MapLocation(bc.Planet.Earth, pLoc.x + direction[0], pLoc.y + direction[1])
			if gc.has_unit_at_location(loc) or not EarthMap.is_passable_terrain_at(loc):
				walls.append(directions[i])
		
		return walls
		
		
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
	
	def cToD(self, dir):
		if dir == [0,1]:
			return bc.Direction.North
		elif dir == [1,1]:
			return bc.Direction.Northeast
		elif dir == [1,0]:
			return bc.Direction.East
		elif dir == [1,-1]:
			return bc.Direction.Southeast
		elif dir == [0,-1]:
			return bc.Direction.South
		elif dir == [-1,-1]:
			return bc.Direction.Southwest
		elif dir == [-1,0]:
			return bc.Direction.West
		elif dir == [-1,1]:
			return bc.Direction.Northwest
		else:
			return [0,0]
			

class Branch():

	def __init__(self, wallDirection, startingLoc):
		self.wallDirection = wallDirection
		self.startingLoc = startingLoc
		self.direction = self.tDirection(wallDirection)
		self.nodes = []
		self.branches = []
		
		if self.startingLoc != bc.MapLocation(bc.Planet.Earth, -1, -1):
			self.pBranch = Branch(-1, bc.MapLocation(bc.Planet.Earth, -1, -1))
	
	def tDirection(self, dir):
		
		if self.startingLoc == bc.MapLocation(bc.Planet.Earth, -1, -1):
			return None
		
		directions = []
		if self.wallDirection % 2 == 0:
			dir = dir - 2
			if dir < 0:
				dir = dir + 8
			directions.append(dir)
			
			dir = directions[0] - 4
			if dir < 0:
				dir = dir + 8
			directions.append(dir)
			
			return directions
		else:
			#This means it's a corner piece. Only give when colliding with two walls or just a corner wall
			dir = self.convertDirection(self.wallDirection - 1)
			testLocation = bc.MapLocation(bc.Planet.Earth, self.startingLoc.x + dir[0], self.startingLoc.y + dir[1])
			
			#Passible terrain at this spot means it's only a corner piece
			if EarthMap.is_passable_terrain_at(testLocation) and not gc.has_unit_at_location(testLocation):
				dir = self.wallDirection - 1
				if dir < 0:
					dir = dir + 8
				directions.append(dir)
				
				dir = directions[0] + 1
				if dir > 7:
					dir = dir - 8
				directions.append(dir)
			else:
				#This means it must be in a corner with two walls to it
				dir = self.wallDirection - 3
				if dir < 0:
					dir = dir + 8
				directions.append(dir)
				
				dir = directions[0] + 3
				if dir > 7:
					dir = dir - 8
				directions.append(dir)
			
			return directions

	#Will later need to make this function try to reach the destination after every node is found
	def extend(self, *extendDirection):
		
		print("Extending...")
		global gc
		global EarthMap
		
		if len(extendDirection) != 0 and extendDirection[0] != -1:
			self.direction = extendDirection
		
		hitWall1 = False
		hitWall2 = False
		
		#Can always ignore the first wall location
		first = True
		
		loc1 = self.startingLoc
		while True:

			dir = self.convertDirection(self.direction[0])
			print("First: " + str(loc1) + " | " + str(self.wallDirection))
			wallDir = self.convertDirection(self.wallDirection)
			
			wallLocation = bc.MapLocation(bc.Planet.Earth, loc1.x + wallDir[0], loc1.y + wallDir[1])
			newPlayerLocation = bc.MapLocation(bc.Planet.Earth, loc1.x + dir[0], loc1.y + dir[1])
			
			#Checks if the wall is no longer there or if the player has run into a wall
			if EarthMap.is_passable_terrain_at(wallLocation) and not gc.has_unit_at_location(wallLocation) and first == False:
				self.nodes.append(loc1)
				break
			elif not EarthMap.is_passable_terrain_at(newPlayerLocation) or gc.has_unit_at_location(newPlayerLocation):
				self.nodes.append(loc1)
				hitWall1 = True
				break
			else:
				loc1 = newPlayerLocation
			
			if first == True:
				first = False
		
		#Can always ignore the first wall location
		first = True
		
		#This loop goes in the opposite direction
		loc2 = self.startingLoc
		if len(self.direction) >= 2:
			while True:
				#Flips the direction of travel
				dir = self.convertDirection(self.direction[1])
				print("Second: " + str(loc2))
				wallDir = self.convertDirection(self.wallDirection)
				
				wallLocation = bc.MapLocation(bc.Planet.Earth, loc2.x + wallDir[0], loc2.y + wallDir[1])
				newPlayerLocation = bc.MapLocation(bc.Planet.Earth, loc2.x + dir[0], loc2.y + dir[1])
				
				#Checks if the wall is no longer there or if the player has run into a wall
				if EarthMap.is_passable_terrain_at(wallLocation) and not gc.has_unit_at_location(wallLocation):
					self.nodes.append(loc2)
					break
				elif not EarthMap.is_passable_terrain_at(newPlayerLocation) or gc.has_unit_at_location(newPlayerLocation):
					self.nodes.append(loc2)
					hitWall2 = True
					break
				else:
					loc2 = newPlayerLocation
				
			print("Nodes: " + str(self.nodes[0]) + " | " + str(self.nodes[1]))
			
			#The function is recurrent and will continue to extend branches
			if hitWall1 == False:
				#The wall direction is now the opposite of the direction it was going because it rounded the corner
				dir = self.direction[0] - 4
				if dir < 0:
					dir = dir + 8
				b = Branch(dir, loc1)
				b.setPreviousBranch(self)
				self.branches.append(b)
				self.branches.append(self.wallDirection)
				#b.extend(self.wallDirection)
			else:
				#The wall direction is the direction unit was trying to go because it hit a wall
				b = Branch(self.direction[0], loc1)
				b.setPreviousBranch(self)
				self.branches.append(b)
				self.branches.append(-1)
				#b.extend()
			if hitWall2 == False:
				#The wall direction is now the opposite of the direction it was going because it rounded the corner
				dir = self.direction[1] - 4
				if dir < 0:
					dir = dir + 8
				b = Branch(dir, loc2)
				b.setPreviousBranch(self)
				self.branches.append(b)
				self.branches.append(self.wallDirection)
				#b.extend(self.wallDirection)
			else:
				#The wall direction is the direction unit was trying to go because it hit a wall
				b = Branch(self.direction[1], loc2)
				b.setPreviousBranch(self)
				self.branches.append(b)
				self.branches.append(-1)
				#b.extend()
			
			print("Branches: " + str(len(self.branches)))			
			return self.branches
			
		else:
			print("Node: " + str(self.nodes[0]))
			
			branches = []
			
			#The function is recurrent and will continue to extend branches
			if hitWall1 == False:
				#The wall direction is now the opposite of the direction it was going because it rounded the corner
				dir = self.direction[0] - 4
				if dir < 0:
					dir = dir + 8
				b = Branch(dir, loc1)
				b.setPreviousBranch(self)
				self.branches.append(b)
				self.branches.append(self.wallDirection)
				#b.extend(self.wallDirection)
			else:
				#The wall direction is the direction unit was trying to go because it hit a wall
				b = Branch(self.direction[0], loc1)
				b.setPreviousBranch(self)
				self.branches.append(b)
				self.branches.append(-1)
				#b.extend()
				
			return self.branches
	
	def getNode(self, x):
		if x >= 1:
			if len(nodes) > 1:
				return nodes[x]
			else:
				print("Only one node")
		else:
			return nodes[x]
	
	def getNodeCount(self):
		return len(nodes)
	
	def getStartingLocation(self):
		return self.startingLoc
		
	def addNode(nodeLocation):
		nodes.append(nodeLocation)
		
	def setPreviousBranch(self, b):
		self.pBranch = b
	
	def getPath(self, locations):
		if self.pBranch.getStartingLocation() !=  bc.MapLocation(bc.Planet.Earth, -1, -1):
			return self.pBranch.getPath(locations) + [self.getStartingLocation()] + locations
		else:
			return [self.getStartingLocation()] + locations
	
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
					list = w.mineKarbonite(unit, workers[unit.id]["Path"], workers[unit.id]["Dest"])
					workers[unit.id]["Path"] = list[0]
					workers[unit.id]["Dest"] = list[1]
			else:
				workers[unit.id] = {"Path":[], "Dest":0}
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
	print("Round: " + str(round))

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
