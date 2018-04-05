# Configuration file for NREL data call
# This file sets up the calls for data from NREL.
# 26/05/2016 Greg Jackson AESE Labs Imperial College

debug = True
storage = True # this metric determines if anything is dumped to the outputJSON

# This is to configure each Test (or do multiple tests sequentually) Currently each of these are for a week but there is a year dataset too
#test_loop = ['0ATotal','0BTotal']
dataset_list = ['0ATotal']
energy_combination = 's'  # There's nine combinations between wind solar and thermal. Let this be chosen by a string contain some or all of s=solar,t=thermal and w=wind

#  Configuration  metrics to convert NREL data to power output of a solar cell
foreground_albedo = 0.2 # This is a standard value recommended by NREL but has a small bearing on overall performance

#Solar Panel Metrics
solar_panel_voltage = 3.3
solar_panel_active_area_m2 = 0.0001 # 0.002 has been standard for testing (20cm2)
solar_panel_efficiency = 0.15 #as percentage 0.15
power_conditioning_efficiency = 1
temperature_coefficient = 0.0049
Noct = 48.6 # Leaving this as static for now, could be a way to improve this number taking into consideration ambient temperature, design of cell and wind speed
ref_cell_temp = 25
sensor_angle_V = 180
sensor_angle_H = 35 # This changes with latitude, is there a simple function I could apply?

# Wind Power Metrics
Ve = 2 # speed in m/s that the wind needs to be going in order to generate usable energy 2m/s
Vo = 20 # Speed in m/s above which the panel cannot operate. Making assumption that anything between these is nominal power generation
Area_wind = 0.405 # Swept area in meters that the wind turbine covers, used a PC fan as a sizing guide for IoT Wind was .105
cp = 0.15 # efficiency metric for the wind turbine. this covers everything from theoretical power from blades to efficiency of power electronics
R_spec = 287.057 # Specific gas constant for wind
wind_turbine_voltage = 3.3

# TEG variables
seedback_coeff = 0.00043
deltaT_min = 5
N_TEG = 310 # for Marlow NL1012T
T_ambient = 20 # for window contacts
gm = 0.9
ef = 0.9
vmin = 0.3

# Variables for EWMA filter
EWMA_A = 0.5
Nw = 48

# Energy Consumption Model
# all current consumption I's are defined in mA.
# State time (in sec) is to allow conversion to mAh
# current current approximations are to be improved on, taken from Ti SensorTag 2.0
Iq = 0.005
Is = 10.100 #0.1 for temp 10.1 for co2
Icomp = 2.1
Itx = 9.54
Ss = 2
Scomp = 3
Stx = 1
sens_freq = 30
#sens_freq = 30 # Times measurement and TX is taken in half hour. This is the number that will vary with ENO, with upper and lower bounds

energy_cons_var =[0.9,1.1] # to account for variations between transmittions
energy_spar_var = [0.75,1.25]  # To account for sensor to sensor variation

# Placeholder for requirements from orchastrator
# orchastPlace = [2,2,2,2,2,2,2,2,2,2,10,10,10,10,10,10,10,10,10,10,30,30,30,30,30,30,30,30,10,10,10,10,10,10,10,10,10,10,2,2,2,2,2,2,2,2,2,2] # Once per 30 minutes
# orchastLamps = [2,2,2,2,2,2,2,2,2,5,5,5,30,30,30,30,30,30,30,5,5,5,5,5,5,5,5,5,5,5,5,5,30,30,30,30,30,30,30,30,30,2,2,2,2,2,2,2]
# orchastMicro = [2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,2,5,5,5,5,5,5,15,15,15,30,30,30,15,15,15,15,15,15,15,15,15,15,5,5,5,2,2,2]
# orchastMulti = [2, 2, 2, 2, 2, 2, 2, 2, 2, 5, 5, 5, 30, 30, 30, 30, 30, 30, 30, 5, 5, 5, 5, 5, 5, 5, 15, 15, 15, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 30, 15, 5, 5, 5, 2, 2, 2]

# Battery Capacity
initial_battery_capacity_mah = 4 # 4mah = For TI Tag, this is 24hours in darkness
coulomb_efficiency = .996 # Ability of storage element to deliver and receive energy (percentage in dec)
battery_self_discharge = .01 # discharge of battery, percentage in dec of total capacity

# ENO Parameters
per_surplus_use = 0.8 # This metric determines the max surplus energy that can be used in ENO function
min_tx_freq = 2 # min tx freq in 30 min time window (every 15 minutes)
max_tx_freq = 30 # Max tx freq in 30 minute time window (every minute)
per_deficit_use = 0.2 # whats this?
solar_prod_var = [1,1]
wind_prod_var  = [1,1]
teg_prod_var = [1,1]
