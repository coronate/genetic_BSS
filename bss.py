import random
import pandas as pd 
import numpy as np  
import random
import pandas as pd 
import numpy as np  
import operator
import copy
import utils_solver
from tqdm import tqdm
import time

from utils_genetic import score_chromosome, generate_population, look_solutions, \
                          save_solutions, sort_population, population_summary, select_topn, \
                          cross_mutate, solve_genetic_algorithm, report_genetic_results



def countSOLUCIONES(SOLUCIONES):
    count  = 0

    for i in SOLUCIONES.keys():
        count+= len(SOLUCIONES[i])
    return count

class Map(object):
    def __init__(self, num_estaciones, num_estados, MAX_COST):
        #TO DO: use bycicle_slots_cost and parking_slots_cost 
        #to upadte self.weights
        self.distances = utils_solver.mapaAleatorio( num_estaciones, num_estados)
        self.available_stations = list(self.distances.columns)
        self.parking_slots_cost = list()
        self.bycicle_slots_cost = list()
        self.weights      = self.distances.copy()
        self.all_stations = list(self.distances.columns)
        self.MAX_COST = MAX_COST
        self.car_positions =  list()

    def __repr__(self):
        repr_str =  "\n\t ------------------MAP---------------------"
        repr_str += "\nMap: \n\tmatrix\n\t available_stations \
         \n\t parking_slots_cost \n\t bycicle_slots_cost\n\t distances,weights: matrix"
        return repr_str


    def update_available_stations( self, FLEET):
        # For all car it remove from available_stations list all the spots in which cars
        #are allocated the it remove the already-route-assigned stations.
        self.available_stations = self.all_stations.copy()
        self.weights      = self.calculateWeights(FLEET)
        self.car_positions = list()
        for i in FLEET.fleet:
            car = FLEET.fleet[i]
            if car.position in self.available_stations: #Take away the stations thata are ocupied by some car.
                self.available_stations.remove(car.position)
                self.car_positions.append(car.position)

            for occupied_area_stations in car.subsystem_list: #Take away the stations that are assigned to a car as part of the optimization problem.
                if occupied_area_stations in self.available_stations:
                    self.available_stations.remove(occupied_area_stations)

    def calculateWeights(self, FLEET, next_time = False):
        """
        In this function we use all the available infromation to represent the expected cost
        of traveling from station A to station B

        for i in self.distances.columns:
            for j in self.distances.columns:
                distance =  self.distance.loc[i,j]
                parking_cost = self.parking_slots_cost[j]
                bycicle_cost = self.bycicle_slots_cost[j]

                weight = bycicle_cost + parking_cost + distances
        """
        #When the time advance we expect new bycycles to arrive at different stations.
        #This can be represented as a new iteration where the weighs of the MAP change.
        if next_time:
            #MAKE SOME FUCNTION WITH BIKES
            self.weights = self.weights.replace("X", -100) -1
            self.weights = self.weights.replace(-101, "X")
            self.weights = self.weights.replace(-1, 0)

        #TWe block the stations we the cars in the Fleet are located using the MAX_COST
        for i in FLEET.fleet:
            car = FLEET.fleet[i]
            for ind in self.weights.index: #station_1, station_2 ...  station_n
                self.weights.loc[ind , car.position] = self.MAX_COST
            
        return  self.weights #En lo que encontramos una funcion que represente



    def change_station(self, car, MAP):
        min_cost = 1000000
        av_st_min = ""
        if len(self.available_stations)>0:
            for av_st in self.available_stations:
                car.subsystem_list.append(av_st)
                car.set_subsystem(MAP)
                subsystem =  car.subsystem.replace("X", 0)
                total_cost_with_new_station =  subsystem.sum().sum()
                #print("\tTEST COST: {} => {}".format(av_st, total_cost_with_new_station))
                if total_cost_with_new_station < min_cost:
                    min_cost = total_cost_with_new_station
                    av_st_min = av_st
                else:
                    #There is an other station with better performance un car.subsystem
                    car.subsystem_list.remove(av_st)
            #print("New station inserted on car {} subsystem => {}".format( car.id_car, av_st_min ))
        else:
            print("There isn't any available_station in Fleet")
            #TO DO: In this part we can take the second worst cart and take the 
            #worst station inside it's subsystem_list.







"""
-----------------------------------------------------------------------------------------------------------------------------
"""

N_CARS        = 16
N_STATIONS    = 128
AREA_SIZE     = 7
N_STATES      = 10
SOLUCIONES    = dict()
MAX_COST      = N_STATES
MAX_COBERTURE = N_STATES
BITS_PER_STATION = N_STATIONS - N_CARS


MAP = Map(N_STATIONS, N_STATES, MAX_COST)

N = 10 
PC = .33
PM = .1
MAX_ITERATIONS = 10

FLEET = Fleet(AREA_SIZE, MAX_COBERTURE, N_STATIONS)

for j in range(N_CARS):
    id_car = j
    position = car_position[id_car]
    capacity = random.randint(5,20) #TO DO: each car have their on capcity
    car = Car( id_car, position, capacity )
    FLEET.insertCar(car)


FLEET.update_carsPosition()          #Save car positions in FLEET.positions
MAP.update_available_stations(FLEET) #Remove car positio and car subsytem from available_stations
FLEET.assignArea(MAP)                #Assign subsystem to each car
FLEET.solve_subsystems(MAP, SOLUCIONES,N_STATIONS, N_STATES)

POPULATION_X, solution = solve_genetic_algorithm( N, PC, PM, MAX_ITERATIONS, MAP, N_STATIONS, AREA_SIZE, MAX_COBERTURE, N_CARS, N_STATES, SOLUCIONES )



