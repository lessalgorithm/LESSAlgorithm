# coding: utf-8

# This is the combination of several scripts that download data from the
# NASA NSRDB database and process.

# The propose of this code it to run experiments around adaptive multitenancy
# driven ENO WSN for an EWSN submission.

import pandas as pd
import time
import math
import simplejson
from NREL import *
import numpy as np
import random
import matplotlib.pyplot as plt
#import matlab.engine
import os
import sys
sys.path.append('energy_prediction')
sys.path.append('eno')
from orchestrator import Orchestrator
from wcewma import WCEWMA
from eno_static import StaticENO
from eno_orchestrator import OrchestratorENO
from eno_less import LESSENO
from eno_kansal import KansalENO

""" Global store of the performance for later graphing """
output_jsons = []  # output file
refSolarPowerVector = [[]]
wcewma_pred_vector = []

# --------------------------------------------------------------------------- #
""" For loading in lighting data for energy harvesting calculation. """

def dfLoad(test):
    df = pd.read_csv('datasets/env_data/{}_solarcalc_raw.csv'.format(test),
                     low_memory=False, index_col=0)  # change file name to loop
    return df


# --------------------------------------------------------------------------- #
""" This sanitizes the input data, there's some strange temperature artifacts
this removes """

def getTemplist(df):
    temperature_list, result = df["Temperature"].tolist(), []
    for item in temperature_list:
        if (type(item) == str) and item.endswith('.1'):
            item = item[:-2]
            result.append(float(item))
        else:
            result.append(float(item))
    return result


# --------------------------------------------------------------------------- #
# This function calls the orchastrator to find system requirements and adds
# them to the dataframe. for now it's a placeholder for the length of the file,
# it'll change to be dynamic


def sysRequirements(df, test, orchest):
    """ This takes the config file dt and multiplies it to be the length of
    the dataframe in multiples of a day """
    
    # print("Shape =>", df.shape[0]/ len(orchest))

    # N = df.shape[0] / len(orchest)
    # df['Orchastration Requirements'] = list(map(lambda x: x*N, orchest))

    df['Orchastration Requirements'] = orchest * int(df.shape[0] / len(orchest))
    return df


# --------------------------------------------------------------------------- #
# This function works out the energy generation of the target test

def panelEnergyGen(df, test):
    DHI_list = df["DHI"].tolist()
    DNI_list = df["DNI"].tolist()
    Zenith_list = df["Solar Zenith Angle"].tolist()
    E_list = [a * (math.cos(math.radians(c))) + b for a, b,
              c in zip(DNI_list, DHI_list, Zenith_list)]
    if debug:
        print(" => E coefficient has been calculated ")

    # reflection coefficients
    rd = (1 + (math.cos(math.radians(sensor_angle_H))) / 2)
    rr = (1 - (math.cos(math.radians(sensor_angle_H))) / 2)

    # Where variable x is DNI*cos(theta)
    x_list = [a * (math.cos(math.radians(sensor_angle_V - b)))
              for a, b in zip(DNI_list, Zenith_list)]

    # energy in w/m2 impinging on the surface of a solar cell
    ES_list = [(a + (b * rd) + (foreground_albedo * c * rr))
               for a, b, c in zip(x_list, DHI_list, E_list)]
    if debug:
        print(" => Energy hitting the cell has been calculated")

    # including temperature as a function of solar cell efficiency in calculations
    temperature_list = getTemplist(df)
    tc_list = [(a + (((Noct - 20) / 800) * b))
               for a, b in zip(temperature_list, ES_list)]
    efficiency_pvg = [((solar_panel_efficiency * power_conditioning_efficiency)
                       * (1 - temperature_coefficient * (a - ref_cell_temp))) for a in tc_list]
    if debug:
        print(" => Efficiency of the solar cell over time has been calculated")

    # conversion from w/m2 to energy generated by solar panel in mA
    EG_list = [(abs(a * (solar_panel_active_area_m2 * b * 1000.00)) / (solar_panel_voltage))
               for a, b in zip(ES_list, efficiency_pvg)]  # change ABS here, can't be right
    df['Energy Solar Gen'] = EG_list
    return df
# function to take in environmental variables and return current consumption

# --------------------------------------------------------------------------- #


def NRELtoWindPower(df):
    energy_type = 3
    if debug:
        print(" => Working out wind parameters")
    pressure_list = df["Pressure"].tolist()
    # Making an assumption that as the system is light it will have a fan to point in the direction of the wind
    wind_speed_list = df["Wind Speed"].tolist()
    temperature_list = getTemplist(df)

    # 100 here convers millibar to pascal and 273.15 is c to kelvin conversion
    air_density_list = [((a * 100) / (R_spec * (b + 273.15)))
                        for a, b in zip(pressure_list, temperature_list)]
    power_e_list = []  # extractable energy by my wind turbine within usable conditions
    for a, b in zip(wind_speed_list, air_density_list):
        if Ve < a and a < Vo:
            temp_power = ((0.5 * b * Area_wind * math.pow(a, 3)
                           * cp) / wind_turbine_voltage)
            power_e_list.append(temp_power)
        else:
            power_e_list.append(0.0)

    df['Energy Wind Gen'] = power_e_list
    if debug:
        print(" => Finished working out wind parameters")
    return df

# sometimes returning negative values, which probably isn't right - need to check DC DC rectifies neg voltages

# --------------------------------------------------------------------------- #


def NRELtoTEGPower(df):
    energy_type = 2
    if debug:
        print(" => Working out TEG parameters")
    temperature_list = getTemplist(df)
    vteg_list = []
    for key in temperature_list:
        temp = abs(key - T_ambient)
        if temp > 5:
            # Check to confirm that the temperature in reverse generates current with neg voltage also and DC/DC can handle that
            vteg_list.append(
                abs(((N_TEG * seedback_coeff) * (key - T_ambient) / 4)))
        else:
            vteg_list.append(0)

    Iout_list = [(gm * (a - vmin)) for a in vteg_list]
    # pout_list = [(ef*a*b) for a,b in zip(Iout_list,vteg_list)] # Original equation here says that Vout, make sure VTEG is Vout in this context
    df['Energy TEG Gen'] = Iout_list
    # PlotNREL(df,location,energy_type)
    if debug:
        print(" => Finished with TEG calculations")
    return df


# --------------------------------------------------------------------------- #
""" This function creates a prediction of current energy generated. This is a
placeholder """


# def createPrediction(df):
#     pred, predoutput, GHI_list, length = [0 for j in range(48)], [], df["GHI"].tolist(
#     ), 1000  # This is updated at end of time window (next time window)
#     for x in range(0, length):
#         for a, b in zip(GHI_list, pred):
#             predoutput.append((b + a) * 0.5)
#         pred, predoutput = predoutput, []
#     df['Prediction'] = pred
#     return df

# --------------------------------------------------------------------------- #
# This function calcualtes the performance of a test


def calcPerf(df, test, name):
    # Calculate metrics for how well system performs
    
    quarter_year_data = len(df['Sense Frequency'].tolist()) // 4

    sens_freq_list = df['Sense Frequency'].tolist()
    print("sens_freq_list before =>", len(sens_freq_list))
    # sens_freq_list = [2] +  sens_freq_list
    print("sens_freq_list after =>", len(sens_freq_list))
    # del sens_freq_list[-1]
    # less_graph.append(2)

    sens_freq_by_quarter_year = [sens_freq_list[i:i+quarter_year_data] 
            for i in range(0, len(sens_freq_list), quarter_year_data)]

    batterylevelflag_list = df['Battery Level Flag'].tolist()
    batterylevelflag_by_quarter_year = [batterylevelflag_list[i:i+quarter_year_data] 
            for i in range(0, len(batterylevelflag_list), quarter_year_data)]
    
    orchastPlace_list = df['Orchastration Requirements'].tolist()
    orchastPlace_by_quarter_year = [orchastPlace_list[i:i+quarter_year_data]
            for i in range(0, len(orchastPlace_list), quarter_year_data)]

    # print("orchastPlace_list size =>", len(orchastPlace_list))
    # print("sens_freq_list =>", len(sens_freq_list))    

    for i in range(0,4):        
        average = round(sum(sens_freq_by_quarter_year[i]) / len(sens_freq_by_quarter_year[i]), 2)  # average sensing rate for ENO

        dead_metric = batterylevelflag_by_quarter_year[i].count(0)
        dead_metric_per = (dead_metric / len(batterylevelflag_by_quarter_year[i])*100)

        waste_metric = batterylevelflag_by_quarter_year[i].count(2)
        waste_metric_per = (waste_metric / len(batterylevelflag_by_quarter_year[i])*100)

        varience = np.var(sens_freq_by_quarter_year[i])

        orchestrator_fullfilment = []
        for sense_freq, orch_reqs in zip(sens_freq_by_quarter_year[i], 
                                         orchastPlace_by_quarter_year[i]):
            if(sense_freq < orch_reqs):
                orchest_met_per = (sense_freq / orch_reqs) * 100
            else:
                orchest_met_per = 100.0

            orchestrator_fullfilment.append(orchest_met_per)

            if name == 'LESS':
                print("sense_freq =>", sense_freq, "orch_reqs =>", orch_reqs, "orchest_met_per =>", orchest_met_per);

        orchestrator_fullfilment_per = (round(sum(orchestrator_fullfilment) / len(orchestrator_fullfilment), 2))

        # Time the orchastrator requirements were met - got to think about how this is represented (especically over provisioning)
        orchas = []
        for a, b in zip(sens_freq_by_quarter_year[i], orchastPlace_by_quarter_year[i]):
            orchas.append(a - b)

        season = {0: 'jan-march', 1: 'april-jun', 2:'jul-sep', 3:'oct-dec'}

        if storage and name != 'orchas':
            output_jsons.append({'source': test, 'test': name, 'season': season[i], 'Dt_average': average, 'variance': varience, 'perTimeDead': dead_metric_per,
                                 'perTimeWasted': waste_metric_per, 'orchFullfilment': orchestrator_fullfilment_per, 'orchas': orchastPlace_list, 'sense_freq': sens_freq_list, 'orchas_diff': orchas})

# Performance here is described as the number of transmissions, time alive, time dead, variance, wasted energy.

# --------------------------------------------------------------------------- #
def dumpData(test):
    if output_jsons:
        epoch_time = int(time.time())
        resultFile = open(
            "datasets/results/{}_{}_solartracking_results.json".format(epoch_time, test), 'w+')
        simplejson.dump(output_jsons, resultFile)
        resultFile.close()


# --------------------------------------------------------------------------- #
def graphData(df):
    tests = ['orchas', 'static', 'LESS', 'eno']
    static_graph, eno_graph, less_graph, orchas_graph, graph = [], [], [], [], []
    # graph.append(min_tx_freq)
    for name in tests:
        for key in output_jsons:
            if key['test'] in "orchas":
                orchas_graph.append(key['sense_freq'])
                # orchas_graph.append(key['orchas'])
            if key['test'] in "eno":
                eno_graph.append(key['sense_freq'])
            if key['test'] in "LESS":
                less_graph.append(key['sense_freq'])            
            if key['test'] in "static":
                static_graph.append(key['sense_freq'])                
                graph.append(key['orchas']) 
    
    print ('\n================================================'
           '=================================================')

    # index=df.index.get_values()
    # plt.plot(orchas_graph[0], c='blue', linewidth=1.5, label='Orchestrator')
    plt.plot(static_graph[0], c='green', linewidth=1.5, label='Static')
    plt.plot(eno_graph[0], c='red', linewidth=1.5, label='ENO')
    # less_graph[0].pop(0)
    # less_graph.append(2)

    plt.plot(less_graph[0], c='orange', linewidth=1.5, label='LESS')
    plt.plot(graph[0], '--', linewidth=1.0, c='violet', label='Target')
    # plt.plot() plot the orchestration requirement as dotted line TD
    legend = plt.legend(loc='upper right', shadow=True)
    plt.xlabel('Time Slot, t', {'color': 'black',
                                'fontsize': 22})
    plt.ylabel('Duty Cycle, D_t', {'color': 'black',
                                   'fontsize': 22})
    plt.grid(True, which='both')
    plt.minorticks_on
    plt.ylim(ymax=35, ymin=0)
    plt.xlim(xmax=700, xmin=0)
    plt.show()
    # Add labelling automatically
    # Change show graph to save graph


# --------------------------------------------------------------------------- #
# Adding function to take care of summing energy sources
def energyGenTotal(df, energy_source):
    if debug:
        print(" => Calculating Total Energy Production")
    solar_list = df["Energy Solar Gen"].tolist()
    wind_list = df["Energy Wind Gen"].tolist()
    teg_list = df["Energy TEG Gen"].tolist()
    currentgen_list = []
    for a, b, c in zip(solar_list, wind_list, teg_list):
        x = 0
        if "s" in energy_source:
            x += (a * (random.uniform(solar_prod_var[0], solar_prod_var[1])))
        if "w" in energy_source:
            x += (b * (random.uniform(wind_prod_var[0], wind_prod_var[1])))
        if "t" in energy_source:
            x += (c * (random.uniform(teg_prod_var[0], teg_prod_var[1])))
        currentgen_list.append(x)
    df['Energy Generation Total'] = currentgen_list
    if debug:
        print(" => Energy level calculated and added to dataframe")
    return df


# --------------------------------------------------------------------------- #
def graphEg(df):
    solar_list = df["Energy Solar Gen"].tolist()
    wind_list = df["Energy Wind Gen"].tolist()
    teg_list = df["Energy TEG Gen"].tolist()
    plt.plot(solar_list, c='blue', linewidth=1.5, label='Solar')
    plt.plot(wind_list, c='green', linewidth=1.5, label='Wind')
    plt.plot(teg_list, c='red', linewidth=1.5, label='TEG')
    # legend = plt.legend(loc='upper right', shadow=True)
    plt.xlabel('Time Slot, t', fontsize='x-large')
    plt.ylabel('Energy Generated (mAh)', fontsize='x-large')
    plt.grid(True, which='both')
    plt.minorticks_on
    plt.ylim(ymax=33, ymin=0)
    plt.xlim(xmax=350, xmin=0)
    plt.show()


# --------------------------------------------------------------------------- #
def plotSolarEgen(df, wvList, wcewma_pred_vector):
    # print(wcewma_pred_vector)
    solar_list = df["Energy Solar Gen"].tolist()
    pre_list = []

    for i in range(len(refSolarPowerVector)):
        for j in range(len(refSolarPowerVector[i])):            
            pre_list.append(refSolarPowerVector[i][j])
    
    plt.figure(1)
    # plt.subplot(211)    
    plt.plot(pre_list, c='red', linewidth=1.5, label='Pre')
    plt.plot(solar_list, c='blue', linewidth=1.5, label='Real Solar Data')
    plt.plot(wcewma_pred_vector, c='green', linewidth=1.5, label='WC-EWMA')
    plt.xlabel('Time Slot, t', fontsize='x-large')
    plt.ylabel('Energy Generated (mAh)', fontsize='x-large')
    # plt.grid(True, which='both')
    plt.minorticks_on
    plt.ylim(ymax=70, ymin=0)
    # plt.xlim(xmax=350, xmin=0)
    plt.xlim(xmax=366, xmin=0)

    # plt.subplot(212)
    # x = np.arange(7)    

    # plt.bar(x, wvList, width=0.4)
    # plt.xlabel('Day, t', fontsize='x-large')
    # plt.ylabel('Weather volatility', fontsize='x-large')        
    # plt.gca().yaxis.grid(True)    
    # plt.minorticks_on
    # plt.ylim(ymax=8, ymin=0)
    # plt.xlim(xmax=6.5, xmin=-0.5)
    plt.show()


# --------------------------------------------------------------------------- #
def plotWeatherVolatility(wvList):
    x = np.arange(7)
    fig, ax = plt.subplots()
    plt.bar(x, wvList)
    plt.ylim(ymax=8, ymin=0)
    plt.xlim(xmax=7, xmin=-1)
    plt.show()

# --------------------------------------------------------------------------- #
# Main
def main(orch_profile, energy_source):
    wcewma = WCEWMA(48);
    eno_static = StaticENO();
    eno_orchestrator = OrchestratorENO();
    eno_kansal = KansalENO();
    eno_less = LESSENO();
    orchest_loop = []
    # orchest_loop.append(orchastLamps)
    # orchest_loop.append(orchastMicro)
    # orchest_loop.append(orchastMulti)
    orchest_loop.append(orch_profile)    
    for orchest in orchest_loop:  
        print("orchest =>", orchest)      
        for dataset in dataset_list:
            # print("dataset =>", dataset)
            # loads environmental variables from location and time defined in NREL.py. If not local it downloads them from the NREL database and parses them for use.
            df = dfLoad(dataset)
            if not df.empty:
                # Currently only works for one loop because of this line but can be fixed later
                if dataset_list.index(dataset) == 0:
                    df = sysRequirements(df, dataset, orchest)
                # Calculates energy generated by solar panel for day
                df = panelEnergyGen(df, dataset)
                # calculated wind power produciton from environmental variables
                df = NRELtoWindPower(df)
                # calculates thermal energy generation from environmental variables
                df = NRELtoTEGPower(df)
                # calculates energy total by summing the above
                if not energy_source:
                    energy_source = energy_combination
                df = energyGenTotal(df, energy_source)
                
                eno_static.staticWSN(df, dataset, initial_battery_capacity_mah)
                calcPerf(df, dataset, 'static')
                if debug:
                    print(" => Calculating the static WSN performance")
                eno_orchestrator.orchasWSN(df, dataset, initial_battery_capacity_mah)
                calcPerf(df, dataset, 'orchas')
                if debug:
                    print(" => Calculating the centrally controlled WSN performance")
                # eno_kansal.enoWSN(df, dataset)

                currentgen_list = df['Energy Generation Total'].tolist()
                # print("currentgen_list =>", currentgen_list)
                # wcewma_pred_vector = wcewma.compute_wcewma_pred_vector(df)
                # print("wcewma_pred_vector =>", wcewma_pred_vector)

                eno_kansal.enoBaseline(df, currentgen_list, initial_battery_capacity_mah)
                calcPerf(df, dataset, 'eno')

                if debug:
                    print(" => Calculating the solely ENO controlled WSN performance")
                eno_less.lessWSN(df, dataset, initial_battery_capacity_mah)
                calcPerf(df, dataset, 'LESS')
                if debug:
                    print(" => Calculating the LESS=MORE WSN performance")
                dumpData(dataset)
                # if debug:
                #     print (output_jsons)

                # wvList = []
                # for i in range(1, 5):
                #     start_slot = (i - 1) * wcewma.slotPerDayCount
                #     end_slot = (i * wcewma.slotPerDayCount) - 1                     
                #     wvList.append(wcewma.weather_volatility_value(df, start_slot, end_slot, 5, 0.8))
                #     print("wv(", i,") = ", wvList[i-1])
                
                # # df, cloudiness_degree_threshold, currentDayIndex, currentDayRefSolarPower, weighting_factor
                
                # for i in range(1, 5):
                #     refSolarPowerVector.insert(i,(wcewma.getNextDayRefSolarPowerVector(df, 3, i, 0.5)))
                
                # wcewma_pred_vector = wcewma.get_wcewma_for_day(df, refSolarPowerVector)
                # print("len(wcewma_pred_vector)", len(wcewma_pred_vector))
                # print(wcewma_pred_vector)
                # plotSolarEgen(df, wvList, wcewma_pred_vector)
                # plotWeatherVolatility(wvList)

                graphData(df)
          
                # tableData(df)
                del output_jsons[:]
                # graphEg(df)


orchestrator = Orchestrator()
dir_path = os.path.dirname(os.path.realpath(__file__))
orch_data_loc = dir_path + '/requirements.txt'
app_req_dict = orchestrator.read_app_reqs(orch_data_loc)

main(orchestrator.parse_reqs(("App1", app_req_dict.get("App1"))), "s")
# profile.run('main()') # Run this if you want timing of each run of the code

# Do I want to use the ICDCS style testing. Robustness to different Nw, different energy sources, different battery sizes etc...
# Different requirements ? ? ? or test for multiple dynamic requirements
# figure out how to include the overhead of transmission for the MORE and LESS algorithms at start of time window
# Do we want to include the conservative (min instead of max) LESS algorithm in discussion - Will
