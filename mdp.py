from utils import argmax, vector_add, orientations, turn_right, turn_left
from collections import defaultdict
import random
import numpy as numpy









'''

An MDP is defined by
	initial state - s0
	goal state - sg

'''
	
class MDP:
	def __init__(self, init, actions, terminals, transitions=None, reward=None, states=None, gamma=0.9):
		if not (0 < gamma <= 1):
			raise ValueError("Gamma must be greater than 0 and at most 1.")

		#If states were not passed in as parameter, collect them from transition tables
		self.states = = states or self.get_states_from_transitions(transitions)

		self.init = init

		if isinstance(actions, list):
			#If every state has the same actions available then actions is a list
			self.actions = actions

		elif isinstance(actions, dict):
			#If states can have different actions available then actions is a dict
			self.actions = actions

		self.terminals = terminals
		self.transitions = transitions or {}
		if not self.transitions:
			print "Warning: Transition table is empty."

		self.gamma = gamma

		self.reward = reward or {s: 0 for s in self.states}

	def R(self,s):
		'''Return numeric reward value for state s.'''

		return self.reward[s]

	def T(self, s, a):
		'''Return transition model for (s,a) pair as a list of (probability,s') pairs.'''

		if not self.transitions:
			raise ValueError("Transition Model is Missing.")
		else:
			return self.transitions[s][a]

	def actions(self,s):
		'''Return list of actions that are available to agent in state s.
		Default is a fixed list of actions except for terminal states.'''

		if s in self.terminals:
			return [None]
		else:
			return self.actions

	def get_states_from_transitions(self, transitions):
		if isinstance(transitions,dict):
			s1 = set(transitions.key())
			s2 = set(tr[1] for actions in transitions.values()
				           for effects in actions.values()
				           for tr in effects)
			return s1.union(s2)
		else:
			print "Failure to retrieve states from transitions."
			return None

	def check_consistency(self):

		#Check that all states in transitions are valid
		assert set(self.states) == self.get_states_from_transitions(self.transitions)

		#Check that init is a valid state
		assert self.init in self.states

		#Check reward function for each state
		assert set(self.reward.keys()) == set(self.states)

		#check that all terminals are valid states
		assert all(t in self.states for t in self.terminals)

		#Check that probability distributions for all actions sum to 1
		for s1, actions in self.transitions.items():
			for a in actions.keys():
				s = 0
				for o in actions[a]:
					s += o[0]
				assert abs(s-1) < 0.001


class MDP2(MDP):
	'''
	Inherits from MDP. Handels terminal states, and transitions to and from terminal states better.
	'''

	def __init__(self, init, actions, terminals, transitions, reward=None, gamma=0.9):
		MDP.__init__(self,init,actions,terminals,transitions,reward,gamma=gamma)

	def T(self,s,a):
		if a is None:
			return [(0,0,s)]
		else:
			return self.transitions[s][a]


class GridMDP(MDP):
	'''
	2-D grid MDP specified as list of lists of rewards. Use None for unreachable states
	Specify terminal states.
	Actions are (x,y) unit vectors.
	'''

	def __init__(self, grid, terminals, init=(0,0), gamma=0.9):
		grid.reverse() #This is to make row 0 be on bottom not top
		reward = {}
		states = set()
		self.rows = len(grid)
		self.cols = len(grid[0])
		self.grid = grid
		for x in range(self.cols):
			for y in range(self.rows):
				if grid[y][x]:
					states.add((x,y))
					reward[(x,y)] = grid[y][x]
		self.states = states
		actions = orientations
		transitions = {}
		for s in states:
			transitions[s] = {}
			for a in actions:
				transitions[s][a] = self.calculate_T(s,a)
		MDP.__init__(self, init, actions=actions, terminals=terminals, transitions=transitions, reward=reward, states=states, gamma=gamma)

	def calculate_T(self,s,a):
		if a:
			return [(0.8, self.go(s, a)),
					(0.1, self.go(s, turn_right(a))),
					(0.1, self.go(s, turn_left(a)))]
		else:
			return [(0.0, s)]

	def T(self,s,a):
		return self.transitions[s][a] if a else [(0.0, state)]

	def go(self,s,direction):
		'''Return the state that results from going in direction from s.'''

		s1 = vector_add(s,direction)
		return s1 if s1 in self.states else s

	def to_grid(self, mapping):
		'''Convert a mapping from (x,y) to v into a [[..., v, ...]] grid.'''

		return list(reversed([[mapping.get((x,y), None)
							   for x in range(self.cols)]
							   for y in range(self.rows)]))

	def to_arros(self, policy):
		chars = {(1,0):'>', 
				 (0,1):'^', 
				(-1,0):'<', 
				(0,-1):'v', 
				  None:'.'}
		return self.to_grid({s:chars[a] for (s,a) in policy.itmes()})