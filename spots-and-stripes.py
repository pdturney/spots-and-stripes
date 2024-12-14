#
#
# Peter Turney, December 2, 2024
#
# spots-and-stripes.py
#
# Evolving Spots and Stripes in the Game of Life
#
# https://en.wikipedia.org/wiki/Patterns_in_nature
#
#
# NOTE: this Python program is intended to run inside Golly.
# It will not run properly outside of Golly.
# https://golly.sourceforge.io/
#
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
# Golly          = https://golly.sourceforge.io/
#
# T60,60         = Make a toroid of 60 x 60
#
# Life-like CA   = https://conwaylife.com/wiki/List_of_Life-like_rules
#                  https://catagolue.hatsya.com/rules/lifelike
#
# B3/S23         = Game of Life
# B36/S23        = https://conwaylife.com/wiki/OCA:HighLife
# B3678/S23      = https://conwaylife.com/wiki/OCA:B3678/S23
# B3/S1237       = https://conwaylife.com/wiki/OCA:SnowLife
# B3/S45678      = https://conwaylife.com/wiki/OCA:Coral
# B35678/S34567  = patterns explode while "cheerios" form in the chaotic mess
#
rule_name        = "B3/S45678:T60,60"
target_number    = 1          # assign target_1, target_2, ..., or target_5
population_size  = 1000       # each new birth requires one death: static population
sample_size      = 40         # a sample of the population
max_births       = 1000000    # run ends after this many births
num_steps        = 100        # number of steps for the Game of Life
prob_black       = 0.5        # probability of black
prob_white       = 0.5        # probability of white
prob_mutation    = 0.1        # probability of switching among white and black
prob_selection   = 0.6        # probability of adding a fit seed and dropping unfit
seed_size        = 30         # 30x30 grid
adult_size       = 60         # 60x60 grid
#
# - record the settings
log_file = open("./log_file" + str(target_number) + ".txt", "a+")
log_file.write("\n" + \
  "rule_name        = " + str(rule_name)       + "\n" + \
  "target number    = " + str(target_number)   + "\n" + \
  "population_size  = " + str(population_size) + "\n" + \
  "sample_size      = " + str(sample_size)     + "\n" + \
  "max_births       = " + str(max_births)      + "\n" + \
  "num_steps        = " + str(num_steps)       + "\n" + \
  "prob_white       = " + str(prob_white)      + "\n" + \
  "prob_black       = " + str(prob_black)      + "\n" + \
  "prob_mutation    = " + str(prob_mutation)   + "\n" + \
  "prob_selection   = " + str(prob_selection)  + "\n" + \
  "seed_size        = " + str(seed_size)       + "\n" + \
  "adult_size       = " + str(adult_size)      + "\n")
log_file.close()
#
#
# COLOURS
# =======
#
# We use the Game of Life rule, which includes two colours.
#
white = 0
black = 1
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
# SEED SIZE
# =========
#
# Genome size = 10x10, 20x20, 30x30, 40x40
#
# - genome is a square grid, so we can use a single number
#   to specify the grid (10x10 --> 10)
# - evolvability specifies size of square gene
# - square gene should be placed in middle of 60x60 matrix
#
#
#
# FUNCTIONS
# =========
#
# Make a random seed matrix.
#
def make_seed_matrix(prob_white, prob_black, seed_size):
  # - seed_size setting = size of the seed = 20 or 40
  # - 20 -> 20x20
  # - 40 -> 40x40
  # - seed_matrix size = 20 rows x 20 columns
  # - the Game of Life seems to prefer a density of
  #   about 0.3, so suggested probability setting is
  #   0.15 for prob_white and 0.15 for prob_black
  # - rows and cols will be shifted by <-10, -10> so
  #   that the matrix is centered on the screen
  # - upper left  = <-10, -10>
  # - lower right = <+10, +10>
  # - start with a matrix of zeros
  seed_matrix = np.zeros([seed_size, seed_size], dtype=int)
  # - each colour is assigned an ID number
  white = 0
  black = 1
  # - fill in the matrix
  for i in range(seed_size):
    for j in range(seed_size):
      # - 0 = loss, 1 = win
      # - assume loss for both white and black
      white_state = 0
      black_state = 0
      # - flip a biased coin for white
      if (rand.random() < prob_white):
        white_state = 1
      # - flip a biased coin for black
      if (rand.random() < prob_black):
        black_state = 1
      # - what if there is a tie between white and black?
      if ((white_state == 1) and (black_state == 1)):
        # - it's a tie, so flip a coin
        if (rand.random() < 0.5):
          white_state = 0
          black_state = 1
        else:
          white_state = 1
          black_state = 0
      # - we've broken the tie
      if (white_state == 1):
        # - white == 1
        seed_matrix[i, j] = white
      if (black_state == 1):
        # - black == 0
        seed_matrix[i, j] = black
      # - if neither white nor black was selected, then 
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
  golly.new(rule_name)            # initialize cells
  golly.setrule(rule_name)        # infinite plane
  golly.autoupdate(True)          # update screen
  # - colours
  white  = 0 # white,255,255,255
  black  = 1 # black,0,0,0
  golly.setcolors([white,255,255,255,black,0,0,0])
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
# Given a seed matrix, swap some of the colours (white, black).
# This is a simple random mutation of the seed.
#
def mutate_seed(seed_matrix, prob_mutation):
  # - each colour is assigned an ID number
  white  = 0
  black  = 1
  # - get seed_matrix size
  rows = len(seed_matrix)
  cols = len(seed_matrix[0])
  new_matrix = np.zeros([rows, cols], dtype=int)
  for i in range(rows):
    for j in range(cols):
      # - change some cells
      if (rand.random() < prob_mutation):
        # - if currently white, then switch to black
        if (seed_matrix[i][j] == white):
          if (rand.random() < 0.5):
            new_matrix[i][j] = black
        # - if currently black, then switch to white
        else:
          if (rand.random() < 0.5):
            new_matrix[i][j] = white
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
  white = 0 # as a colour here, white is represented as 0
  black = 1 # as a colour here, black is represented as 1
  #
  assert (len(adult)     == 60)
  assert (len(adult[0])  == 60)
  assert (len(target)    == 60)
  assert (len(target[0]) == 60)
  #
  # - compare the adult matrix and the target matrix
  # - for each square in the adult matrix, we look for the
  #   corresponding square in the target matrix
  # - let black-on-black be the total number of cases where the 
  #   adult matrix has a black square and the target matrix also 
  #   has a black square in the corresponding position
  # - let black-on-white be the total number of cases where the 
  #   adult matrix has a black square but the target matrix 
  #   has a white square in the corresponding position
  #
  black_on_black = 0
  black_on_white = 0
  #
  for i in range(rows):
    for j in range(cols):
      # - increment black_on_black
      if ((adult[i, j] == black) and (target[i, j] == black)):
        black_on_black += 1
      # - increment black_on_white
      if ((adult[i, j] == black) and (target[i, j] == white)):
        black_on_white += 1
      #
  #
  # - the larger that black_on_black is and the smaller that
  #   black_on_white is, the greater the fitness
  # - the offset is designed to slow down the convergence of
  #   the growth, so that it does not converge to a suboptimal
  #   result
  #
  return [black_on_black, black_on_white]
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
#   black, white
#   white, black
#
def target_1():
  rows = 60
  cols = 60
  matrix_1 = np.zeros([rows, cols], dtype=int)
  for i in range(rows):
    for j in range(cols):
      if (j >= 0) and (j < 30) and (i >= 0) and (i < 30):
        matrix_1[i, j] = black
      if (j >= 0) and (j < 30) and (i >= 30) and (i < 60):
        matrix_1[i, j] = white
      if (j >= 30) and (j < 60) and (i >= 0) and (i < 30):
        matrix_1[i, j] = white
      if (j >= 30) and (j < 60) and (i >= 30) and (i < 60):
        matrix_1[i, j] = black
  return matrix_1
#
# Target 2
#
# - target_2()
# - vertical stripes of black and white
#
def target_2():
  rows = 60
  cols = 60
  matrix_2 = np.zeros([rows, cols], dtype=int)
  for i in range(rows):
    for j in range(cols):
      if (j >= 0) and (j < 30):
        matrix_2[i, j] = black
      if (j >= 30) and (j < 60):
        matrix_2[i, j] = white
  return matrix_2
#
# Target 3
#
# - target_3()
# - vertical stripes of white, black, white
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
        matrix_3[i, j] = white
      if (j >= 20) and (j < 40):
        matrix_3[i, j] = black
      if (j >= 40) and (j < 60):
        matrix_3[i, j] = white
  return matrix_3
#
# Target 4
#
# - target_4()
# - vertical stripes of white, black, white, black, white
#
def target_4():
  rows = 60
  cols = 60
  matrix_4 = np.zeros([rows, cols], dtype=int)
  for i in range(rows):
    for j in range(cols):
      if (j >= 0) and (j < 10):   # 10 white
        matrix_4[i, j] = white
      if (j >= 10) and (j < 25):  # 15 black
        matrix_4[i, j] = black
      if (j >= 25) and (j < 35):  # 10 white
        matrix_4[i, j] = white
      if (j >= 35) and (j < 50):  # 15 black
        matrix_4[i, j] = black
      if (j >= 50) and (j < 60):  # 10 white
        matrix_4[i, j] = white
  return matrix_4
#
# Target 5
#
# - target_5()
#  ##########
#  # w /\ w #
#  #  /  \  #
#  # / b  \ #
#  #/      \#
#  #   /\   #
#  #  /  \  #  - 60 x 60
#  # / w  \ #  - 1 = black, 0 = white
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
        matrix_5[i, 29 - j] = black
      else:
        matrix_5[i, 29 - j] = white
  # - top right
  for i in range(30):
    for j in range(30):
      if (i >= j):
        matrix_5[i, 30 + j] = black
      else:
        matrix_5[i, 30 + j] = white
  # - bottom left
  for i in range(30):
    for j in range(30):
      if (i > j):
        matrix_5[30 + i, 29 - j] = white
      else:
        matrix_5[30 + i, 29 - j] = black
  # - bottom right
  for i in range(30):
    for j in range(30):
      if (i > j):
        matrix_5[30 + i, 30 + j] = white
      else:
        matrix_5[30 + i, 30 + j] = black
  #
  return matrix_5
#
#
# STEPS
# =====
#
# - run an experiment
#
# - make a torus
golly.autoupdate(True)
golly.new(rule_name)
# - a torus is finite, which means the live cells should
#   be packed more densely and uniformly, which is good
golly.setrule(rule_name)
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
if (target_number == 1):
  target = target_1()
  target_name = "target_1()"
if (target_number == 2):
  target = target_2()
  target_name = "target_2()"
if (target_number == 3):
  target = target_3()
  target_name = "target_3()"
if (target_number == 4):
  target = target_4()
  target_name = "target_4()"
if (target_number == 5):
  target = target_5()
  target_name = "target_5()"
log_file = open("./log_file" + str(target_number) + ".txt", "a+")
log_file.write("\ntarget = " + str(target_name) + "\n\n")
log_file.close()
##############################################################
#
# - create generation zero
# - generation zero is random; no selection has been applied yet
# - seed_size = the size of the seed matrix (e.g., 20x20 or 40x40)
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
    # - "seed_size" determines the size of the square seed (e.g., 20 or 40)
    seed = make_seed_matrix(prob_black, prob_white, seed_size)
    # - grow the matrix -- adult_size = 60 = size of the 60x60 matrix
    adult = grow_matrix(seed, num_steps, adult_size)
    # - measure how well the adult matches with the target
    [black_on_black, black_on_white] = compare(adult, target, adult_size)
    fitness = black_on_black - black_on_white
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
    [black_on_black2, black_on_white2] = compare(adult2, target, adult_size)
    fitness2 = black_on_black2 - black_on_white2
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
    [black_on_black1, black_on_white1] = compare(adult1, target, adult_size)
    fitness1 = black_on_black1 - black_on_white1
    # - place the new individual where the less fit individual was
    population[position1] = [seed1, adult1, fitness1]
    #
#
#
# - report the best fitness
# - start with the first fitness
log_file = open("./log_file" + str(target_number) + ".txt", "a+")
log_file.write("\n")
best_fitness_so_far = 0
for k in range(population_size):
  [seed, adult, fitness] = population[k]
  [black_on_black, black_on_white] = compare(adult, target, adult_size)
  fitness = black_on_black - black_on_white
  if (fitness > best_fitness_so_far):
    best_fitness_so_far = fitness
    best_seed_so_far  = seed
    best_adult_so_far = adult
    log_file.write(str(k) + " fitness " + str(fitness) + "\n")
    log_file.write(str(k) + " black_on_black " + str(black_on_black) + "\n")
    log_file.write(str(k) + " black_on_white " + str(black_on_white) + "\n")
log_file.write("\n")
log_file.close()
#
# - NOTE: to view the photos below, you must run Golly. All of the
#   files of the form "photo_target.rle", "photo_seed.rle", and
#   "photo_adult.rle" are run-length encoded (RLE) files, designed to
#   to display photos inside Golly.
#
# - show target (60x60)
# - show seed_size and selection in file name
# - seed_size = size of the seed = 20 or 40
# - selection = selection pressure = target_1(), ..., target_5()
golly.new("")
show_target(target, adult_size)
golly.setmag(3)
golly.setname("photo_target" + str(target_number))
golly.save("photo_target" + str(target_number) + ".rle", "rle", False)
#
# - show seed (20x20)
# - golly.setcell(x, y, state) -- x is horizontal, y is vertical
# - best_seed_so_far[i][j] -- i is rows (vertical), j is cols horizontal
# - therefore we need to swap i and j, to rotate the image
golly.new("")
rows = seed_size
cols = seed_size
halfway = int(seed_size / 2)                # 20/2 = 10 or 40/2 = 20
for i in range(rows):
  for j in range(cols):
    colour = best_seed_so_far[i][j]
    golly.setcell(j - halfway, i - halfway, colour)
golly.setmag(3)
golly.setname("photo_seed" + str(target_number))
golly.save("photo_seed" + str(target_number) + ".rle", "rle", False)
#
# - show adult (60x60)
# - write top_adult to the screen
golly.new("")
grown_matrix = grow_matrix(best_seed_so_far, num_steps, adult_size)
show_target(grown_matrix, adult_size)
golly.setmag(3)
golly.setname("photo_adult" + str(target_number))
golly.save("photo_adult" + str(target_number) + ".rle", "rle", False)
#
#
#