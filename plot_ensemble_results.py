#!/usr/bin/env python
import sys,os, time
import numpy as np
import subprocess
import pickle
import model_ELM
from optparse import OptionParser
from sklearn import preprocessing
from sklearn.model_selection import train_test_split, GridSearchCV
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

#Python code used to manage the ensemble simulations 
#  and perform post-processing of model output.

parser = OptionParser()

parser.add_option("--case", dest="case", default="", \
                  help="Case name")
# parser.add_option("--postproc_only", dest="postproc_only", default=False, \
#                   action="store_true")
# parser.add_option("--UQ_only", dest="UQ_only", default=False, \
#                   action="store_true")
(options, args) = parser.parse_args()
#Load case object
myfile=open('pklfiles/'+options.case+'.pkl','rb')
mycase=pickle.load(myfile)

#print(mycase)
print(mycase.output.keys())
print(mycase.output['taxis'])
print(mycase.postproc_vars)
print(mycase.postproc_freq)
print("Parameters:")
print(mycase.samples.transpose().shape)

for var_string in mycase.postproc_vars:
    print("Plot ", var_string)
    if var_string == "SR":
        mycase.plot_ensemble(var_string, plot_param=True)
    else:
        mycase.plot_ensemble(var_string, plot_param=False)