# ======================================================================
# FILE:        Main.py
#
# AUTHOR:      Abdullah Younis
#
# DESCRIPTION: This file is the entry point for the program. The main
#              function serves a couple purposes: (1) It is the
#              interface with the command line. (2) It reads the files,
#              creates the World object, and passes that all the
#              information necessary. (3) It is in charge of outputing
#              information.
#
# NOTES:       - Syntax:# ======================================================================
# FILE:        MyAI.py
#
# AUTHOR:      Abdullah Younis
#
# DESCRIPTION: This file contains your agent class, which you will
#              implement. You are responsible for implementing the
#              'getAction' function and any helper methods you feel you
#              need.
#
# NOTES:       - If you are having trouble understanding how the shell
#                works, look at the other parts of the code, as well as
#                the documentation.
#
#              - You are only allowed to make changes to this portion of
#                the code. Any changes to other portions of the code will
#                be lost when the tournament runs your code.
# ======================================================================
from Agent import Agent


class MyAI(Agent):
    def __init__(self):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================

        self.wumpusShot = False
        self.shot_arrow = False
        self.orientation = 'R'
        self.has_moved = False
        self.got_gold = False
        self.back_tracking = False
        self.go_home = [Agent.Action.CLIMB]
        self.World = Knowledge_Base()
        self.numMoves = 0
        self.just_shot = False
        self.has_moved = True
        self.just_found_gold = False

        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

    def getAction(self, stench, breeze, glitter, bump, scream):
        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================

        #If Agent has found the gold, creates matrix of optimal paths and chooses shortest path home
        if (self.got_gold):
            if self.just_found_gold:
                self.World.findPaths() #matrix of optimal paths
                self.just_found_gold = False
            
            if self.World._x == 0 and self.World._y ==0 :
                return Agent.Action.CLIMB

            m = self.World.spots_available(self.World._x, self.World._y)
            temp_dict = dict()

            for x,y in m:
                temp_dict[(x,y)] = self.World._paths[(x,y)]

            tdict = sorted(temp_dict.keys(), key = lambda x: temp_dict[x][0], reverse = True)

            return self.get_move((tdict[0][0], tdict[0][1]))

        #When Agent can no longer go forward, it will go backwards until it finds a tile where
        #   it can move in a different direction
        if (self.back_tracking):
            if (self.World._x == 0 and self.World._y == 0):
                return Agent.Action.CLIMB
            x = self.go_home.pop()
            if (x==Agent.Action.FORWARD):
                self.World.update_position()
            elif (x==Agent.Action.TURN_LEFT):
                self.World.update_orientation('L')
            elif (x==Agent.Action.TURN_RIGHT):
                self.World.update_orientation('R')
            return x
        self.numMoves += 1

        #ensures that Agent will give up after too many moves have been made for it score well
        if (self.numMoves > 150):
                self.got_gold = True
                self.just_found_gold = True
                
                self._threshold = .75
                self.World.update_orientation('L')
                self.go_home.append(Agent.Action.TURN_LEFT)
                return Agent.Action.TURN_LEFT
        
        #will only add a move if it is a tile the Agent has never been
        if ((self.World._x, self.World._y) not in self.World._visited) and bump==False:
            self.World.add_move()

        #will only update number of times visited if it is not bumping against a wall
        elif (self.has_moved==True and bump==False):
            self.World._visited[(self.World._x, self.World._y)]+=1

        if glitter: 
            self.got_gold = True
            self.just_found_gold = True
            if not (self.World._x == 0 and self.World._y == 0):
                self.go_home.append(Agent.Action.TURN_LEFT)
                self.go_home.append(Agent.Action.TURN_LEFT)
            return Agent.Action.GRAB

        if (self.World._x == 0 and self.World._y == 0 and breeze):
            return Agent.Action.CLIMB

        if bump:
            self.go_home.pop()
            self.World.handleBump()

        if self.just_shot:
            if scream:
                self.wumpusShot = True
                self.World.shotArrow(True)
                self.World.update_world("Scream")
            else:
                self.World.shotArrow(False)
            self.just_shot = False

        if (self.has_moved):
            self.has_moved = False
            
            #updates None in World dictionary 
            if breeze == False and stench == False:
                self.World.update_world(None)
                
            #updates location of a breeze in World dictionary
            if breeze:
                self.World.update_world('B')
                
            #updates location of stench in World dictionary and shoots arrow
            if stench and not self.shot_arrow:
                self.World.update_world('S')
                self.World.updateWumpusLocation()
                self.shot_arrow, self.just_shot = True, True
                return Agent.Action.SHOOT

        #gets move, which is a direction: i.r. 'R'   
        move = self.World.next_move()

        #from move, determines whether to go forward or turn
        if move == self.World._orientation:
            self.back_tracking = False
            self.World.update_position()
            self.has_moved = True
            self.go_home.append(Agent.Action.FORWARD)
            return Agent.Action.FORWARD
        if (move == "Turnaround"):
            self.back_tracking = True
            self.go_home.append(Agent.Action.TURN_LEFT)
            self.World.update_orientation('L')
            return Agent.Action.TURN_LEFT
        else:
            self.back_tracking = False
            if self.find_move(move) == 1:
                self.World.update_orientation('R')
                self.go_home.append(Agent.Action.TURN_LEFT)
                return Agent.Action.TURN_RIGHT
            else:
                self.World.update_orientation('L')
                self.go_home.append(Agent.Action.TURN_RIGHT)
                return Agent.Action.TURN_LEFT

    
    def get_move(self, move_info):
        #print(move_info)
        if self.World._orientation == self.World._paths[move_info][1]:
            self.World.update_orientation('L')
            return Agent.Action.TURN_LEFT
        else:
            if abs(self.dir_diff(move_info)) == 0:
                self.World.update_position()
                return Agent.Action.FORWARD
            elif self.dir_diff(move_info) == -1:
                self.World.update_orientation('R')
                return Agent.Action.TURN_RIGHT
            else:
                self.World.update_orientation('L')
                return Agent.Action.TURN_LEFT


    def dir_diff(self, k):
        d1 = self.World._possible_orientations.index(self.World.coord_to_orientation((self.World._x, self.World._y),k))
        d2 = self.World._possible_orientations.index(self.World._orientation)
        value = d1 - d2
        return value

    def find_move(self, dir):
        d1 = self.World._possible_orientations.index(dir)
        d2 = self.World._possible_orientations.index(self.World._orientation)
        return d2-d1
        


        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

        # ======================================================================
        # YOUR CODE BEGINS
        # ======================================================================

#class holding all objects and functions pertaining to the Wumpus World
class Knowledge_Base(object):
    def __init__(self):
        self._possible_orientations = ['R', 'U', 'L', 'D']
        self._orientation = 'R'
        self._x = 0
        self._y = 0
        self._world = dict()
        self._visited = dict()
        self._paths = dict()

        self._possibleWumpus = set ()
        self.WumpusLocation = None

        self._xmax = 1000
        self._ymax = 1000

        self._count = 0
        self._wumpus_shot = False

        self._threshold = .5

        self._n = 0

        self._past_list = []
        self._no_moves_from_spot = []
    
    #creates a matrix of moves from location of gold to origin 
    def findPaths(self):
        stack = list()

        now = (0,0)
        self._paths[now] = (-1, 'R')
        move_list = self.checkMove(now[0], now[1])
        stack.extend(move_list)
        past = now
        if len(move_list) > 1:
            self._past_list.append(past)
        if len(move_list)==0:
            return

        while (len(stack) != 0):
            now = stack.pop()
            past = self.check_matrix_values(now)
            value = self.turnheuristic(past,now)

            if (now in self._paths) and self._paths[now][0] < value:
                a=4
            else:
                self._paths[now] = (value, self.coord_to_orientation(past, now))

            move_l = self.checkMove(now[0], now[1])
            stack.extend(move_l)

    #helper function to determine if coordinates have been visited
    def check_matrix_values(self, tile):
        x=tile[0]
        y=tile[1]
        places = []
        if (x+1,y) in self._paths:
            places.append((x+1,y))
        if (x-1,y) in self._paths:
            places.append((x-1,y))
        if (x,y+1) in self._paths:
            places.append((x,y+1))
        if (x,y-1) in self._paths:
            places.append((x,y-1))

        return sorted(places, key=lambda x: self._paths[x][0], reverse=True)[0]


    #helper funciton to find_paths which determines which way to turn
    def turnheuristic(self, past, now):
        d1 = self._possible_orientations.index(self.coord_to_orientation(past,now))
        d2 = self._possible_orientations.index(self._paths[past][1])
        value = 1 + abs(d1-d2)
        if value == 3:
            value = 1

        heuristic = -value + self._paths[past][0]
        return heuristic
    
    #gives orientation to turn to based on coordinates from current location
    def coord_to_orientation(self, past, now):
        if (now[0]-past[0]) == 1:
            return 'R'
        if (now[0] -past[0]) == -1:
            return 'L'
        if (now[1] - past[1]) == 1:
            return 'U'
        if (now[1] - past[1]) == -1:
            return 'D'

    #helper function to find_paths which appends places on the grid that are valid and have been visited
    def spots_available(self, x, y):
        r = []
        #UP
        if ((self.validLocation(x,y+1) and ((x,y+1) in self._visited))):
            r.append((x,y+1))
        #RIGHT
        if ((self.validLocation(x+1,y) and ((x+1,y) in self._visited))):
            r.append((x+1,y))
        #DOWN
        if ((self.validLocation(x,y-1) and ((x,y-1) in self._visited))):
            r.append((x, y-1))
        #LEFT
        if ((self.validLocation(x-1,y) and ((x-1,y) in self._visited))):
            r.append((x-1,y))
        return r

    def checkMove(self, x, y):
        r = []
        #UP
        if ((self.validLocation(x,y+1) and ((x,y+1) in self._visited) and ((x,y+1) not in self._paths))):
            r.append((x,y+1))
        #RIGHT
        if ((self.validLocation(x+1,y) and ((x+1,y) in self._visited)) and ((x+1,y) not in self._paths)):
            r.append((x+1,y))
        #DOWN
        if ((self.validLocation(x,y-1) and ((x,y-1) in self._visited)) and ((x,y-1) not in self._paths)):
            r.append((x, y-1))
        #LEFT
        if ((self.validLocation(x-1,y) and ((x-1,y) in self._visited)) and ((x-1,y) not in self._paths)):
            r.append((x-1,y))
        return r


    def shotArrow(self, inFront=False):
        dirx, diry = 0, 0
        if (self._orientation == "R"):
            dirx = 1
        if (self._orientation == "L"):
            dirx = -1
        if (self._orientation == "U"):
            diry = 1
        if (self._orientation == "D"):
            diry = -1

        locx, locy = self._x + dirx, self._y + diry

        if (inFront):
            self._possibleWumpus = set([(locx, locy)])
            self._wumpus_shot = True  
            self.WumpusLocation = [(locx, locy)]

        else:
            t = set([(locx, locy)])
            self._possibleWumpus = self._possibleWumpus.difference(t)

            if (len(self._possibleWumpus) == 1):
                self.WumpusLocation = list(self._possibleWumpus)

        return

    def updateWumpusLocation(self):
        x = self._x
        y = self._y

        if (len(self._possibleWumpus) == 0):
            if (self.validLocation(x - 1, y)) and ((x - 1, y) not in self._visited):
                self._possibleWumpus.add((x - 1, y))
            if (self.validLocation(x, y + 1)) and ((x, y + 1) not in self._visited):
                self._possibleWumpus.add((x, y + 1))
            if (self.validLocation(x + 1, y)) and ((x + 1, y) not in self._visited):
                self._possibleWumpus.add((x + 1, y))
            if (self.validLocation(x, y - 1)) and ((x, y - 1) not in self._visited):
                self._possibleWumpus.add((x, y - 1))
        else:
            t = set([(x - 1, y), (x, y + 1), (x + 1, y), (x, y - 1)])
            self._possibleWumpus = self._possibleWumpus.intersection(t)

        if (len(self._possibleWumpus) == 1):
            self.WumpusLocation = list(self._possibleWumpus)
        return

    def update_position(self):
        if self._orientation == 'U':
            self._y += 1
        if self._orientation == 'D':
            self._y -= 1
        if self._orientation == 'R':
            self._x += 1
        if self._orientation == 'L':
            self._x -= 1

    #ensures that bumps do not throw off our tracker for current location
    def handleBump(self):
        if self._orientation == 'U':
            self._y -= 1
            self._ymax = self._y
        if self._orientation == 'R':
            self._x -= 1
            self._xmax = self._x
        if self._orientation == 'D':
            self._y -= 1
        if self._orientation == 'L':
            self._x -= 1

    def add_move(self):
        self._world[(self._x, self._y)] = {'B': 0, 'S': 0, 'P': 0, 'W': 0}
        self._visited[(self._x, self._y)] = self._visited.get((self._x, self._y), 0) + 1

    def update_orientation(self, direction):
        i = self._possible_orientations.index(self._orientation)
        if direction == 'L':
            if i == 3:
                self._orientation = self._possible_orientations[0]
            else:
                self._orientation = self._possible_orientations[i + 1]
        elif direction == 'R':
            if i == 0:
                self._orientation = self._possible_orientations[3]
            else:
                self._orientation = self._possible_orientations[i - 1]
    
    #updates probability for result at that location
    def update_world(self, result):
        if result == 'Scream':
            self._wumpus_shot = True
            self.remove_stench()
            return
        if self._wumpus_shot and result == 'S':
            self._world[(self._x, self._y)]['W'] = 0
            self._world[(self._x, self._y)]['S'] = 0
            return
        if result == None:
            self._world[(self._x, self._y)] = {'B': 0, 'S': 0, 'P': 0, 'W': 0}
        else:
            self._world[(self._x, self._y)][result] = 1.0
            self._world[(self._x, self._y)]['P'] = 0
            self._world[(self._x, self._y)]['W'] = 0

        self._count = 0
        self.surrounding_cells_visited(self._x, self._y)

        self.check_direction(result, self._x + 1, self._y)
        self.check_direction(result, self._x, self._y + 1)
        self.check_direction(result, self._x - 1, self._y)
        self.check_direction(result, self._x, self._y - 1)

        return
    
    def surrounding_cells_visited(self, x, y):
        if ((x + 1, y) not in self._visited) and x + 1 >= 0 and y >= 0 and x + 1 <= self._xmax and y <= self._ymax:
            self._count += 1
        if ((x - 1, y) not in self._visited) and x - 1 >= 0 and y >= 0 and x - 1 <= self._xmax and y <= self._ymax:
            self._count += 1
        if ((x, y + 1) not in self._visited) and x >= 0 and y + 1 >= 0 and x <= self._xmax and y + 1 <= self._ymax:
            self._count += 1
        if ((x, y - 1) not in self._visited) and x >= 0 and y - 1 >= 0 and x <= self._xmax and y - 1 <= self._ymax:
            self._count += 1
        return 

    def check_direction(self, result, x, y):
        if x < 0 or y < 0 or x > self._xmax or y > self._ymax:
            return
        if (x, y) in self._visited.keys():
            return
        if (x, y) in self._world:
            self.set_prob(x, y, result)
        else:
            self._world[(x, y)] = {'B': 0, 'S': 0, 'P': 0, 'W': 0}
            self.set_prob(x, y, result)
        return
    
    #if the wumpus as been shot, we no longer care about stenches detected
    def remove_stench(self):
        for key, value in self._world.items():
            for k, v in value.items():
                if k == 'S':
                    self._world[key][k] = 0
                if k == 'W':
                    self._world[key][k] = 0

    #sets the probability based on tiles around it for that result
    def set_prob(self, x, y, result):
        if self._count == 0:
            return
        prob = 1 / self._count
        if result == 'B':
            self._world[(x, y)]['P'] += prob
        if result == 'S':
            self._world[(x, y)]['W'] += prob
        if result == None:
            self._world[(x, y)]['P'] = 0
            self._world[(x, y)]['W'] = 0

    def next_move(self):  
        smove = self.possible_moves()

        if (len(smove)==0):
            self._threshold += .25
            smove = self.possible_moves()

        if (len(smove)==0):
            return "Turnaround"

        if (len(smove) == 1) and (self.dir_to_coord(smove[0]) in self._visited):
            self._no_moves_from_spot.append((self._x, self._y))

        c = 0

        for k in smove.keys():
            if smove[k] == self._n: 
                c += 1
            if self._orientation == k:
                c += 1


        if c == len(smove) + 1:
            return self._orientation

        if (len(smove) > 0):
            x = min(smove.items(), key=lambda m: m[1])
            if smove.get(self._orientation, -1) == x[1]:
                return self._orientation
            else:
                return sorted(smove, key=smove.get)[0]
        else:
            return "Turnaround"


    def dir_to_coord(self, dir):
        if dir == 'L':
            return (self._x -1, self._y)
        if dir == 'R':
            return (self._x +1, self._y)
        if dir == 'U':
            return (self._x, self._y+1)
        if dir == 'D':
            return (self._x , self._y-1)


    def possible_moves(self):
        x, y = self._x, self._y

        potentials = dict()

        sum = (self._visited.get((x, y - 1), 0) + self._visited.get((x + 1, y), 0) + self._visited.get((x, y + 1),0) + self._visited.get(
            (x - 1, y), 0)) * 4.0


        if (sum == 0):
            sum = 4.0

        self.possible_moves_helper(x, y-1, sum, potentials, 'D')
        self.possible_moves_helper(x, y+1, sum, potentials, 'U')
        self.possible_moves_helper(x+1, y, sum, potentials, 'R')
        self.possible_moves_helper(x-1, y, sum, potentials, 'L')


        '''
        if self.validMove(x, y - 1) and self._world.get((x, y - 1), {'P': 0})['P'] < self._threshold and \
                        self._world.get((x, y - 1), {'W': 0})['W'] < self._threshold and self._visited.get((x, y - 1),
                                                                                                           0) < 4:
            potentials['D'] = self._world.get((x, y - 1), {'P': 0})['P'] + self._world.get((x, y - 1), {'W': 0})[
                'W'] + (self._visited.get((x, y - 1), 0) / sum)
            self._n = potentials['D']
        if self.validMove(x + 1, y) and self._world.get((x + 1, y), {'P': 0})['P'] < self._threshold and \
                        self._world.get((x + 1, y), {'W': 0})['W'] < self._threshold and self._visited.get((x + 1, y),
                                                                                                           0) < 4:
            potentials['R'] = self._world.get((x + 1, y), {'P': 0})['P'] + self._world.get((x + 1, y), {'W': 0})[
                'W'] + (self._visited.get((x + 1, y), 0) / sum)
            self._n = potentials['R']
        if self.validMove(x, y + 1) and self._world.get((x, y + 1), {'P': 0})['P'] < self._threshold and \
                        self._world.get((x, y + 1), {'W': 0})['W'] < self._threshold and self._visited.get((x, y + 1),
                                                                                                           0) < 4:
            potentials['U'] = self._world.get((x, y + 1), {'P': 0})['P'] + self._world.get((x, y + 1), {'W': 0})[
                'W'] + (self._visited.get((x, y + 1), 0) / sum)
            self._n = potentials['U']
        if self.validMove(x - 1, y) and self._world.get((x - 1, y), {'P': 0})['P'] < self._threshold and \
                        self._world.get((x - 1, y), {'W': 0})['W'] < self._threshold and self._visited.get((x - 1, y),
                                                                                                           0) < 4:
            potentials['L'] = self._world.get((x - 1, y), {'P': 0})['P'] + self._world.get((x - 1, y), {'W': 0})[
                'W'] + (self._visited.get((x - 1, y), 0) / sum)
            self._n = potentials['L']
        '''

        return potentials


    def possible_moves_helper(self, x,y, sum, potentials, dir):
        if self.validMove(x, y) and self._world.get((x, y), {'P': 0})['P'] < self._threshold and \
        self._world.get((x, y), {'W': 0})['W'] < self._threshold and self._visited.get((x, y), 0) < 4:
            
            potentials[dir] = self._world.get((x, y), {'P': 0})['P'] + self._world.get((x, y), {'W': 0})[
                'W'] + (self._visited.get((x, y), 0) / sum)

            self._n = potentials[dir]
            

    def validLocation(self, x, y):
        return (x > -1 and y > -1 and x <= self._xmax and y <= self._ymax)

    def validMove(self, x, y):
        if not ((self.validLocation(x, y) and self._visited.get((x, y), 0) < 9)):
            return False
        if (self.WumpusLocation == None or self._wumpus_shot):
            return True
        return not (x == self.WumpusLocation[0][0] and y == self.WumpusLocation[0][1])




        # ======================================================================
        # YOUR CODE ENDS
        # ======================================================================

