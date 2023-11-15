import os
import sys
import random 
import json
import math
import utils
import time
import config
import numpy
random.seed(73)

class Agent:
    def __init__(self, table_config) -> None:
        self.table_config = table_config
        self.prev_action = None
        self.curr_iter = 0
        self.state_dict = {}
        self.holes =[]
        self.ns = utils.NextState()


    def set_holes(self, holes_x, holes_y, radius):
        for x in holes_x:
            for y in holes_y:
                self.holes.append((x[0], y[0]))
        self.ball_radius = radius


    def get_value(self, state):
        value = 0
        for ball, pos in state.items():
            d_min = math.inf
            for hole in self.holes:
                d = (hole[0] - pos[0])**2 + (hole[1] - pos[1])**2
                d_min = min(d, d_min)
            value += d_min
        return value


    def min_force(self, state, ball, angle):
        left = 0
        right = 1
        ball_x, ball_y = state[ball]
        for _ in range(10):
            mid = (left + right)/2
            next_state = self.ns.get_next_state(state, (angle, mid), 42)
            if ball not in next_state.keys() or next_state[ball][0] != ball_x or next_state[ball][1] != ball_y:
                right = mid
            else:
                left = mid
        return left

    def action(self, ball_pos=None):
        ## Code you agent here ##
        ## You can access data from config.py for geometry of the table, configuration of the levels, etc.
        ## You are NOT allowed to change the variables of config.py (we will fetch variables from a different file during evaluation)
        ## Do not use any library other than those that are already imported.
        ## Try out different ideas and have fun!
        
        cue_x, cue_y = ball_pos["white"]
        b, ball_x, ball_y = 0, 0, 0
        d_min = math.inf
        for ball, pos in ball_pos.items():
            if ball == 0 or ball == "white":
                continue
            for hole in self.holes:
                d = (hole[0] - pos[0])**2 + (hole[1] - pos[1])**2 + (cue_x - pos[0])**2 + (cue_y - pos[1])**2
                if d < d_min:
                    d_min = d
                    b = ball
                    ball_x, ball_y = pos
        
        d_min = math.inf
        for hole in self.holes:
            hole_x, hole_y = hole
            d = math.sqrt((ball_x - hole_x)**2 + (ball_y - hole_y)**2)
            if d > 500:
                continue
            x = ((d + 2*self.ball_radius)*ball_x - 2*self.ball_radius*hole_x)/d
            y = ((d + 2*self.ball_radius)*ball_y - 2*self.ball_radius*hole_y)/d
            
            a = math.atan((cue_x - x)/(abs(cue_y - y) + 1e-6))/math.pi
            if y > cue_y:
                a = (1 - a) if a > 0 else (abs(a) - 1)
                
            # a1 = abs((cue_x - x)/((cue_y - y) + 1e-6))
            # a2 = abs((hole[0] - x)/((hole[1] - y) + 1e-6))
            # strike_angle = (a1 - a2)/(1 + a1*a2)
            # print(strike_angle)
            
            if d < d_min:
                angle = a
                d_min = d 
            
        left = 0
        right = 1
        for _ in range(10):
            mid = (left + right)/2
            next_state = self.ns.get_next_state(ball_pos, (angle, mid), 42)
            if b not in next_state.keys() or next_state[b][0] != ball_x or next_state[b][1] != ball_y:
                right = mid
            else:
                left = mid
        
        return angle, min(left + 0.05 + d_min/2000, 0.8)
        
        