#########################################
# Author: Chenfu Shi
# Email: chenfu.shi@postgrad.manchester.ac.uk


# Function inputs a HiChIP CSR_mat and extracts the peaks. 
# Extracts short range interactions from these peaks, forms a vector. Calls significantly enriched fragments then cleans up and merges peaks together. 
# Returns list of peaks as fragment numbers

#########################################

import scipy
import scipy.sparse
import scipy.stats
import statsmodels.stats.multitest
import math
import numpy
import os
import re
import multiprocessing
import subprocess
import matplotlib.pyplot

def sparse_to_peaks(CSR_mat,frag_index,frag_prop,frag_amount,valid_chroms,chroms_offsets):
    """Wrapper function to call individual funcitons"""

    diagonal = extract_diagonal(CSR_mat,2)

    smoothed_diagonal = numpy.rint(moving_integration(diagonal,5)).astype(int)
    quick_peaks = quick_call(smoothed_diagonal)

    import pickle
    with open("./testdata/peaks_tests.pi" ,"wb") as pickleout:
        pickle.dump([smoothed_diagonal,quick_peaks],pickleout)
    

    




    return diagonal, peaks

def moving_integration (values, window):
    weights = numpy.repeat(1.0, window)
    sma = numpy.convolve(values, weights, 'same')
    return sma
def moving_average (values, window):
    weights = numpy.repeat(1.0, window)/window
    sma = numpy.convolve(values, weights, 'same')
    return sma

def extract_diagonal(CSR_mat,window):
    """extract the diagonal including the sum of the window in all directions. calls moving_integration as well"""
    diagonal = CSR_mat.diagonal()
    if window == 0:
        return diagonal
    for i in range(1,window):
        off_diagonal = CSR_mat.diagonal(i)
        diagonal = [sum(x) for x in zip(diagonal, [0]*i + off_diagonal, off_diagonal + [0]*i)]
    return diagonal

def quick_call(smoothed_diagonal):
    """calls the peaks using a very simple genomic average"""

    average_signal = numpy.mean(smoothed_diagonal)
    quick_p_vals=[]
    poisson_pre_pvals = [scipy.stats.poisson.sf(x, average_signal) + scipy.stats.poisson.pmf(x, average_signal) for x in range(numpy.max(smoothed_diagonal)+1)]

    for res_site in smoothed_diagonal.tolist(): 
        quick_p_vals.append(poisson_pre_pvals[res_site])
    
    quick_peaks, correct_q_vals = statsmodels.stats.multitest.fdrcorrection(quick_p_vals, alpha = 0.01)

    return quick_peaks



def refined_call(smoothed_diagonal, quick_peaks, frag_prop, smoothing=5):


    return refined_peaks











if __name__=="__main__":
    """test functions here"""
    import pickle
    CSR_mat = scipy.sparse.load_npz('./testdata/sparse_matrix_mumbach_non_reassigned_chr1.npz')
    with open("./testdata/variables.pi","rb") as picklefile:
        frag_index,frag_prop,frag_amount,valid_chroms,chroms_offsets = pickle.load(picklefile)

    sparse_to_peaks(CSR_mat,frag_index,frag_prop,frag_amount,valid_chroms,chroms_offsets)

