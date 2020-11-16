# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import distanceCalculator
import random
import time
import util
import sys
from game import Directions
import game
from util import nearestPoint

#################
# Team creation #
#################


def createTeam(firstIndex, secondIndex, isRed,
               first='offensiveReflexAgent', second='defensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]


##########
# Agents #
##########
offenseIndex = None
defenseIndex = None

# Define the dummy class here
# new comment after init upstream branch remotely
class DummyAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """
  pacmanIndex = 0
  backHome = False
  step = 0
  defense_time = 300  # 300
  timeLine = [300, 600, 900, 1000]

  def __init__(self, *args, **kwargs):
    self.chasedByGhost = False
    self.featuresList = ['DisToGhost', 'DisToPacman']
    self.alpha = 0.1
    self.gamma = 0.9
    CaptureAgent.__init__(self, *args, **kwargs)

  def registerInitialState(self, gameState):

    self.initial_food = self.getFood(gameState).count()

    self.start = gameState.getAgentPosition(self.index)
    CaptureAgent.registerInitialState(self, gameState)

  def goHome(self, gameState, timeleft):
    gap = [1, 2, 3]
    if (timeleft - 300 in gap or timeleft - 600 in gap or timeleft - 900 in gap) and gameState.getAgentState(self.index).isPacman:
      print("!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  300X time to return home !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
      return True
    if len(self.getFoodYouAreDefending(gameState).asList()) <= 6:
      return True
    if timeleft < 100:
      return True

  def chooseAction(self, gameState):

    actions = gameState.getLegalActions(self.index)
    values = [self.evaluate(gameState, a) for a in actions]

    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    foodLeft = len(self.getFood(gameState).asList())
    timeleft = gameState.data.timeleft

    # print(self.backHome)
    if foodLeft <= 2 or self.goHome(gameState, timeleft) or self.backHome:
      self.backHome = True
      pos2 = gameState.getAgentPosition(self.index)
      if self.getMazeDistance(self.start, pos2) < 3:
        self.backHome = False

      if not gameState.getAgentState(self.index).isPacman and self.backHome:   # ghost, defense
        print('===================Turn to defense!===========================!!!')
        self.backHome = False
        if timeleft < 0.5 * self.defense_time or len(self.getFoodYouAreDefending(gameState).asList()) <= 5:
          self.backHome = True
        bestDist = 9999
        bestAction = None

        for action in actions:
          tmp = 9999
          nextState = self.getSuccessor(gameState, action)
          nextPosition = nextState.getAgentPosition(self.index)
          enemies = [nextState.getAgentState(i) for i in self.getOpponents(nextState)]
          currentEnemies = [nextState.getAgentState(i) for i in self.getOpponents(gameState)]
          pacman_position = [a.getPosition() for a in enemies if a.isPacman and a.getPosition() != None]
          cur_pacman_position = [a.getPosition() for a in currentEnemies if a.isPacman and a.getPosition() != None]
          if len(pacman_position) > 0:
            for pos in cur_pacman_position:
              if nextPosition == pos:
                print('next step eats pacman !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!')
                return action

            close_pacman_position = pacman_position[0]
            for pacman_pos in pacman_position:
              if self.getMazeDistance(pacman_pos, nextPosition) < tmp:
                tmp = self.getMazeDistance(pacman_pos, nextPosition)
                close_pacman_position = pacman_pos
            dist = self.getMazeDistance(close_pacman_position, nextPosition)
            if dist < bestDist:
              bestAction = action
              bestDist = dist
        if bestAction == None:
          bestAction = Directions.STOP  # random.choice(bestActions)

        return bestAction

      if gameState.getAgentState(self.index).isPacman:
        print("Go home or not ? : ======>" + str(self.backHome))

      if gameState.getAgentState(self.index).isPacman and self.backHome:
        print('===================Go home!===========================!!!')
        return random.choice(bestActions)
        '''
        bestDist = 9999
        for action in actions:
          successor = self.getSuccessor(gameState, action)
          pos2 = successor.getAgentPosition(self.index)
          dist = self.getMazeDistance(self.start, pos2)
          if dist < bestDist:
            bestAction = action
            bestDist = dist
        return bestAction
        '''

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def updateW(self, gameState, action, reward, features):
    '''
    w[i] w[i]+ alpha * correction * f[i](s,a),

    correction=R(s,a)+ gamma *
    '''
    nextState = self.getSuccessor(gameState, action)
    nextActionList = nextState.getLegalActions(self.index)

    reward = self.getReward(gameState, action)
    Q_old = self.getQvalue(gameState, action, features)
    Q_nextAll = [self.getQvalue(nextState, nextAction, features) for nextAction in nextActionList]
    Q_newMax = max(Q_nextAll)
    diff = reward + self.gamma * Q_newMax - Q_old
    '''
    print('Reward: =====' + str(reward))
    print('Diff:========' + str(diff))
    '''
    for feat in self.featuresList:
      self.weights[feat] += self.alpha * diff * features[feat]

  def getReward(self, gameState, action):
    if self.getSuccessor(gameState, action) is None:
      return 0

    reward = 0
    nextState = self.getSuccessor(gameState, action)

    # Find out if we got a pac dot. If we did, add 10 points.
    nextPosition = nextState.getAgentPosition(self.index)
    currentFood = self.getFood(gameState).asList()
    nextFood = self.getFood(nextState).asList()

    if len(currentFood) > len(nextFood):
      reward += 10

    nextState = self.getSuccessor(gameState, action)
    enemies = [nextState.getAgentState(i) for i in self.getOpponents(nextState)]
    ghost_position = [a.getPosition() for a in enemies if not a.isPacman and a.getPosition() != None]
    if len(ghost_position) > 0:
      disToGhost = [self.getMazeDistance(nextPosition, gpos) for gpos in ghost_position]
      minDisToGhost = min(disToGhost)
      if minDisToGhost == 1 or nextPosition in ghost_position:
        reward -= 100

    return reward

  def getQvalue(self, gameState, action, features):
    weights = self.weights
    return features * weights

  '''
  Below are some helper functions
  '''

  def isGhost(self, gameState, index):
    """
    Returns true ONLY if we can see the agent and it's definitely a ghost
    """
    opp_position = gameState.getAgentPosition(index)
    if opp_position is None:
      return False

    if gameState.isOnRedTeam(self.index):
      return opp_position[0] > gameState.getWalls().width / 2
    else:
      return opp_position[0] <= gameState.getWalls().width / 2

  def isScared(self, ghost):
    """
    Says whether or not the given agent is scared
    """
    for gh in ghost:
      if gh.scaredTimer > 0 and gh.scaredTimer < 20:
        return True
    return False

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    reward = self.getReward(gameState, action)
    # self.updateW(gameState, action, reward, features)

    # if gameState.getAgentState(self.index).isPacman:
    #print('Action: ' + str(action) + ', value: ' + str(features * self.getWeights(gameState, action)))

    return features * self.getWeights(gameState, action)


class defensiveReflexAgent(DummyAgent):
  weights = util.Counter()
  weights['DisToPacman'] = -1000  # -50
  #weights['DisToDefendingFood'] = -10
  weights['reverse'] = -10
  weights['stuck'] = -20
  weights['DisToBorder'] = -5
  weights['DisToCap'] = -50  # -50

  def chooseMidPoint(self, nextState, start, width, height):
    gap1 = [-2, -3, -4, -5, -1]
    gap2 = [2, 3, 4, 5, 1]
    if start[0] < 0.5 * width:
      for i in range(5):
        x = (int)(0.5 * width + gap1[i])
        y = (int)(0.5 * height + gap1[i])
        if not nextState.hasWall(x, y):
          return (x, y)
    else:
      for i in range(5):
        x = (int)(0.5 * width + gap2[i])
        y = (int)(0.5 * height + gap2[i])
        if not nextState.hasWall(x, y):
          return (x, y)

  def getFeatures(self, gameState, action):

    walls = gameState.getWalls()
    wallsList = walls.asList()
    mazeSize = walls.width * walls.height
    midPoint = self.chooseMidPoint(self.getSuccessor(gameState, action), self.start, walls.width, walls.height)

    features = util.Counter()
    if action == Directions.STOP:
      features['stuck'] = 1000
    # get self position
    currentPosition = gameState.getAgentPosition(self.index)
    nextState = self.getSuccessor(gameState, action)
    nextPosition = nextState.getAgentPosition(self.index)

    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev:
      features['reverse'] = 1

    capsuleList = self.getCapsulesYouAreDefending(gameState)
    disToCap = [self.getMazeDistance(f, nextPosition) for f in capsuleList]
    if len(disToCap) > 0:
      minDisToCapsule = min(disToCap)
      features['DisToCap'] = 1.0 * minDisToCapsule

    # offense: get position of the ghost and closest dis to it
    enemies = [nextState.getAgentState(i) for i in self.getOpponents(nextState)]
    pacman_position = [a.getPosition() for a in enemies if a.isPacman and a.getPosition() != None]
    pacman_State = [a for a in enemies if a.isPacman]

    foodList = self.getFoodYouAreDefending(nextState).asList()
    disToFood = [self.getMazeDistance(f, nextPosition) for f in foodList]
    #minDisToFood = min(disToFood)
    #features['DisToDefendingFood'] = 1.0 * minDisToFood

    # gets closer to border
    DisToBorder = self.getMazeDistance(nextPosition, midPoint)
    features['DisToBorder'] = DisToBorder
    if len(pacman_State) > 0 or len(pacman_position) > 0:
      features['DisToBorder'] = 0

    # Defense: Dis to pacman:
    if len(pacman_position) > 0:
      disToPacman = [self.getMazeDistance(nextPosition, ppos) for ppos in pacman_position]
      minDisToPacman = min(disToPacman)
      features['DisToPacman'] = 1.0 * minDisToPacman
      if nextState.getAgentState(self.index).scaredTimer > 0:
        features['DisToPacman'] = -1.0 * minDisToPacman
    else:  # NOT within detection range
      features['DisToPacman'] = 0

    # if not gameState.getAgentState(self.index).isPacman:
      # print('Action: ' + str(action) + ', feature numFood: ' + str(features['numFood']))
      #print('Action: ' + str(action) + ', feature disToFood: ' + str(features['DisToFood']))
      #print('Defending! Action: ' + str(action) + ', feature disToPacman: ' + str(features['DisToPacman']))

    return features

  def getWeights(self, gameState, action):
    return self.weights


class offensiveReflexAgent(DummyAgent):

  weights = util.Counter()

  weights['DisToGhost'] = 100
  weights['DisToFood'] = -20
  # weights['numFood'] = -80   # -80
  weights['DisToCapsule'] = -50
  weights['cornerPos'] = -500  # -10
  weights['stuck'] = -20  # -20
  weights['goHome'] = -100

  def getFeatures(self, gameState, action):
    '''
    1. distance to nearest ghost(offense), to pacman(defense)
    (If scared, increase Q feature val)
    2. distance to nearest food
    3. distance to power capsule
    4. punish 'corner' food when we are chased 
    '''
    walls = gameState.getWalls()
    width = walls.width
    height = walls.height
    wallsList = walls.asList()
    mazeSize = walls.width * walls.height

    features = util.Counter()
    # get self position
    currentPosition = gameState.getAgentPosition(self.index)
    nextState = self.getSuccessor(gameState, action)
    nextPosition = nextState.getAgentPosition(self.index)

    if action == Directions.STOP:
      features['stuck'] = 1.0

    # offense: get position of the ghost and closest dis to it
    enemies = [nextState.getAgentState(i) for i in self.getOpponents(nextState)]
    ghost_position = [a.getPosition() for a in enemies if not a.isPacman and a.getPosition() != None]
    old_enemies = [nextState.getAgentState(i) for i in self.getOpponents(gameState)]
    old_ghost_position = [a.getPosition() for a in old_enemies if not a.isPacman and a.getPosition() != None]
    ghost_state = [a for a in enemies if not a.isPacman and a.getPosition() != None]
    pacman_position = [a.getPosition() for a in enemies if a.isPacman and a.getPosition() != None]
    if len(ghost_position) > 0:
      disToGhost = [self.getMazeDistance(nextPosition, gpos) for gpos in ghost_position]
      minDisToGhost = min(disToGhost)

      if minDisToGhost <= 5 and not self.isScared(ghost_state):
        self.chasedByGhost = True

      if self.isScared(ghost_state):
        # print('========================Scared!!!!!!!!!!================')
        # print(minDisToGhost)
        features['DisToGhost'] = -1.0 * minDisToGhost
        if nextPosition in old_ghost_position:
          features['DisToGhost'] = 0
      else:
        features['DisToGhost'] = 1.0 * minDisToGhost
    else:  # NOT within detection range
      features['DisToGhost'] = 0

    # Dis to the closest food, capsule

    foodList = self.getFood(nextState).asList()
    old_foodList = self.getFood(gameState).asList()
    numFood = len(foodList) - len(old_foodList)
    #features['numFood'] = 1.0 * numFood

    # find nearest food and if it is bad position:
    nearDis = 99999
    nearestFood = None
    for foodPos in old_foodList:
      if nextPosition == foodPos:
        nearDis = 0
        nearestFood = foodPos
        break
      else:
        tmpDis = self.getMazeDistance(foodPos, nextPosition)
        if tmpDis < nearDis:
          nearDis = tmpDis
          nearestFood = foodPos

    disToFood = [self.getMazeDistance(f, nextPosition) for f in foodList]
    minDisToFood = min(disToFood)
    features['DisToFood'] = 1.0 * minDisToFood

    # next food to eat
    for foodPos in old_foodList:
      if nextPosition == foodPos:
        features['DisToFood'] = 0
        break

    if nearestFood and self.isSrd(nearestFood, nextState, width, height):
      features['DisToFood'] += 5

    # go home !
    disToHome = self.getMazeDistance(self.start, nextPosition)
    if self.backHome:
      features['goHome'] = 1.0 * disToHome

    capsuleList = self.getCapsules(gameState)
    disToCap = [self.getMazeDistance(f, nextPosition) for f in capsuleList]
    if len(disToCap) > 0:
      minDisToCapsule = min(disToCap)
      features['DisToCapsule'] = 1.0 * minDisToCapsule

    # punish 'corner' food when we are chased
    # first decide if we are chased or not

    self.step += 1
    if self.chasedByGhost:
      #self.weights['DisToGhost'] *= 10
      self.weights['stuck'] = -2 * self.weights['DisToGhost']
      # print('chased by Ghost, step:' + str(self.step))
      if self.isSrd(nextPosition, nextState, width, height):
        features['cornerPos'] = 1.0
        #features['DisToFood'] += 100
    else:
      features['cornerPos'] = 0.0
      '''
      nx = nextPosition[0]
      ny = nextPosition[1]
      countSrd = 0
      srdPos = [(nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1)]
      for pos in srdPos:
        if nextState.hasWall(pos[0], pos[1]):
          countSrd += 1
      if countSrd >= 3:
        # print('Corner on the go!!!, step: ' + str(self.step))
        features['cornerPos'] = 1.0  # Pretty much Unwanted behavior
    else:
      features['cornerPos'] = 0.0
      '''
    self.chasedByGhost = False
    '''
    if gameState.getAgentState(self.index).isPacman:
      print('Action: ' + str(action) + ', feature disToGhost: ' + str(features['DisToGhost']))
      print('Action: ' + str(action) + ', feature disToFood: ' + str(features['DisToFood']))
      print('Action: ' + str(action) + ', feature cornerPos: ' + str(features['cornerPos']))
      print('Action: ' + str(action) + ', weights DisToGhost: ' + str(self.weights['DisToGhost']))
      print('Action: ' + str(action) + ', weights DisToFood: ' + str(self.weights['DisToFood']))
      print('Action: ' + str(action) + ', weights cornerPos: ' + str(self.weights['cornerPos']))
    '''

    return features

  def isSrd(self, nextPosition, nextState, width, height):
    flag = False
    nx = nextPosition[0]
    ny = nextPosition[1]
    countSrd = 0
    srdPos = [(nx + 1, ny), (nx - 1, ny), (nx, ny + 1), (nx, ny - 1), (nx + 2, ny), (nx - 2, ny), (nx, ny + 2), (nx, ny - 2)]
    for pos in srdPos[0:4]:
      if self.validPosition(pos[0], pos[1], width, height) and nextState.hasWall(pos[0], pos[1]):
        countSrd += 1
    if countSrd >= 3:
      return True
    elif countSrd == 2:
      for pos in srdPos:
        if self.validPosition(pos[0], pos[1], width, height) and not nextState.hasWall(pos[0], pos[1]):
          tx = pos[0]
          ty = pos[1]
          countSrd = 0
          srdPos2 = [(tx + 1, ty), (tx - 1, ty), (tx, ty + 1), (tx, ty - 1)]
          for pos in srdPos2:
            if self.validPosition(pos[0], pos[1], width, height) and nextState.hasWall(pos[0], pos[1]):
              countSrd += 1
          if countSrd >= 3:
            return True
    return False

  def validPosition(self, x, y, width, height):
    if x > 0 and x < width and y > 0 and y < height:
      return True
    else:
      return False

  def getWeights(self, gameState, action):
    return self.weights
