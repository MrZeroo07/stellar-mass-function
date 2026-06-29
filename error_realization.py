# Author: Shiva Thanay Pandiri
# Date: 29-06-2026

# This jupyter notebook can be utilized to generate flux error realization files for CIGALE. Realizations are sampled randomly from a truncated
# normal distribution, taking the flux values as the mean and the flux_err values as the standard deviation of the normal. The distribution is 
# truncated to ensure that only positive flux values are sampled. Scipy's truncnorm function is used which requires upper and lower limits of
# truncation in standardized units. The realization files are saved in an ascii-commented_header format as required by CIGALE. This file does not
# contain code to generate realization plots. That code will be written in another file (I haven't written it yet). Please look for it, I'm sure 
# it's there in the future :) Incase its not, DM me... wherever you want. Or, write the code yourself! 

# importing the required dependencies

import numpy as np
from astropy.io import ascii
from astropy.table.table import Table
from scipy.stats import truncnorm

input_filepath = '../Downloads/cigale-v2025.1/cigale-v2025.1/desi_fs_erass_final_0.txt' # replace with your own input file
output_directory = '../Downloads/cigale-v2025.1/cigale-v2025.1/realization_inputs/' # replace with your desired directory to store your realization files

data_table: Table = ascii.read(input_filepath) # creating a Table instance of the input file

Ngal = len(data_table) # Number of rows, i.e, number of galaxies
Ndraws = 50 # Number of times you want to sample from the gaussian distribution

flux_columns = ['flux_g', 'flux_r', 'flux_z', 'wise.W1', 'wise.W2', 'efeds_flux'] # replace the list items with the flux columns of your input file
err_columns = [col+'_err' for col in flux_columns] # defining the corresponding error columns, conveniently using CIGALE's input file convention for flux and flux error columns

flux_realizations = {} # creating an empty dictionary to eventually store realizations for each flux column

for i in range(len(flux_columns)):

    # creating the loc and scale arrays of shape (Ngal, 1) for sampling
    loc = np.asarray(data_table[flux_columns[i]], dtype=float)[:, None]
    scale = np.asarray(data_table[err_columns[i]], dtype=float)[:, None]
    
    # defining the lower and upper limits in standardized units to define the truncated normal distribution
    lower_limit = (0-loc)/scale
    upper_limit = np.inf

    # random sampling from a truncated normal distribution
    realizations = truncnorm.rvs(lower_limit, upper_limit, 
                                 loc=loc, scale=scale, size=(Ngal, Ndraws))
    
    flux_realizations[flux_columns[i]] = realizations # storing the realization of a flux column in the dictionary

# The flux_realizations dictionary now contains realizations as values for each flux column key.
# Realization contains randomly sampled values for each galaxy (row) for each draw (column)


# reading values off the flux_realizations dictionary and creating realization files to use as input files for CIGALE
# CIGALE requires the commented_header version of ascii and the format can be modified to plain ascii incase you're not 
# going to use these realization files for something that doesn't require it.

for draw in range(0, Ndraws):
    realization_table = data_table.copy()
    for column in flux_columns:
        realization_table[column] = flux_realizations[column][:, draw]
    realization_table.write(output_directory+f'desi_fs_erass_final_{draw+1}.txt', format='ascii.commented_header', overwrite=True) # replace with your desired filename