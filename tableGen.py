#coding: utf-8

# Script to generate tables for LESS paper

import pandas as pd
import sys, os, io
import time, math
from datetime import date, datetime, timedelta
import csv,simplejson,json
from NREL import * 
import numpy as np
import profile, random
import matplotlib.pyplot as plt

def tableData(json):
	tests = ['orchas','static','LESS','eno']
	static_perf,eno_perf,less_perf,orchas_perf,target_perf = [],[],[],[],[]
	sd,orchd,enod,lessd = [],[],[],[]
	# Order of these variable elemetns are orchas, eno, less, static
	average,dead,variable =[],[],[]
	for key in json:
		if key['test'] in "orchas":
			orchas_perf.append(key['sense_freq'])
			average.append(key['Dt_average'])
			variable.append(round(key['variance'],2))
			orchd.append(key['orchas_diff'])
		if key['test'] in "eno":
			eno_perf.append(key['sense_freq'])			
			average.append(key['Dt_average'])
			variable.append(round(key['variance'],2))
			enod.append(key['orchas_diff'])
		if key['test'] in "LESS":
			less_perf.append(key['sense_freq'])
			average.append(key['Dt_average'])
			variable.append(round(key['variance'],2))
			lessd.append(key['orchas_diff'])
		if key['test'] in "static":
			static_perf.append(key['sense_freq'])
			target_perf.append(key['orchas'])
			average.append(key['Dt_average'])
			variable.append(round(key['variance'],2))
			sd.append(key['orchas_diff'])

	# Use this trick again to keep arrays of floats tidy
	static = [float(i) for i in static_perf[0]]
	less = [float(i) for i in less_perf[0]]
	eno = [float(i) for i in eno_perf[0]]
	orch = [float(i) for i in orchas_perf[0]]
	target = [float(i) for i in target_perf[0]]


	# works out the abosolute number of tasks missed by each method with compared to the target
	sdd= round(sum(item for item in sd[0] if item < 0))
	sdd= round(1- abs(sdd)/sum(target_perf[0]),2)*100
	
	orchdd= round(sum(item for item in orchd[0] if item < 0))
	orchdd= round(1- abs(orchdd)/sum(target_perf[0]),2)*100

	enodd= round(sum(item for item in enod[0] if item < 0))
	enodd= round(1- abs(enodd)/sum(target_perf[0]),2)*100

	lessdd= round(sum(item for item in lessd[0] if item < 0))
	lessdd= round(1- abs(lessdd)/sum(target_perf[0]),2)*100
	
	print "The average Dt static {0},orch {1},ENO {2}, LESS {3}, target {4} ".format(round(sum(static)/len(static),2),round(sum(orch)/len(orch),2),round(sum(eno)/len(eno),2),round(sum(less)/len(less),2),round(sum(target)/len(target),2))
	print "The variability static {0},orch {1}, ENO {2},LESS {3}, target {4}".format(round(np.var(static),2),round(np.var(orch),2),round(np.var(eno),2),round(np.var(less),2),round(np.var(target),2))
	print "time dead static {0}%,orch {1}%, ENO {2}%,LESS {3}%".format(round(static.count(0)/float(len(static))*100,2),round(orch.count(0)/float(len(orch))*100,2),round(eno.count(0)/float(len(eno))*100,2),round(less.count(0)/float(len(less))*100,2))
	print 'the % of target met static {0}%,orch {1}%,ENO {2}%, LESS {3}%'.format(sdd,orchdd,enodd,lessdd)

def loadJSON():
	#FILE_NAME = 'Datasets/test/1505063614_0ATotal_solartracking_results.json' # app2 wind original
	#FILE_NAME = 'Datasets/test/1505068489_0ATotal_solartracking_results.json' # app2 thermal original
	#FILE_NAME = 'Datasets/test/1505068744_0ATotal_solartracking_results.json' # app3 solar 
	#FILE_NAME = 'Datasets/test/1505068738_0ATotal_solartracking_results.json' # app3 wind 
	#FILE_NAME = 'Datasets/test/1505068733_0ATotal_solartracking_results.json' # app3 thermal 


	with open(FILE_NAME) as data_file:    
    		data = json.load(data_file)
	return data

def main():
	json = loadJSON()
	tableData(json)
main()
