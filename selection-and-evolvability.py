#
#
# Peter Turney, October 23, 2024
#
# selection-and-evolvability.py
#
# Selection and Evolvability in Cellular Automata
#
#
#
# RULE LOADER
# ===========
#
# This script will only work if you have the "Immigration.rule"
# and you have specified the folder in which the Immigration.rule
# is stored. 
#
# To activate the Immigration.rule, open Golly and enter the following:
#
# > Control > Set Algorithm > RuleLoader
#
# > Control > Set Rule... > OK
#
# > Enter a new rule: Immigration
# > Or select a named rule: Immigration
#
# The current rule is: Immigration:T60,60
#
#
# IMPORT
# ======
#
import golly
import numpy as np
import random as rand
import copy
#
#
# EXPERIMENT SETTINGS
# ===================
#
run_number       = 18           # assign a unique ID number for each run
population_size  = 2000         # each new birth requires one death
sample_size      = 40           # a sample of the population
max_births       = 500000       # run ends after this many births
num_steps        = 100          # number of steps for the Game of Life
prob_red         = 0.3          # probability of red
prob_blue        = 0.3          # probability of blue
prob_mutation    = 0.1          # probability of switching among white, red, blue
prob_selection   = 1.0          # probability of adding a fit seed and dropping unfit
evolvability     = 20           # 20x20 grid (10x10, 20x20, 30x30, 40x40)
adult_size       = 60           # the size of the grid is fixed at 60x60
#
# - the target (target_1() to target_5()) must be set below
#   #######################################################
#
# - record the settings
log_file = open("./log_file" + str(run_number) + ".txt", "a+")
log_file.write("\n" + \
  "run number       = " + str(run_number)      + "\n" + \
  "population_size  = " + str(population_size) + "\n" + \
  "sample_size      = " + str(sample_size)     + "\n" + \
  "max_births       = " + str(max_births)      + "\n" + \
  "num_steps        = " + str(num_steps)       + "\n" + \
  "prob_red         = " + str(prob_red)        + "\n" + \
  "prob_blue        = " + str(prob_blue)       + "\n" + \
  "prob_mutation    = " + str(prob_mutation)   + "\n" + \
  "prob_selection   = " + str(prob_selection)  + "\n" + \
  "evolvability     = " + str(evolvability)    + "\n" + \
  "adult_size       = " + str(adult_size)      + "\n")
log_file.close()
#
#
# COLOURS
# =======
#
# We use the Immigration Game rule, which includes three colours.
#
white  = 0
red    = 1
blue   = 2
#
#
# ALGORITHM
# =========
#
# Algorithm = random mutation and/or evolutionary algorithm
#
# - "mutate_seed(seed_matrix, prob_mutation)"
# - "select_seed(seed_matrix, prob_selection)"
#
# - mutation only: prob_mutation = 0.2, prob_selection = 0.0
# - selection only: prob_mutation = 0.0, prob_selection = 0.2
# - mutation and selection: prob_mutation = 0.2, prob_selection = 0.2
#
#
# EVOLVABILITY
# ============
#
# Genome size = 10x10, 20x20, 30x30, 40x40
#
# - genome is a square grid, so we can use a single number
#   to specify the grid (10x10 --> 10)
# - increasing genome size = greater evolvability, more complex
#   genomes
# - evolvability specifies size of square gene
# - square gene should be placed in middle of 60x60 matrix
#
#
# SELECTION
# =========
#
# - we randomly sample a percentage of the population
# - 0.05 = 5%, 0.35 = 35%, ...
# - the most fit seed in the random sample is allowed to reproduce
# - the new child seed is copied from the selected seed and a small 
#   mutation is introduced for variety
# - the greater the sample size, the greater the selection pressure
# - selection specifies selection pressure
# - low pressure = 0.2, high pressure = 0.8
# - choose selection = 0.2 or 0.8
#
#
# FUNCTIONS
# =========
#
# Make a random seed matrix.
#
def make_seed_matrix(prob_red, prob_blue, evolvability):
  # - evolvability setting = size of the seed = 20 or 40
  # - 20 -> 20x20
  # - 40 -> 40x40
  # - seed_matrix size = 20 rows x 20 columns
  # - the Game of Life seems to prefer a density of
  #   about 0.3, so suggested probability setting is
  #   0.15 for prob_red and 0.15 for prob_blue
  # - rows and cols will be shifted by <-10, -10> so
  #   that the matrix is centered on the screen
  # - upper left  = <-10, -10>
  # - lower right = <+10, +10>
  # - start with a matrix of zeros
  seed_matrix = np.zeros([evolvability, evolvability], dtype=int)
  # - each colour is assigned an ID number
  white  = 0
  red    = 1
  blue   = 2
  # - fill in the matrix
  for i in range(evolvability):
    for j in range(evolvability):
      # - 0 = loss, 1 = win
      # - assume loss for both red and blue
      red_state  = 0
      blue_state = 0
      # - flip a biased coin for red
      if (rand.random() < prob_red):
        red_state = 1
      # - flip a biased coin for blue
      if (rand.random() < prob_blue):
        blue_state = 1
      # - what if there is a tie between red and blue?
      if ((red_state == 1) and (blue_state == 1)):
        # - it's a tie, so flip a coin
        if (rand.random() < 0.5):
          red_state  = 0
          blue_state = 1
        else:
          red_state  = 1
          blue_state = 0
      # - we've broken the tie
      if (red_state == 1):
        # - red == 1
        seed_matrix[i, j] = red
      if (blue_state == 1):
        # - blue == 2
        seed_matrix[i, j] = blue
      # - if neither red nor blue was selected, then 
      #   seed_matrix[i, j] is zero, since the seed_matrix is
      #   initialized to zero (white)
  return seed_matrix
#
# Given a seed matrix, write it on the Golly screen and let it grow.
# The result is an adult matrix.
#
def grow_matrix(seed_matrix, num_steps, adult_size):
  # - position the seed in the center of the grid
  seed_size   = len(seed_matrix)
  seed_offset = int(seed_size / 2)
  # - grow the seed
  rule_name = "Immigration"                  # Immigration.rule
  max_dimension = ":T60,60"                  # Torus of 60 x 60
  golly.new(rule_name)                       # initialize cells
  golly.setrule(rule_name + max_dimension)   # infinite plane
  golly.autoupdate(True)                     # update screen
  # - colours
  white  = 0 # white,255,255,255
  red    = 1 # red,255,0,0
  blue   = 2 # blue,0,0,255
  golly.setcolors([white,255,255,255,red,255,0,0,blue,0,0,255])
  # - write seed_matrix in the center of Golly screen
  for i in range(seed_size):
    for j in range(seed_size):
      # - get the colour of this matrix cell
      colour = seed_matrix[i][j]
      # - write the colour on the Golly screen
      # - center the 20x20 seed by moving up and left by seed_offset 10
      # - center the 40x40 seed by moving up and left by seed_offset 20
      golly.setcell(i - seed_offset, j - seed_offset, colour)
  # - run Golly until it grows to 60 x 60
  golly.run(num_steps)
  # - now make a box of 60 x 60 centered on the origin
  [left, top, width, height] = [-30, -30, 60, 60]
  # - read the 60 x 60 box into a matrix
  grown_matrix = np.zeros([height, width], dtype=int)
  for i in range(height):
    for j in range(width):
      grown_matrix[i][j] = golly.getcell(i + left, j + top)
  # - output the new grown_matrix
  return grown_matrix
#
# Given a seed matrix, swap some of the colours (red, white, blue).
# This is a simple random mutation of the seed.
#
def mutate_seed(seed_matrix, prob_mutation):
  # - each colour is assigned an ID number
  white  = 0
  red    = 1
  blue   = 2
  # - get seed_matrix size
  rows = len(seed_matrix)
  cols = len(seed_matrix[0])
  new_matrix = np.zeros([rows, cols], dtype=int)
  for i in range(rows):
    for j in range(cols):
      # - change some cells
      if (rand.random() < prob_mutation):
        # - if currently red, then switch to blue or white
        if (seed_matrix[i][j] == red):
          if (rand.random() < 0.5):
            new_matrix[i][j] = blue
          else:
            new_matrix[i][j] = white
        # - if currently blue, then switch to red or white
        elif (seed_matrix[i][j] == blue):
          if (rand.random() < 0.5):
            new_matrix[i][j] = red
          else:
            new_matrix[i][j] = white
        # - if currently white, then switch to red or blue
        else: # - must be white
          assert (seed_matrix[i][j] == white)
          if (rand.random() < 0.5):
            new_matrix[i][j] = red
          else:
            new_matrix[i][j] = blue
      # - otherwise don't change
      else:
        new_matrix[i][j] = seed_matrix[i][j]
  # - output the new matrix
  return new_matrix
#
# Sample a fraction of the population (e.g., 20%) and make a copy 
# of the most fit member of the sample. Mutate the copy. Remove the
# least fit member of the population and insert the mutated seed in
# its place.
#
def mutate_and_select_seed(population, sample_size, target, prob_mutation):
  # - we have two things going on here:
  #
  # - (1) mutation: random mutations introduce new varieties of seeds
  #   into the population
  # - increasing the number of mutations may speed up evolution, but it
  #   may also overlook useful seeds, which could prevent evolution from
  #   achieving its full potential
  # - *prob_mutation* is the parameter for controlling the pace of mutation
  # - we're assuming here that the population size is static, so each new
  #   mutation must be matched with a death
  # - TO TURN OFF MUTATION: set prob_mutation = 0
  #
  # - (2) selection: here we pick out an organism that is achieving high
  #   fitness and we make a copy of that organism and add it to the population
  # - with a static population size, we now have a duplicate, which might speed
  #   up evolution, but doesn't add anything fundamentally new
  # - ideally we want a combination of mutation and selection
  # - *sample_size* controls the pace of selection
  # - if sample_size is high, selection will converge faster, but might
  #   not achieve the best results
  # - if sample_size is low, selection may find better solutions, but it
  #   will take longer to achieve good results
  # - TO TURN OFF SELECTION: set sample_size = 0
  #
  # - "population" is a list of lists
  # - find the size of the population (e.g., 1000)
  # - population consists of about 1000 triples, where each
  #   triple has the form [[seed, adult, target], ..., [seed, adult, target]]
  population_size = len(population)
  # - sample_size should be smaller than population_size (e.g., 20)
  assert (sample_size <= population_size)
  assert (sample_size >= 0)
  # - each member of the population is a triple: 
  #   [seed, adult, target]
  # - sample a subset of the population (sample_size) and locate
  #   the least fit and most fit members of the subset
  least_fit_pos = rand.randrange(population_size)
  least_fit_val = population[least_fit_pos][2] # [2] = target
  most_fit_pos  = rand.randrange(population_size)
  most_fit_val  = population[most_fit_pos][2] # [2] = target
  # - now we're looking at sample_size different triples, but, in the
  #   end, we only want to use two of the triples
  for i in range(sample_size):
    pos = rand.randrange(population_size)
    val = population[pos][2]
    if (val < least_fit_val):
      least_fit_val = val
      least_fit_pos = pos
    if (val > most_fit_val):
      most_fit_val = val
      most_fit_pos = pos
  # - leave the most_fit triple as it is
  # - modify the least_fit triple as follows:
  # - (1) copy most_fit triple into least_fit triple
  # - in the triple, we only consider the seed, because the adult 
  #   and the target can be reconstructed from the seed
  population[least_fit_pos][0] = population[most_fit_pos][0] # seed matrix
  # - (2) use mutate_seed(seed_matrix, prob_mutation) to mutate
  #       least_fit triple (now a copy of most_fit triple)
  seed_matrix = population[least_fit_pos][0]
  seed_matrix = mutate_seed(seed_matrix, prob_mutation)
  # - output the new seed
  return seed_matrix
#
#
# TARGETS
# =======
#
# Given two matrices, measure how much they agree. The first
# matrix will be an organism that will be tested to see how
# fit it is. The other matrix will be a target that is used
# to measure the fitness of the first matrix.
#
def compare(adult, target, adult_size):
  # adult and target are both 60x60 matrices
  # adult_size = 60
  assert adult_size == 60
  rows = adult_size
  cols = adult_size
  #
  white  = 0
  red    = 1
  blue   = 2
  #
  fitness    = 0
  #
  true_blue  = 0
  true_red   = 0
  false_blue = 0
  false_red  = 0
  #
  assert (len(adult)     == 60)
  assert (len(adult[0])  == 60)
  assert (len(target)    == 60)
  assert (len(target[0]) == 60)
  #
  for i in range(rows):
    for j in range(cols):
      # - blue on blue = 1 point (blue target + blue adult)
      if ((adult[i, j] == blue) and (target[i, j] == blue)):
        fitness   += 1
        true_blue += 1
      # - red on red = 1 point
      if ((adult[i, j] == red) and (target[i, j] == red)):
        fitness  += 1
        true_red += 1
      # - blue on red = -1 point
      if ((adult[i, j] == blue) and (target[i, j] == red)):
        fitness    -= 1
        false_blue -= 1
      # - red on blue = -1 point
      if ((adult[i, j] == red) and (target[i, j] == blue)):
        fitness   -= 1
        false_red -= 1
      #
  golly.show("fitness = " + str(fitness))
  return [fitness, true_blue, true_red, false_blue, false_red]
#
# The target patterns that the seed should evolve towards.
#
# - target_1(), target_2(), target_3(), target_4(), target_5()
#
def show_target(matrix, adult_size):
  # - make a box of adult_size x adult_size centered on the origin
  # - golly.setcell(x, y, state) -- x is horizontal, y is vertical
  # - matrix[i][j] -- i is rows (vertical), j is cols horizontal
  # - therefore we need to swap i and j, to rotate the image
  # - NOTE: if we divide a 60x60 grid into four quadrants:
  # - the top left quadrant ranges horizontally from -30 to -1
  # - the top right quadrant ranges horizontally from 0 to 29
  # - the top left quadrant ranges vertically from -30 to -1
  # - the bottom left quadrant ranges vertically from 0 to 29
  rows   =  60
  cols   =  60
  left   = -30
  right  = +30 # stops at +29
  top    = -30
  bottom = +30 # stops at +29
  #
  assert adult_size == 60
  #
  height = 60
  width  = 60
  #
  for i in range(height):
    for j in range(width):
      # - for the matrix, i and j range from 0 to 59
      colour = matrix[i, j]
      # - for golly, j and i range from -30 to +29
      golly.setcell(j + top, i + left, colour)
  return
#
# The following targets assume a size of 60 x 60
#
# Target 1
#
# - target_1()
#   four boxes
#   red, blue
#   blue, red
#
def target_1():
  rows = 60
  cols = 60
  matrix_1 = np.zeros([rows, cols], dtype=int)
  for i in range(rows):
    for j in range(cols):
      if (j >= 0) and (j < 30) and (i >= 0) and (i < 30):
        matrix_1[i, j] = red
      if (j >= 0) and (j < 30) and (i >= 30) and (i < 60):
        matrix_1[i, j] = blue
      if (j >= 30) and (j < 60) and (i >= 0) and (i < 30):
        matrix_1[i, j] = blue
      if (j >= 30) and (j < 60) and (i >= 30) and (i < 60):
        matrix_1[i, j] = red
  return matrix_1
#
# Target 2
#
# - target_2()
# - vertical stripes of red and blue
#
def target_2():
  rows = 60
  cols = 60
  matrix_2 = np.zeros([rows, cols], dtype=int)
  for i in range(rows):
    for j in range(cols):
      if (j >= 0) and (j < 30):
        matrix_2[i, j] = red
      if (j >= 30) and (j < 60):
        matrix_2[i, j] = blue
  return matrix_2
#
# Target 3
#
# - target_3()
# - vertical stripes of red, blue, red
#
def target_3():
  rows = 60
  cols = 60
  matrix_3 = np.zeros([rows, cols], dtype=int)
  rows = 60
  cols = 60
  for i in range(rows):
    for j in range(cols):
      if (j >= 0) and (j < 20):
        matrix_3[i, j] = red
      if (j >= 20) and (j < 40):
        matrix_3[i, j] = blue
      if (j >= 40) and (j < 60):
        matrix_3[i, j] = red
  return matrix_3
#
# Target 4
#
# - target_4()
# - vertical stripes of red, blue, red, blue
#
def target_4():
  rows = 60
  cols = 60
  matrix_4 = np.zeros([rows, cols], dtype=int)
  for i in range(rows):
    for j in range(cols):
      if (j >= 0) and (j < 15):
        matrix_4[i, j] = red
      if (j >= 15) and (j < 30):
        matrix_4[i, j] = blue
      if (j >= 30) and (j < 45):
        matrix_4[i, j] = red
      if (j >= 45) and (j < 60):
        matrix_4[i, j] = blue
  return matrix_4
#
# Target 5
#
# - target_5()
#  ##########
#  # r /\ r #
#  #  /  \  #
#  # / b  \ #
#  #/      \#
#  #   /\   #
#  #  /  \  #  - 60 x 60
#  # / r  \ #  - 1 = red, 2 = blue
#  #/      \#
#  ##########
#
def target_5():
  rows = 60
  cols = 60
  matrix_5 = np.zeros([rows, cols], dtype=int)
  # - top left
  for i in range(30):
    for j in range(30):
      if (i >= j):
        matrix_5[i, 29 - j] = blue
      else:
        matrix_5[i, 29 - j] = red
  # - top right
  for i in range(30):
    for j in range(30):
      if (i >= j):
        matrix_5[i, 30 + j] = blue
      else:
        matrix_5[i, 30 + j] = red
  # - bottom left
  for i in range(30):
    for j in range(30):
      if (i > j):
        matrix_5[30 + i, 29 - j] = red
      else:
        matrix_5[30 + i, 29 - j] = blue
  # - bottom right
  for i in range(30):
    for j in range(30):
      if (i > j):
        matrix_5[30 + i, 30 + j] = red
      else:
        matrix_5[30 + i, 30 + j] = blue
  #
  return matrix_5
#
#
# STEPS
# =====
#
# - note that evolvability and selection are defined above, in the section
#   EVOLVABILITY AND SELECTION
#
# - run an experiment
#
# - make a torus
rule_name = "Immigration"     # - use the Immigration rule
max_dimension = ":T60,60"     # - Torus of 60 x 60
golly.autoupdate(True)
golly.new(rule_name)
# - Immigration:T60,60 makes a torus of 60 x 60
# - a torus is finite, which means the live cells should
#   be packed more densely and uniformly, which is good
golly.setrule(rule_name + max_dimension)
# - the population size is fixed at population_size
population = []
# - set the target for determining fitness
# - the fitness of an organism is determined by how well it
#   matches with the given target
# - matching with the target means having a pattern of colours
#   that is similar to the target's pattern of colours
# - set target to one of:
#   target_1(), target_2(), target_3(), target_4(), target_5()
#
##############################################################
target = target_3()
log_file = open("./log_file" + str(run_number) + ".txt", "a+")
log_file.write("\ntarget = target_3()\n\n") # target_3()
log_file.close()
##############################################################
#
# - create generation zero
# - generation zero is random; no selection has been applied yet
# - EVOLVABILITY = the size of the seed matrix (e.g., 20x20 or 40x40)
# - the larger the seed matrix is, the more variety is possible;
#   the more genetic information that is available for the 
#   organisms
# - hypothesis: if the seed is 20x20 the adult will struggle to
#   reach 80x80
# - SELECTION = organisms are tested independently and reproduction
#   is asexual, so selection can only be based on the match with the
#   fitness measure -- matching a target shape
for individual in range(population_size):
  # - randomly sample a small number of seed matrices
  # - sample_size is defined at the top of this file
  sample_set = []
  # - collect sample_size samples and then extract the best sample
  for sample in range(sample_size):
    # - "evolvability" determines the size of the square seed (e.g., 20 or 40)
    seed = make_seed_matrix(prob_red, prob_blue, evolvability)
    # - grow the matrix -- adult_size = 60 = size of the 60x60 matrix
    adult = grow_matrix(seed, num_steps, adult_size)
    # - measure how well the adult matches with the target
    [fitness, true_blue, true_red, false_blue, false_red] = \
      compare(adult, target, adult_size)
    assert fitness == true_blue + true_red + false_blue + false_red
    # - append sample
    sample_set.append([seed, adult, fitness])
  # - sort the list (sample_set) by the third element (fitness)
  sorted_samples = sorted(sample_set, key=lambda tup: tup[2])
  # - best_sample is the last tuple in the list of sorted_samples
  best_sample = sorted_samples[-1]
  # - store the vector [seed, adult, target]
  population.append(best_sample) 
#
#
# - now we let the population evolve
# - with each step, we add a newly born seed and let it grow
#   to adult size
# - then we replace the least fit organism with the new organism
for new_birth in range(max_births):
  # - randomly select two adults from the population
  # - an organism has the form [seed, adult, target]
  position1 = rand.randrange(population_size)
  position2 = rand.randrange(population_size)
  organism1 = population[position1] # [seed, adult, target]
  organism2 = population[position2] # [seed, adult, target]
  fitness1  = organism1[2] # fitness
  fitness2  = organism2[2] # fitness
  seed1     = organism1[0] # seed
  seed2     = organism2[0] # seed
  # - make a copy of the more fit organism and mutate it
  # - then replace the less fit organism with the mutant
  if (fitness1 > fitness2):
    # - fitness1 is better than fitness2, so keep [seed1, adult1, fitness1]
    # - population[position1] = organism1 = [seed1, adult1, fitness1]
    # - fitness2 is worse than fitness1, so replace fitness2 with a
    #   mutated version of fitness1
    seed2 = mutate_and_select_seed(population, sample_size, target, prob_mutation)
    # - grow the new seed
    adult2 = grow_matrix(seed2, num_steps, adult_size)
    # - fitness of the new adult
    [fitness2, true_blue2, true_red2, false_blue2, false_red2] = \
      compare(adult2, target, adult_size)
    assert fitness2 == true_blue2 + true_red2 + false_blue2 + false_red2
    # - place the new individual where the less fit individual was
    population[position2] = [seed2, adult2, fitness2]
  # - otherwise, if (fitness1 < fitness2) then replace the less fit 
  #   organism with the new mutant
  else:
    # - fitness1 is worse than fitness2, so keep [seed2, adult2, fitness2]
    # - population[position2] = organism2 = [seed2, adult2, fitness2]
    # - fitness1 is better than fitness2, so replace fitness2 with a
    #   mutated version of fitness1
    seed1 = mutate_and_select_seed(population, sample_size, target, prob_mutation)
    # - grow the new seed
    adult1 = grow_matrix(seed1, num_steps, adult_size)
    # - fitness of the new adult
    [fitness1, true_blue1, true_red1, false_blue1, false_red1] = \
      compare(adult1, target, adult_size)
    assert fitness1 == true_blue1 + true_red1 + false_blue1 + false_red1
    # - place the new individual where the less fit individual was
    population[position1] = [seed1, adult1, fitness1]
    #
#
#
# - report the best fitness
# - start with the first fitness
log_file = open("./log_file" + str(run_number) + ".txt", "a+")
log_file.write("\n")
best_fitness_so_far = 0
for k in range(population_size):
  [seed, adult, fitness] = population[k]
  [fitness, true_blue, true_red, false_blue, false_red] = \
    compare(adult, target, adult_size)
  if (fitness > best_fitness_so_far):
    best_fitness_so_far = fitness
    best_seed_so_far  = seed
    best_adult_so_far = adult
    log_file.write(str(k) + " fitness "    + str(fitness) + "\n")
    log_file.write(str(k) + " true blue "  + str(true_blue) + "\n")
    log_file.write(str(k) + " true red "   + str(true_red) + "\n")
    log_file.write(str(k) + " false blue " + str(false_blue) + "\n")
    log_file.write(str(k) + " false red "  + str(false_red) + "\n")
    assert fitness == true_blue + true_red + false_blue + false_red
log_file.write("\n")
log_file.close()
#
# - show target (60x60)
# - show evolvability and selection in file name
# - evolvability = evolvability setting = size of the seed = 20 or 40
# - selection = selection pressure = target_1(), ..., target_5()
golly.new("")
show_target(target, adult_size)
golly.setmag(3)
golly.setname("photo_target" + str(run_number))
golly.save("photo_target" + str(run_number) + ".rle", "rle", False)
#
# - show seed (20x20)
# - golly.setcell(x, y, state) -- x is horizontal, y is vertical
# - best_seed_so_far[i][j] -- i is rows (vertical), j is cols horizontal
# - therefore we need to swap i and j, to rotate the image
golly.new("")
rows = evolvability
cols = evolvability
halfway = int(evolvability / 2)                # 20/2 = 10 or 40/2 = 20
for i in range(rows):
  for j in range(cols):
    colour = best_seed_so_far[i][j]
    golly.setcell(j - halfway, i - halfway, colour)
golly.setmag(3)
golly.setname("photo_seed" + str(run_number))
golly.save("photo_seed" + str(run_number) + ".rle", "rle", False)
#
# - show adult (60x60)
# - write top_adult to the screen
golly.new("")
grown_matrix = grow_matrix(best_seed_so_far, num_steps, adult_size)
show_target(grown_matrix, adult_size)
golly.setmag(3)
golly.setname("photo_adult" + str(run_number))
golly.save("photo_adult" + str(run_number) + ".rle", "rle", False)
#
#