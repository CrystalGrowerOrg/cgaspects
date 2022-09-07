# ------------------------------------------------------------------------------+
#
#	Alvin Jenner Walisinghe
#	Simple Particle Swarm Optimization (PSO) with Python
#	Created: 31-JUL-2022
#	Python 3.10
#
# ------------------------------------------------------------------------------+

from chmpy import Crystal
import numpy as np
import pandas as pd
from pathlib import Path
from shutil import copy
import matplotlib.pyplot as plt
from random import random
from random import uniform
from subprocess import Popen, PIPE


initial= [5, 5, 5]                 # initial starting location [x1,x2...]
bounds= [(-10, 10), (-10, 10), (-10, 10)]   # input bounds [(x1_min,x1_max),(x2_min,x2_max)...]

class Particle_Swarm_Optimisation:
    def __init__(self, init_pos, search_bounds, num_particles=10, maxiter=100):

        self.num_dimensions = len(init_pos)     # number of CrystalGrower variables
        print('DIMENSIONS:', self.num_dimensions)
        self.bounds = search_bounds                    # bounds for the search-space
        self.num_particles = num_particles      # number of particles used in the search
        self.maxiter = maxiter                  # number of optimisation steps
        self.init_pos = init_pos
        self.maxiter = maxiter

        self.swarm = []

        self.pos_best_i = []          # best position individual
        self.distance_best_i = -1          # best error individual
        self.err_i = -1               # error individual

        self.distance_best_g = -1                   # best error for group
        self.pos_best_g = [5, 5, 5, 5]               # best position for group

        # self.parent_path = path


    def print_swarm(self, swarm):
        for idx, particle in enumerate(swarm):
            print(f'Particle_{idx+1}\nPosition: {particle[0]}\nVelocity: {particle[1]}')
    
    def run_crystalgrower(self, cg_path, dir_path='.'):

        input_path = Path(dir_path) / 'addinput.txt'
        with open(input_path, encoding="utf-8") as file:
            p = Popen([cg_path], stdin=file, stdout=PIPE, cwd=dir_path)
        print(p.communicate())

    def create_particle_folder(self, path, cycle, particle_number):
        parent_folder = Path(path)
        particle_folder = Path(path) / f'PSO_cycle{cycle}' / f'partcle_{particle_number}'
        particle_folder.mkdir(parents=True, exist_ok=True)
        copy(parent_folder / 'input.txt', particle_folder)
        copy(parent_folder / 'addinput.txt', particle_folder)
        copy(parent_folder / 'net.txt', particle_folder)

        return particle_folder
    
    def init_particle(self):
        position_i = []
        velocity_i = []
        for i in range(0, self.num_dimensions):
            velocity_i.append(uniform(-1, 1))
            position_i.append(uniform(self.bounds[i][0], self.bounds[i][1]))
            # self.position_i.append(init_pos[i])

        # print(f'Position: {position_i} \n Velocity: {velocity_i}')
        return (position_i, velocity_i)

    def init_swarm(self, path):
        for num in range(0, self.num_particles):
            self.swarm.append(self.init_particle())
            self.create_particle_folder(path, 0, num)

        print('INITIAL SWARM :::::::::\n')
        self.print_swarm(self.swarm)


    def cost_func(self, x):
        total = 0
        length = len(x)
        for i in range(length):
            total += x[i] ** 2

        return total

    # evaluate current fitness
    def evaluate(self, position_i):
        distance_i = self.cost_func(position_i)

        # check to see if the current position is an individual best
        if distance_i < self.distance_best_i or self.distance_best_i == -1:
            self.pos_best_i = position_i.copy()
            self.distance_best_i = distance_i

        return distance_i

    # update new particle velocity
    def updated_velocity(self, position_i, velocity_i, pos_best_g):
        w = 0.5       # constant inertia weight (how much to weigh the previous velocity)
        c1 = 1        # cognative constant
        c2 = 2        # social constant

        for i in range(0, self.num_dimensions):
            r1 = random()
            r2 = random()
            
            vel_cognitive = c1 * r1 * (self.pos_best_i[i] - position_i[i])
            vel_social = c2 * r2 * (pos_best_g[i] - position_i[i])
            velocity_i[i] = w * velocity_i[i] + vel_cognitive + vel_social

        return velocity_i

    # update the particle position based off new velocity updates
    def updated_position(self, position_i, velocity_i, pos_best_g):

        velocity_i = self.updated_velocity(position_i, velocity_i, pos_best_g)

        for i in range(0, self.num_dimensions):
            position_i[i] = position_i[i] + velocity_i[i]
            
            # adjust maximum position if necessary
            if position_i[i] > self.bounds[i][1]:
                position_i[i] = self.bounds[i][1]
            # adjust minimum position if neseccary
            if position_i[i] < self.bounds[i][0]:
                position_i[i] = self.bounds[i][0]

        return (position_i, velocity_i)

    def minimize(self, verbose=True):
        # begin optimization loop
        i = 0
        while i < self.maxiter:

            update_swarm = []                

            # cycle through particles in swarm and evaluate fitness
            for particle in self.swarm:
                position_i = particle[0]
                velocity_i = particle[1]
                distance_i = self.evaluate(position_i)

                # determine if current particle is the best (globally)
                if self.distance_best_i < self.distance_best_g or self.distance_best_g == -1:
                    self.pos_best_g = position_i
                    self.distance_best_g = float(distance_i)
                    print(distance_i)

                new_pos, new_vel = self.updated_position(position_i, velocity_i, self.pos_best_g)
                update_swarm.append([(new_pos), (new_vel)])


            self.swarm = update_swarm
            
                    
            if verbose:
                print(f'iter: {i:>4d} best solution: {self.distance_best_g:10.6f}')
                if i == self.maxiter - 1:
                    self.print_swarm(self.swarm)


            i+=1

        # print final results
        if verbose:
            print('\nFINAL SOLUTION:')
            print(f'   > {self.pos_best_g}')
            print(f'   > {self.distance_best_g}\n')

        return self.distance_best_g, self.pos_best_g

    def plotting(self, x, y, z):
                # Plotting prepartion
        pass




#--- RUN ----------------------------------------------------------------------+


PSO = Particle_Swarm_Optimisation(init_pos=initial, search_bounds=bounds)
# PSO.init_swarm(path='/Users/alvin/CrystalGrower/CrystalSystems/AdipicAcid/PSO/')
# PSO.minimize()
PSO.run_crystalgrower("/Users/alvin/CrystalGrower/CrystalSystems/CrystalGrower_X_1_5_0_mac", 
                    dir_path='/Users/alvin/CrystalGrower/CrystalSystems/AdipicAcid/PSO/')

#--- END ----------------------------------------------------------------------+