# -*- coding: utf-8 -*-
"""
Created on Thu Jan  6 09:50:23 2022

@author: Jason
"""
import pickle
from Tetris import Tetris
import pygame
import numpy as np

agent = pickle.load(open('best.pickle_720', 'rb'))
# W = np.array([-12.63, 6.6, -9.22, -19.77, -13.08, -10.49, -1.61, -24.04])

rendering = True
fps = 15

env = Tetris(False, None, [], rendering)

clock = pygame.time.Clock()




# Definitions and default settings
run = True
action_taken = False
slow = True
done = False

while run:
    if rendering:
        clock.tick(fps)
    

    # Process input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                run = False
            elif event.key == pygame.K_r:
                env.reset()
            elif event.key == pygame.K_p:
                pause = True
                while pause:
                    clock.tick(40)
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            pygame.quit()
                            run = False
                            pause = False
                        if event.type == pygame.KEYDOWN:
                            if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                                pygame.quit()
                                run = False
                                pause = False
                            elif event.key == pygame.K_p:
                                pause = False
    
    # Let agent determine and take next action
    # Find all final_states and evaluate them
    states = env.get_final_states()
    evaluations = env.get_evaluations(states)
    
    # Pass the evaluation for each state into the NN
    outputs = [agent.activate(input) for input in evaluations]
    # outputs = [np.dot(input, W) for input in evaluations]
    

    # Go to best scored state
    best_index = outputs.index(max(outputs))
    best_state = states[best_index]
    done, _ = env.place_state(best_state) 
    
    while False and done:
        clock.tick(40)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                run = False
                done = False
            if event.type == pygame.KEYDOWN:
                if event.key in [pygame.K_ESCAPE, pygame.K_q]:
                    pygame.quit()
                    run = False
                    done = False
                elif event.key == pygame.K_p:
                    done = False
    
    
    
    # -12.63*lock_height+6.6*erodeded_cells-9.22*row_transitions-19.77*column_transitions\
        # -13.08*holes-10.49*cum_wells-1.61*hole_depth-24.04*rows_holes
    
    
    if rendering:
        env.render()
    
pygame.quit()





