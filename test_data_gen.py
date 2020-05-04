# -*- coding: utf-8 -*-
"""
Created on Sat May  2 02:16:30 2020

@author: Mikhail Kuts
"""
import numpy as np

def get_initial_coordinates(n_particles, box_width):
    x_coord = np.random.rand(n_particles,1)*box_width
    y_coord = np.random.rand(n_particles,1)*box_width
    z_coord = np.random.rand(n_particles,1)*box_width
    return np.concatenate((x_coord,y_coord, z_coord), axis = 1)

def get_initial_velocities(n_particles, max_velocit):
    x_vel = 2*max_velocity*(np.random.rand(n_particles,1)-0.5)
    y_vel = 2*max_velocity*(np.random.rand(n_particles,1)-0.5)
    z_vel = 2*max_velocity*(np.random.rand(n_particles,1)-0.5)
    return np.concatenate((x_vel, y_vel, z_vel), axis = 1)

def take_step(coords, vels, dt, box_width):
    coords +=vels*dt
    
    vels[coords>box_width] = -vels[coords>box_width]
    vels[coords<0] = -vels[coords<0]
    return coords

def save_system(file, system_par, system):
    file.write("{}\n".format(system_par["particles"]))
    file.write("{}\n".format(system_par["box_width"]))
    file.write("{}\n".format(system_par["steps_num"]))
    file.write("{}\n".format(system_par["time_step"]))
    for i in range(system_par["steps_num"]):
        file.write("\n")
        for j in range(system_par["particles"]):
            file.write("{} {} {} {} {} {}\n".format(*system[j,:,i]))
        

n_particles = 5
box_width = 10
max_velocity = 5

n_steps = 10000
dt = 0.01

coords = get_initial_coordinates(n_particles, box_width)
vels = get_initial_velocities(n_particles, max_velocity)
system = np.zeros([n_particles,6,n_steps])
for i in range(n_steps):
    coords = take_step(coords, vels, dt, box_width)
    system[:,:3,i] = coords
    system[:,3:,i] = vels
    
file = open("system.txt","w")
system_par = {"particles": n_particles,
              "box_width": box_width,
              "steps_num": n_steps,
              "time_step": dt}
save_system(file,system_par, system)
file.close()

    



