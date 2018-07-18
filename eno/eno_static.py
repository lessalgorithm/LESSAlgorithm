# coding: utf-8
import random
from NREL import *

class StaticENO():

	# def staticWSN(self, df, test,initial_battery_capacity_mah):
	def staticWSN(self, df, test):
		
		# This list contains the battery level of the system over the source of the system . Assumes state zero is full battery
		batterylevel_list = [initial_battery_capacity_mah]
		
		#  This is a simple flag to show when battery is full (2),  battery is empty/system dead (0) or nominally operating (1)
		batterylevelflag_list = [2]

		# This records surplus energy generation that otherwise wouldn't be used when there is no ENO utility stuff
		energygensurplus_list = [0]
		
		# This list records times of where energy consumption is greater than generation. This is then used to derive battery health
		energydeficit_list = [0]

		# Holds the total energy consumption per time slot
		I_cons_list = [0]

        # current battery level. Makes assumption that system starts full
		cur_bat_level = initial_battery_capacity_mah		
		
		sens_freq_list = [sens_freq]
		
		# batteryLevel(df,test,Icons_list,'orchas')
		currentgen_list = df['Energy Generation Total'].tolist()
		
		# Load arbitrary list to iterate about. This will change to input variables when ENO in introduced		
		Icons_list = [((((Iq + ((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * sens_freq)) * (random.uniform(energy_cons_var[0],
        				energy_cons_var[1]))) for a in currentgen_list]  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted
		counter = 0		
		
		# current battery level. Makes assumption that system starts full
		cur_bat_level = initial_battery_capacity_mah
		
		# for slot_en_gen in currentgen_list[1:]:
		for I_cons, slot_en_gen in zip(Icons_list[1:], currentgen_list[1:]):
			
			new_energy_level = cur_bat_level + ((slot_en_gen - I_cons) / 2)
			
			# This if takes care of the times when battery is full so we don't report greater than 100% storage
			if new_energy_level > initial_battery_capacity_mah:				
				batterylevel_list.append(initial_battery_capacity_mah)
				batterylevelflag_list.append(2) 
				energy_surplus = new_energy_level - initial_battery_capacity_mah
				energygensurplus_list.append(energy_surplus)
				energydeficit_list.append(0)				
				cur_bat_level = initial_battery_capacity_mah
				sens_freq_list.append(sens_freq)			
				
			elif new_energy_level < 0:  # This takes care of when battery is empty. Doesn't report negative storage
				# print("new_energy_level < 0")
				batterylevel_list.append(0)
				batterylevelflag_list.append(0)
				energygensurplus_list.append(0)
				energydeficit_list.append((slot_en_gen - I_cons) / 2)
				# print("energy deficit =>", (slot_en_gen - I_cons) / 2)
				cur_bat_level = 0
				sens_freq_list.append(0)			

			else:  # Normal operating for system, to calc new battery level
				# print("normal")
				batterylevel_list.append(new_energy_level)
				batterylevelflag_list.append(1)
				energygensurplus_list.append(0)
				energydeficit_list.append(0)
				cur_bat_level = new_energy_level
				sens_freq_list.append(sens_freq)			

		# pass these metrics to a list so that the calcPerf can use them later
		df['Energy Consumption'] = Icons_list
		df['Battery Level'] = batterylevel_list
		df['Battery Level Flag'] = batterylevelflag_list
		df['Energy Surplus List'] = energygensurplus_list
		df['Energy Deficit List'] = energydeficit_list
		df['Sense Frequency'] = sens_freq_list
		# if debug:
		#print(" => Static Current consumption calculated")


	# --------------------------------------------------------------------------- #
	""" This function calculates the consumption of a WSN where each sensor always
	performs at it's maximum duty cycle. """

	# def staticWSN(self, df, test):
	# 	# if debug:
	# 	print(" => Working out static current consumption bits")
	# 	# Load arbitrary list to iterate about. This will change to input variables when ENO in introduced
	# 	DHI_list = df["DHI"].tolist()
	# 	Icons_list = [((((Iq + ((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * sens_freq)) * (random.uniform(energy_cons_var[0],
 #                                                                                                                                 energy_cons_var[1]))) for a in DHI_list]  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted
	# 	currentgen_list = df['Energy Generation Total'].tolist()
	# 	#  This is a simple flag to show when battery is full (2),  battery is empty/system dead (0) or nominally operating (1)
	# 	batterylevelflag_list = [2]
	# 	# This records surplus energy generation that otherwise wouldn't be used when there is no ENO utility stuff
	# 	energygensurplus_list = [0]
	# 	# This list records times of where energy consumption is greater than generation. This is then used to derive battery health
	# 	energydeficit_list = [0]
	# 	sens_freq_list = [sens_freq]
	# 	# This list contains the battery level of the system over the source of the system . Assumes state zero is full battery
	# 	batterylevel_list = [initial_battery_capacity_mah]
	# 	# current battery level. Makes assumption that system starts full
	# 	prev = initial_battery_capacity_mah
	# 	for a, b in zip(Icons_list[1:], currentgen_list[1:]):
	# 		x = prev + ((b - a) / 2)
	# 		if x > initial_battery_capacity_mah:  # if there is a surplus energy and battery is full
	# 			# this is the energy wasted in mAh
	# 			energygensurplus_list.append(x - initial_battery_capacity_mah)
	# 			# this appends zero to the deficit list as we have not wasted energy
	# 			energydeficit_list.append(0)
	# 			# appends a 2 to the level flag list
	# 			batterylevelflag_list.append(2)
	# 			# records the battery level for final calculations
	# 			batterylevel_list.append(initial_battery_capacity_mah)
	# 			prev = initial_battery_capacity_mah
	# 			sens_freq_list.append(sens_freq)  # Think about where to put this
	# 		elif x < 0:  # This takes care of when battery is empty. Doesn't report negative storage
	# 			batterylevel_list.append(0)
	# 			batterylevelflag_list.append(0)
	# 			energygensurplus_list.append(0)
	# 			energydeficit_list.append(x - prev)
	# 			prev = 0
	# 			sens_freq_list.append(0)

	# 		else:  # Normal operating for system, to calc new battery level
	# 			batterylevel_list.append(x)
	# 			batterylevelflag_list.append(1)
	# 			energygensurplus_list.append(0)
	# 			energydeficit_list.append(0)
	# 			prev = x
	# 			sens_freq_list.append(sens_freq)

	# 	# pass these metrics to a list so that the calcPerf can use them later
	# 	df['Energy Consumption'] = Icons_list
	# 	df['Battery Level'] = batterylevel_list
	# 	df['Battery Level Flag'] = batterylevelflag_list
	# 	df['Energy Surplus List'] = energygensurplus_list
	# 	df['Energy Deficit List'] = energydeficit_list
	# 	df['Sense Frequency'] = sens_freq_list
	# 	# if debug:
	# 	print(" => Static Current consumption calculated")
