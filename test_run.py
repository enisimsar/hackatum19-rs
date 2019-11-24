#!/usr/bin/env python
# coding: utf-8




import time
from DUT import DUT
import matplotlib.pyplot as plt
import numpy as np
import json
import sys

import os
import pandas as pd
import random

# In[2]:



f= open("time_course_results.csv","a+")
#f.write("seed,base,count,corr,queue\n")


for seed in np.random.randint(0,2000,50):
    f.write("{}".format(seed))
    ## Baseline Model

    my_dut = DUT(seed, True, 3.2)

    meastime, nmeas, nport, meas, ports, expyield = my_dut.info()
    print("DUT: meas. time= ", meastime, " | measurements= ", nmeas, " | ports= ", nport, " | expected yield = ", expyield)
    error_count = 0
    X = []
    Y = []
    t=0

    data= {}
    data['component']=[]

    meas_fails = []

    for x in range(20000):
        my_dut.new_dut()
        dut={}
        dut['dut_id'] = x
        dut['measurements']=[]

        if x % 500 == 0:
            my_dut.calibrate()

        for i in range(0, nmeas):
            t, result, dist = my_dut.gen_meas_idx(i)
            measurement = {}
            measurement['m_id'] = i
            measurement['m_time'] = meas[i].meas_time
            measurement['m_result'] = dist
            dut['measurements'].append(measurement)
            
            if dist > 1.0: meas_fails.append(i)
                
            if result == False:
                break

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res

        data['component'].append(dut)

        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1

    error_dut, error_meas = my_dut.get_errordutcount()
    print("Total: ",t, "s ", x+1, " ( ", error_count, " | ", error_dut, " | ", error_meas, " ) ==> ", (x+1-error_count)/(x+1) )
    f.write(",{}".format(t))
    
    ## Count Model
    
    my_dut = DUT(seed, True, 3.2)

    n_train = 5000
    n_test = 20000 - n_train

    meastime, nmeas, nport, meas, ports, expyield = my_dut.info()
    print("DUT: meas. time= ", meastime, " | measurements= ", nmeas, " | ports= ", nport, " | expected yield = ", expyield)

    error_count = 0
    X = []
    Y = []
    t=0

    data= {}
    data['component']=[]
    fails = []
    my_err = 0

    for x in range(n_train):
        my_dut.new_dut()
        dut={}
        dut['dut_id'] = x
        dut['measurements']=[]
        
        if x % 500 == 0:
            my_dut.calibrate()
            
        toggle = True

        for i in range(0, nmeas):
            t, result, dist = my_dut.gen_meas_idx(i)
            
            if dist > 1: fails.append(i)
            
            measurement = {}
            measurement['m_id'] = i
            measurement['m_time'] = meas[i].meas_time
            measurement['m_result'] = dist
            dut['measurements'].append(measurement)
                    
            if result == False and toggle:
                toggle = False
                my_err += 1
                break

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res

        data['component'].append(dut)

        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1

    a, c = np.unique(fails, return_counts=True)
    indexes = np.zeros(nmeas)
    if len(a):
        indexes[a] = c
    sorted_meas = np.argsort(-indexes)

    sorted_meas #= sorted_meas # [:-sum(indexes < 1)]

    for x in range(n_test):
        my_dut.new_dut()
        dut={}
        dut['dut_id'] = x
        dut['measurements']=[]

        if x % 500 == 0:
            my_dut.calibrate()
        
        incount = True
        for j, i in enumerate(sorted_meas):
            t, result, dist = my_dut.gen_meas_idx(i, incount)
            measurement = {}
            measurement['m_id'] = i
            measurement['m_time'] = meas[i].meas_time
            measurement['m_result'] = dist
            dut['measurements'].append(measurement)
            
            if result == False or j > nmeas - sum(indexes < 1):
                if result == False and incount:
                    my_err +=1
                incount = False

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res

        data['component'].append(dut)

        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1

    error_dut, error_meas = my_dut.get_errordutcount()
    print("Total: ",t, "s ", x+1, " ( ", error_count, " | ", error_dut, " | ", error_meas, " ) ==> ", (x+1-error_count)/(x+1) )
    f.write(",{}".format(t))
    
    ## Count Correlation Model
    
    my_dut = DUT(seed, True, 3.2)

    n_train = 2500
    n_test = 20000 - n_train * 2

    meastime, nmeas, nport, meas, ports, expyield = my_dut.info()
    print("DUT: meas. time= ", meastime, " | measurements= ", nmeas, " | ports= ", nport, " | expected yield = ", expyield)

    error_count = 0
    X = []
    Y = []
    t=0

    data= {}
    data['component']=[]

    fails = []
    my_err = 0

    for x in range(n_train):
        my_dut.new_dut()
        dut={}
        dut['dut_id'] = x
        dut['measurements']=[]
        
        if x % 500 == 0:
            my_dut.calibrate()
            
        toggle = True

        for i in range(0, nmeas):
            t, result, dist = my_dut.gen_meas_idx(i)
            
            if dist > 1: fails.append(i)
            
            measurement = {}
            measurement['m_id'] = i
            measurement['m_time'] = meas[i].meas_time
            measurement['m_result'] = dist
            dut['measurements'].append(measurement)
                    
            if result == False and toggle:
                toggle = False
                my_err += 1
                break

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res

        data['component'].append(dut)

        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1


    a, c = np.unique(fails, return_counts=True)
    indexes = np.zeros(nmeas)
    indexes[a] = c
    sorted_meas = np.argsort(-indexes)



    import itertools

    all_possible_tuples = {
        (i, j): 0 for i, j in itertools.product(range(nmeas), range(nmeas)) if i != j and list(sorted_meas).index(i) < list(sorted_meas).index(j)
    }


    for x in range(n_train):
        my_dut.new_dut()
        dut={}
        dut['dut_id'] = x
        dut['measurements']=[]
        
        if x % 500 == 0:
            my_dut.calibrate()
        
        failed = np.zeros(nmeas)

        for i in sorted_meas:
            t, result, dist = my_dut.gen_meas_idx(i)
            
            measurement = {}
            measurement['m_id'] = i
            measurement['m_time'] = meas[i].meas_time
            measurement['m_result'] = dist
            dut['measurements'].append(measurement)
                    
            if result == False:
                failed[i] = 1
                my_err += 1
                break

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res
        
        for i, j in all_possible_tuples.keys():
            if failed[i] == 0 and failed[j] == 1:
                all_possible_tuples[(i, j)] += 1

        data['component'].append(dut)

        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1


    sorted_meas = []

    for i, j in sorted(all_possible_tuples, key=all_possible_tuples.get, reverse=True):
        if i not in sorted_meas: sorted_meas.append(i)
        if j not in sorted_meas: sorted_meas.append(j)


    for x in range(n_test):
        my_dut.new_dut()
        dut={}
        dut['dut_id'] = x
        dut['measurements']=[]

        if x % 500 == 0:
            my_dut.calibrate()
        
        incount = True
        for j, i in enumerate(sorted_meas):
            t, result, dist = my_dut.gen_meas_idx(i, incount)
            measurement = {}
            measurement['m_id'] = i
            measurement['m_time'] = meas[i].meas_time
            measurement['m_result'] = dist
            dut['measurements'].append(measurement)
            
            if result == False or j > nmeas - sum(indexes < 1):
                if result == False and incount:
                    my_err +=1
                incount = False

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res

        data['component'].append(dut)

        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1


    error_dut, error_meas = my_dut.get_errordutcount()
    print("Total: ",t, "s ", x+1, " ( ", error_count, " | ", error_dut, " | ", error_meas, " ) ==> ", (x+1-error_count)/(x+1) )
    
    f.write(",{}".format(t))
    
    ## Queue-Cut Model
    my_dut = DUT(seed, True, 3.2)
    expected_TN_rate = 0.02


    print("Defected Measures:", my_dut.defected_meas)
    print("Negative Correlation:", my_dut.neg_corr)


    n_train = 2500
    n_test = 20000 - n_train * 2

    meastime, nmeas, nport, meas, ports, expyield = my_dut.info()
    print("DUT: meas. time= ", meastime, " | measurements= ", nmeas, " | ports= ", nport, " | expected yield = ", expyield)


    error_count = 0
    X = []
    Y = []
    t=0

    data= {}
    data['component']=[]


    fails = []
    my_err = 0


    for x in range(n_train):
        my_dut.new_dut()
        dut={}
        dut['dut_id'] = x
        dut['measurements']=[]
        
        if x % 500 == 0:
            my_dut.calibrate()
            
        toggle = True

        for i in range(0, nmeas):
            t, result, dist = my_dut.gen_meas_idx(i)
            
            if dist > 1: fails.append(i)
            
            measurement = {}
            measurement['m_id'] = i
            measurement['m_time'] = meas[i].meas_time
            measurement['m_result'] = dist
            dut['measurements'].append(measurement)
                    
            if result == False and toggle:
                toggle = False
                my_err += 1
                break

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res

        data['component'].append(dut)

        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1


    a, c = np.unique(fails, return_counts=True)
    indexes = np.zeros(nmeas)
    indexes[a] = c
    sorted_meas = np.argsort(-indexes)



    import itertools

    all_possible_tuples = {
        (i, j): 0 for i, j in itertools.product(range(nmeas), range(nmeas)) if i != j and list(sorted_meas).index(i) < list(sorted_meas).index(j)
    }


    len(all_possible_tuples)


    for x in range(n_train):
        my_dut.new_dut()
        dut={}
        dut['dut_id'] = x
        dut['measurements']=[]
        
        if x % 500 == 0:
            my_dut.calibrate()
        
        failed = np.zeros(nmeas)

        for i in sorted_meas:
            t, result, dist = my_dut.gen_meas_idx(i)
            
            measurement = {}
            measurement['m_id'] = i
            measurement['m_time'] = meas[i].meas_time
            measurement['m_result'] = dist
            dut['measurements'].append(measurement)
                    
            if result == False:
                failed[i] = 1
                my_err += 1
                break

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res
        
        for i, j in all_possible_tuples.keys():
            if failed[i] == 0 and failed[j] == 1:
                all_possible_tuples[(i, j)] += 1

        data['component'].append(dut)

        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1


    sorted_meas = []


    for i, j in sorted(all_possible_tuples, key=all_possible_tuples.get, reverse=True):
        if i not in sorted_meas: sorted_meas.append(i)
        if j not in sorted_meas: sorted_meas.append(j)



    # Ones that got falsely stamped as not defect
    false_positives = 0



    for x in range(n_test):
        my_dut.new_dut()
        dut={}
        dut['dut_id'] = x
        dut['measurements']=[]
        
        if x % 500 == 0:
            my_dut.calibrate()
                    
        queue_cut = 0
        exp_faults = expected_TN_rate  * ( my_err / (x + n_train) )
        for j, i in enumerate(np.flip(sorted_meas)):
            tmp = indexes[i] / float((x + n_train))
            if exp_faults - tmp >= 0:
                exp_faults = exp_faults - tmp
                queue_cut += 1
            else:
                break

        incount = True
        for j, i in enumerate(sorted_meas):
            t, result, dist = my_dut.gen_meas_idx(i, incount)
            measurement = {}
            measurement['m_id'] = i
            measurement['m_time'] = meas[i].meas_time
            measurement['m_result'] = dist
            dut['measurements'].append(measurement)
            if result == False or j >  nmeas - queue_cut:
                if result == False and incount:
                    my_err +=1
                    if my_dut.dut_result == True:
                        false_positives+=1
                incount = False

        t, res, dist = my_dut.get_result()
        dut['dut_result'] = res

        data['component'].append(dut)

        X.append(t)
        Y.append(dist)
        if not res:
            error_count += 1

    error_dut, error_meas = my_dut.get_errordutcount()
    print("Total: ",t, "s ", x+1, " ( ", error_count, " | ", error_dut, " | ", error_meas, " ) ==> ", (x+1-error_count)/(x+1) )
    print(my_err)
    false_negatives = error_dut - (my_err - false_positives )
    print(" Undetected faulty chips: {}\n Falsely labeled healty chips: {}".format(false_negatives, false_positives ))
    f.write(",{}\n".format(t))



f.close()
