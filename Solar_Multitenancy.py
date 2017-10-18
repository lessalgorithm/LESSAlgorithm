# coding: utf-8

# This is the combination of several scripts that download data from the
# NASA NSRDB database and process.

# This code is adapted from original code written for the longevity ICDCS
# paper and subsequent GLOBECOM paper based on solar tracking.

# The propose of this code it to run experiments around adaptive multitenancy
# driven ENO WSN for an E-WSN submission.

# Original Code Greg Jackson 19/05/2016 AESE Labs Imperial College. gr3gario
# on twitter and gregario on github.

# Tracking Paper Code Greg Jackson 6/03/2017 AESE Labs Imperial College.
# gr3gario on twitter and gregario on github.

# Multitenancy paper code Greg Jackson and Milan Kabac, 28/08/2017.

import pandas as pd
import time
import math
import simplejson
from NREL import *
import numpy as np
import random
import matplotlib.pyplot as plt

""" Global store of the performance for later graphing """
output_jsons = []  # output file

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
    df['Orchastration Requirements'] = orchest * (df.shape[0] / len(orchest))
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
        print 'E coefficient has been calculated'

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
        print 'Energy hitting the cell has been calculated'

    # including temperature as a function of solar cell efficiency in calculations
    temperature_list = getTemplist(df)
    tc_list = [(a + (((Noct - 20) / 800) * b))
               for a, b in zip(temperature_list, ES_list)]
    efficiency_pvg = [((solar_panel_efficiency * power_conditioning_efficiency)
                       * (1 - temperature_coefficient * (a - ref_cell_temp))) for a in tc_list]
    if debug:
        print 'Efficiency of the solar cell over time has been calculated'

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
        print "working out wind parameters"
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
        print "Finished working out wind parameters"
    return df

# sometimes returning negative values, which probably isn't right - need to check DC DC rectifies neg voltages

# --------------------------------------------------------------------------- #


def NRELtoTEGPower(df):
    energy_type = 2
    if debug:
        print "Working out TEG parameters"
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
        print "finished with TEG calculations"
    return df


# --------------------------------------------------------------------------- #
""" This function creates a prediction of current energy generated. This is a
placeholder """


def createPrediction(df):
    pred, predoutput, GHI_list, length = [0 for j in range(48)], [], df["GHI"].tolist(
    ), 1000  # This is updated at end of time window (next time window)
    for x in range(0, length):
        for a, b in zip(GHI_list, pred):
            predoutput.append((b + a) * 0.5)
        pred, predoutput = predoutput, []
    df['Prediction'] = pred
    return df


# --------------------------------------------------------------------------- #
# This function calcualtes the performance of a test


def calcPerf(df, test, name):
    # Calculate metrics for how well system performs
    sens_freq_list = df['Sense Frequency'].tolist()
    batterylevelflag_list = df['Battery Level Flag'].tolist()
    orchastPlace_list = df['Orchastration Requirements'].tolist()

    average = round(sum(sens_freq_list) / len(sens_freq_list),
                    2)  # average sensing rate for ENO

    dead_metric = batterylevelflag_list.count(0)
    dead_metric_per = (dead_metric / len(batterylevelflag_list))

    waste_metric = batterylevelflag_list.count(2)
    waste_metric_per = (waste_metric / len(batterylevelflag_list))

    varience = np.var(sens_freq_list)

    # Time the orchastrator requirements were met - got to think about how this is represented (especically over provisioning)
    orchas = []
    for a, b in zip(sens_freq_list, orchastPlace_list):
        orchas.append(a - b)

    if storage:
        output_jsons.append({'source': test, 'test': name, 'Dt_average': average, 'variance': varience, 'perTimeDead': dead_metric_per,
                             'perTimeWasted': waste_metric_per, 'orchas': orchastPlace_list, 'sense_freq': sens_freq_list, 'orchas_diff': orchas})

# Performance here is described as the number of transmissions, time alive, time dead, variance, wasted energy.


# --------------------------------------------------------------------------- #
""" This function calculates the consumption of a WSN where each sensor always
performs at it's maximum duty cycle. """


def staticWSN(df, test):
    if debug:
        print "working out static current consumption bits"
    # Load arbitrary list to iterate about. This will change to input variables when ENO in introduced
    DHI_list = df["DHI"].tolist()
    Icons_list = [((((Iq + ((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * sens_freq)) * (random.uniform(energy_cons_var[0],
                                                                                                                                 energy_cons_var[1]))) for a in DHI_list]  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted
    currentgen_list = df['Energy Generation Total'].tolist()
    #  This is a simple flag to show when battery is full (2),  battery is empty/system dead (0) or nominally operating (1)
    batterylevelflag_list = [2]
    # This records surplus energy generation that otherwise wouldn't be used when there is no ENO utility stuff
    energygensurplus_list = [0]
    # This list records times of where energy consumption is greater than generation. This is then used to derive battery health
    energydeficit_list = [0]
    sens_freq_list = [sens_freq]
    # This list contains the battery level of the system over the source of the system . Assumes state zero is full battery
    batterylevel_list = [initial_battery_capacity_mah]
    # current battery level. Makes assumption that system starts full
    prev = initial_battery_capacity_mah
    for a, b in zip(Icons_list[1:], currentgen_list[1:]):
        x = prev + ((b - a) / 2)
        if x > initial_battery_capacity_mah:  # if there is a surplus energy and battery is full
            # this is the energy wasted in mAh
            energygensurplus_list.append(x - initial_battery_capacity_mah)
            # this appends zero to the deficit list as we have not wasted energy
            energydeficit_list.append(0)
            # appends a 2 to the level flag list
            batterylevelflag_list.append(2)
            # records the battery level for final calculations
            batterylevel_list.append(initial_battery_capacity_mah)
            prev = initial_battery_capacity_mah
            sens_freq_list.append(sens_freq)  # Think about where to put this
        elif x < 0:  # This takes care of when battery is empty. Doesn't report negative storage
            batterylevel_list.append(0)
            batterylevelflag_list.append(0)
            energygensurplus_list.append(0)
            energydeficit_list.append(x - prev)
            prev = 0
            sens_freq_list.append(0)

        else:  # Normal operating for system, to calc new battery level
            batterylevel_list.append(x)
            batterylevelflag_list.append(1)
            energygensurplus_list.append(0)
            energydeficit_list.append(0)
            prev = x
            sens_freq_list.append(sens_freq)

    # pass these metrics to a list so that the calcPerf can use them later
    df['Energy Consumption'] = Icons_list
    df['Battery Level'] = batterylevel_list
    df['Battery Level Flag'] = batterylevelflag_list
    df['Energy Surplus List'] = energygensurplus_list
    df['Energy Deficit List'] = energydeficit_list
    df['Sense Frequency'] = sens_freq_list
    calcPerf(df, test, 'static')
    if debug:
        print 'Static Current consumption calculated'


# --------------------------------------------------------------------------- #
""" This function calculates the energy consumption of the WSN if only
controlled by the MORE algorithm. """


def orchasWSN(df, test):
    if debug:
        print "working out MORE current consumption bits"
    orchastPlace_list = df['Orchastration Requirements'].tolist()
    Icons_list = [((((Iq + ((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * a)) * (random.uniform(energy_cons_var[0], energy_cons_var[1])))
                  for a in orchastPlace_list]  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted
    # batteryLevel(df,test,Icons_list,'orchas')
    currentgen_list = df['Energy Generation Total'].tolist()
    #  This is a simple flag to show when battery is full (2),  battery is empty/system dead (0) or nominally operating (1)
    batterylevelflag_list = [2]
    # This records surplus energy generation that otherwise wouldn't be used when there is no ENO utility stuff
    energygensurplus_list = [0]
    # This list records times of where energy consumption is greater than generation. This is then used to derive battery health
    energydeficit_list = [0]
    sens_freq_list = []
    sens_freq_list.append(orchastPlace_list[0])
    # This list contains the battery level of the system over the source of the system . Assumes state zero is full battery
    batterylevel_list = [initial_battery_capacity_mah]
    # current battery level. Makes assumption that system starts full
    prev = initial_battery_capacity_mah
    for a, b, c in zip(Icons_list[1:], currentgen_list[1:], orchastPlace_list[1:]):
        x = prev + ((b - a) / 2)
        if x > initial_battery_capacity_mah:  # if there is a surplus energy and battery is full
            # this is the energy wasted in mAh
            energygensurplus_list.append(x - initial_battery_capacity_mah)
            # this appends zero to the deficit list as we have not wasted energy
            energydeficit_list.append(0)
            # appends a 2 to the level flag list
            batterylevelflag_list.append(2)
            # records the battery level for final calculations
            batterylevel_list.append(initial_battery_capacity_mah)
            prev = initial_battery_capacity_mah
            sens_freq_list.append(c)  # Think about where to put this
        elif x < 0:  # This takes care of when battery is empty. Doesn't report negative storage
            batterylevel_list.append(0)
            batterylevelflag_list.append(0)
            energygensurplus_list.append(0)
            energydeficit_list.append(x - prev)
            prev = 0
            sens_freq_list.append(0)

        else:  # Normal operating for system, to calc new battery level
            batterylevel_list.append(x)
            batterylevelflag_list.append(1)
            energygensurplus_list.append(0)
            energydeficit_list.append(0)
            prev = x
            sens_freq_list.append(c)

    # pass these metrics to a list so that the calcPerf can use them later
    df['Energy Consumption'] = Icons_list
    df['Battery Level'] = batterylevel_list
    df['Battery Level Flag'] = batterylevelflag_list
    df['Energy Surplus List'] = energygensurplus_list
    df['Energy Deficit List'] = energydeficit_list
    df['Sense Frequency'] = sens_freq_list
    calcPerf(df, test, 'orchas')
    if debug:
        print 'orchastration Current consumption calculated'


# --------------------------------------------------------------------------- #
""" This function calculates energy consumption if the system only relies on the
LESS algorithm (without taking into account the MORE aspect)"""


def enoWSN(df, test):
    if debug:
        print "working out ENO current consumption bits"

    Eg_Nwi2 = [0.1] * Nw
    Eg_Nwi = [0.1] * Nw
    duty_Nw = []
    # This defines the duty cycle starting point for any window size Nw (following Kansal method)
    for key in range(0, Nw):
        if key <= round((0.333 * Nw), 0):
            duty_Nw.append(min_tx_freq)
        elif key > round((0.333 * Nw), 0) and key <= round((0.666 * Nw)):
            duty_Nw.append(max_tx_freq)
        elif key > round((0.666 * Nw)):
            duty_Nw.append(min_tx_freq)
        else:
            pass

    # Change this to EG_total
    currentgen_list = df['Energy Generation Total'].tolist()
    # This list contains the battery level of the system over the source of the system . Assumes state zero is full battery
    batterylevel_list = [initial_battery_capacity_mah]
    #  This is a simple flag to show when battery is full (2),  battery is empty/system dead (0) or nominally operating (1)
    batterylevelflag_list = [2]
    # This records surplus energy generation that otherwise wouldn't be used when there is no ENO utility stuff
    energygensurplus_list = [0]
    # This list records times of where energy consumption is greater than generation. This is then used to derive battery health
    energydeficit_list = [0]
    Icons_list = [0]
    sens_freq_list = []
    sens_freq_list.append(duty_Nw[0])
    # current battery level. Makes assumption that system starts full
    prev = initial_battery_capacity_mah
    sanity = []
    loop = 0

    # Variables for EWMA filter
    for a in currentgen_list[1:]:
        sens_freq = duty_Nw[loop]

        Icons = ((Iq + ((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * sens_freq)) * (random.uniform(
            energy_cons_var[0], energy_cons_var[1])))  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted
        Icons_list.append(Icons)
        x = prev + (((a) - Icons) / 2)
        if x > prev:  # This if takes care of the times when battery is full so we don't report greater than 100% storage
            batterylevel_list.append(prev)
            batterylevelflag_list.append(2)
            y = x - prev
            energygensurplus_list.append(y)
            energydeficit_list.append(0)
            sens_freq_list.append(sens_freq)

        elif x < 0:  # This takes care of when battery is empty. Doesn't report negative storage
            batterylevel_list.append(0)
            batterylevelflag_list.append(0)
            energygensurplus_list.append(0)
            temp = x - prev
            energydeficit_list.append(temp)
            prev = 0
            sens_freq_list.append(0)

        else:  # Normal operating for system, to calc new battery level
            batterylevel_list.append(x)
            batterylevelflag_list.append(1)
            energygensurplus_list.append(0)
            prev = x
            sens_freq_list.append(sens_freq)

        Eg_Nwi[loop] = round(Eg_Nwi[loop], 2)
        Eg_Nwi[loop] = a

        # Sensing frequency considerations
        cost_per_tx = ((((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * 1))
                       * (random.uniform(energy_cons_var[0], energy_cons_var[1])))
        residual_energy = (Eg_Nwi[loop] - Iq) - (duty_Nw[loop] * cost_per_tx)

        # There is more energy generated than used in the timeslot
        if loop == Nw:
            pass
        else:
            if residual_energy >= cost_per_tx:
                duty_temp = duty_Nw
                index_min = np.argmin(duty_temp)
                no_trans = round(residual_energy / cost_per_tx)
                change_duty = duty_Nw[index_min] + no_trans
                if change_duty > max_tx_freq:
                    duty_change = max_tx_freq - duty_Nw[index_min]
                    duty_Nw[index_min] = max_tx_freq
                    duty_temp = duty_Nw
                    change_duty = no_trans - duty_change
                    index_min = np.argmin(duty_temp)
                    if change_duty > max_tx_freq:
                        duty_Nw[index_min] = max_tx_freq
                    else:
                        duty_Nw[index_min] = change_duty
                else:
                    duty_Nw[index_min] = change_duty

            # There is a deficit in energy greater than the energy needed to send a transmission
            if residual_energy < 0 and abs(residual_energy) > cost_per_tx:
                duty_temp = duty_Nw
                index_max = np.argmax(duty_temp)
                no_trans = abs(round(residual_energy / cost_per_tx))
                change_duty = duty_Nw[index_max] - no_trans
                if change_duty < min_tx_freq:
                    duty_change = abs(min_tx_freq - duty_Nw[index_max])
                    duty_Nw[index_max] = min_tx_freq
                    duty_temp = duty_Nw
                    index_max = np.argmax(duty_temp)
                    change_duty = no_trans - duty_change
                    if change_duty < min_tx_freq:
                        duty_Nw[index_max] = min_tx_freq
                    else:
                        duty_Nw[index_max] = change_duty

                else:
                    duty_Nw[index_max] = change_duty
            else:
                pass

        loop += 1
        if loop > Nw - 1:
            # This checks the number of transmissions over or under utilised + is surplus energy, negative is energy defecit
            sanity_check = round(
                ((sum(Eg_Nwi)) - (sum(duty_Nw) * cost_per_tx)), 1)
            sanity.append(sanity_check)
            loop = 0

    df['Battery Level'] = batterylevel_list
    df['Battery Level Flag'] = batterylevelflag_list
    #df['Energy Surplus List'] = energygensurplus_list
    #df['Energy Deficit List'] = energydeficit_list
    df['Energy Consumption'] = Icons_list
    df['Sense Frequency'] = sens_freq_list
    # Find a way to record the window characteristics

    if debug:
        print 'Battery level calculated for battery aware model and added to dataframe'
    output = sum(sanity) / len(sanity)
    calcPerf(df, test, 'eno')


# --------------------------------------------------------------------------- #
""" This function calculates the energy consumption of the whole performance
of the system where LESS is MORE. """


def lessWSN(df, test):
    if debug:
        print "working out LESS current consumption bits"
    orchastPlace_list = df['Orchastration Requirements'].tolist()
    Eg_Nwi2 = [0.1] * Nw
    Eg_Nwi = [0.1] * Nw
    duty_Nw = []
    # This defines the duty cycle starting point for any window size Nw (following Kansal method)
    for key in range(0, Nw):
        if key <= round((0.333 * Nw), 0):
            duty_Nw.append(min_tx_freq)
        elif key > round((0.333 * Nw), 0) and key <= round((0.666 * Nw)):
            duty_Nw.append(max_tx_freq)
        elif key > round((0.666 * Nw)):
            duty_Nw.append(min_tx_freq)
        else:
            pass

    # Change this to EG_total
    currentgen_list = df['Energy Generation Total'].tolist()
    # This list contains the battery level of the system over the source of the system . Assumes state zero is full battery
    batterylevel_list = [initial_battery_capacity_mah]
    #  This is a simple flag to show when battery is full (2),  battery is empty/system dead (0) or nominally operating (1)
    batterylevelflag_list = [2]
    # This records surplus energy generation that otherwise wouldn't be used when there is no ENO utility stuff
    energygensurplus_list = [0]
    # This list records times of where energy consumption is greater than generation. This is then used to derive battery health
    energydeficit_list = [0]
    Icons_list = [0]
    sens_freq_list = []
    sens_freq_list.append(duty_Nw[0])
    # current battery level. Makes assumption that system starts full
    prev = initial_battery_capacity_mah
    sanity = []
    loop = 0

    for a in currentgen_list[1:]:
        sens_freq_eno = duty_Nw[loop]
        sens_freq_needed = orchastPlace_list[loop]
        # Think about this, this needs to choose the orchastrator amount unless that will kill the sustainability of the system
        sens_freq = min(sens_freq_eno, sens_freq_needed)
        # sens_freq = duty_Nw[loop] #added this in instead the line above with hopes it would have been simpler. It wasn't
        # if sens_freq_needed > sens_freq_eno:
        #	duty_Nw[loop] = sens_freq_needed
        # So there's 4 version of the algo. 1. max 2. min. 3. max + if statement. 4. min + if statement
        Icons = ((Iq + ((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * sens_freq)) * (random.uniform(
            energy_cons_var[0], energy_cons_var[1])))  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted
        Icons_list.append(Icons)
        x = prev + (((a) - Icons) / 2)
        if x > prev:  # This if takes care of the times when battery is full so we don't report greater than 100% storage
            batterylevel_list.append(prev)
            batterylevelflag_list.append(2)
            y = x - prev
            energygensurplus_list.append(y)
            energydeficit_list.append(0)
            sens_freq_list.append(sens_freq)

        elif x < 0:  # This takes care of when battery is empty. Doesn't report negative storage
            batterylevel_list.append(0)
            batterylevelflag_list.append(0)
            energygensurplus_list.append(0)
            temp = x - prev
            energydeficit_list.append(temp)
            prev = 0
            # Here I could ammend to the amount of tx's they were able to do before the battery died?
            sens_freq_list.append(0)
        else:  # Normal operating for system, to calc new battery level
            batterylevel_list.append(x)
            batterylevelflag_list.append(1)
            energygensurplus_list.append(0)
            prev = x
            sens_freq_list.append(sens_freq)

        Eg_Nwi[loop] = round(Eg_Nwi[loop], 2)
        # Have a think about how I abstracted the ENO function with EWMA between N_w and Eg_nwi, should I expand for clarity?
        Eg_Nwi[loop] = a

        # Sensing frequency considerations
        cost_per_tx = ((((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * 1))
                       * (random.uniform(energy_cons_var[0], energy_cons_var[1])))
        # residual_energy = (Eg_Nwi[loop] - Iq) - (duty_Nw[loop]*cost_per_tx) # Editing this line to calculate residual energy from the chosen sens freq and not the duty_Nw loop every time
        residual_energy = (Eg_Nwi[loop] - Iq) - (sens_freq * cost_per_tx)
        # There is more energy generated than used in the timeslot
        if loop == Nw:
            pass
        else:
            while abs(residual_energy) > (cost_per_tx + (0.5 * cost_per_tx)):
                if residual_energy >= cost_per_tx:  # If theres a surplus energy
                    diff_1 = 0
                    counter = loop
                    # This finds the point further along in the loop where the ENO is furthest below the orchestrator
                    for a, b in zip(duty_Nw[loop:], orchastPlace_list[loop:]):
                        diff = b - a
                        if diff > 0:
                            if diff > diff_1:
                                index_diff = counter
                                diff_1 = diff
                        counter = counter + 1
                    # These don't do anything unless you change pass to break.
                    if duty_Nw[index_diff] == max_tx_freq:
                        break
                    duty_Nw[index_diff] = duty_Nw[index_diff] + 1
                    residual_energy = residual_energy - cost_per_tx

                # There is a deficit in energy greater than the energy needed to send a transmission
                if residual_energy < 0 and abs(residual_energy) > cost_per_tx:
                    diff_1 = 0
                    counter = loop
                    # This finds the point further along in the loop where the ENO is furthest below the orchestrator
                    for a, b in zip(duty_Nw[loop:], orchastPlace_list[loop:]):
                        diff = a - b
                        if diff > 0:
                            if diff > diff_1:
                                index_diff = loop
                                diff_1 = diff
                        counter = counter + 1
                    # These don't do anything unless you change pass to break.
                    if duty_Nw[index_diff] == min_tx_freq:
                        break
                    duty_Nw[index_diff] = duty_Nw[index_diff] - 1
                    residual_energy = residual_energy + cost_per_tx
                else:
                    pass
        #loop2 += 1
        loop += 1
        if loop > Nw - 1:
            # This checks the number of transmissions over or under utilised + is surplus energy, negative is energy defecit
            sanity_check = round(
                ((sum(Eg_Nwi)) - (sum(duty_Nw) * cost_per_tx)), 1)
            sanity.append(sanity_check)
            loop = 0

    df['Battery Level'] = batterylevel_list
    df['Battery Level Flag'] = batterylevelflag_list
    #df['Energy Surplus List'] = energygensurplus_list
    #df['Energy Deficit List'] = energydeficit_list
    df['Energy Consumption'] = Icons_list
    df['Sense Frequency'] = sens_freq_list
    # Find a way to record the window characteristics

    if debug:
        print 'Battery level calculated for battery aware model and added to dataframe'
    output = sum(sanity) / len(sanity)
    calcPerf(df, test, 'LESS')


# --------------------------------------------------------------------------- #
def dumpData(test):
    if output_jsons:
        epoch_time = int(time.time())
        resultFile = open(
            "datasets/results/{}_{}_solartracking_results.json".format(epoch_time, test), 'wb')
        simplejson.dump(output_jsons, resultFile)
        resultFile.close()


# --------------------------------------------------------------------------- #
def graphData(df):
    tests = ['orchas', 'static', 'LESS', 'eno']
    static_graph, eno_graph, less_graph, orchas_graph, graph = [], [], [], [], []
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

    # index=df.index.get_values()
    plt.plot(orchas_graph[0], c='blue', linewidth=1.5, label='Orchestrator')
    plt.plot(static_graph[0], c='green', linewidth=1.5, label='Static')
    plt.plot(eno_graph[0], c='red', linewidth=1.5, label='ENO')
    less_graph[0].pop(0)
    less_graph.append(2)
    plt.plot(less_graph[0], c='orange', linewidth=1.5, label='LESS')
    plt.plot(graph[0], '--', linewidth=1.0, label='Target')
    # plt.plot() plot the orchestration requirement as dotted line TD
    legend = plt.legend(loc='upper right', shadow=True)
    plt.xlabel('Time Slot, t', {'color': 'black',
                                'fontsize': 22})
    plt.ylabel('Duty Cycle, D_t', {'color': 'black',
                                   'fontsize': 22})
    plt.grid(True, which='both')
    plt.minorticks_on
    plt.ylim(ymax=33, ymin=0)
    plt.xlim(xmax=350, xmin=0)
    plt.show()
    # Add labelling automatically
    # Change show graph to save graph


# --------------------------------------------------------------------------- #
# Adding function to take care of summing energy sources
def energyGenTotal(df):
    if debug:
        print 'Calculating Total Energy Production'
    solar_list = df["Energy Solar Gen"].tolist()
    wind_list = df["Energy Wind Gen"].tolist()
    teg_list = df["Energy TEG Gen"].tolist()
    currentgen_list = []
    for a, b, c in zip(solar_list, wind_list, teg_list):
        x = 0
        if "s" in energy_combination:
            x += (a * (random.uniform(solar_prod_var[0], solar_prod_var[1])))
        if "w" in energy_combination:
            x += (b * (random.uniform(wind_prod_var[0], wind_prod_var[1])))
        if "t" in energy_combination:
            x += (c * (random.uniform(teg_prod_var[0], teg_prod_var[1])))
        currentgen_list.append(x)
    df['Energy Generation Total'] = currentgen_list
    if debug:
        print 'Energy level calculated and added to dataframe'
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
# Main
def main():
    orchest_loop = []
    # orchest_loop.append(orchastLamps)
    # orchest_loop.append(orchastMicro)
    orchest_loop.append(orchastMulti)
    for orchest in orchest_loop:
        for test in test_loop:
            # loads environmental variables from location and time defined in NREL.py. If not local it downloads them from the NREL database and parses them for use.
            df = dfLoad(test)
            if not df.empty:
                # Currently only works for one loop because of this line but can be fixed later
                if test_loop.index(test) == 0:
                    df = sysRequirements(df, test, orchest)
                # Calculates energy generated by solar panel for day
                df = panelEnergyGen(df, test)
                # calculated wind power produciton from environmental variables
                df = NRELtoWindPower(df)
                # calculates thermal energy generation from environmental variables
                df = NRELtoTEGPower(df)
                # calculates energy total by summing the above
                df = energyGenTotal(df)
                staticWSN(df, test)
                if debug:
                    print "Calculating the static WSN performance"
                orchasWSN(df, test)
                if debug:
                    print "Calculating the centrally controlled WSN performance"
                enoWSN(df, test)
                if debug:
                    print "Calculating the solely ENO controlled WSN performance"
                lessWSN(df, test)
                if debug:
                    print "Calculating the LESS=MORE WSN performance"
                dumpData(test)
                if debug:
                    print output_jsons
                # graphData(df)
                # tableData(df)
                del output_jsons[:]
                # graphEg(df)


# main()
# profile.run('main()') # Run this if you want timing of each run of the code

# Do I want to use the ICDCS style testing. Robustness to different Nw, different energy sources, different battery sizes etc...
# Different requirements ? ? ? or test for multiple dynamic requirements
# figure out how to include the overhead of transmission for the MORE and LESS algorithms at start of time window
# Do we want to include the conservative (min instead of max) LESS algorithm in discussion - Will
