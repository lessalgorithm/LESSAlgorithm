# coding: utf-8

import random
from NREL import *

class OrchestratorENO():

	# --------------------------------------------------------------------------- #
	""" This function calculates the energy consumption of the WSN if only
	controlled by the MORE algorithm. """

	def orchasWSN(self, df, test):
		
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

		orchestPlace_List = df['Orchastration Requirements'].tolist()
		# print("orchestPlace_List => ", orchestPlace_List);

		sens_freq_list = []
		sens_freq_list.append(orchestPlace_List[0])
		
		# I_cons_list = [((((Iq + ((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * a)) * (random.uniform(
		# 	energy_cons_var[0], energy_cons_var[1]))) for a in orchestPlace_List]  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted

		# batteryLevel(df,test,Icons_list,'orchas')
		currentgen_list = df['Energy Generation Total'].tolist()
		# print("currentgen_list => ", currentgen_list)
		
		counter = 0

		# for a, slot_en_gen, orchest_req in zip(Icons_list[1:], currentgen_list[1:], orchestPlace_List[1:]):
		for slot_en_gen in currentgen_list[1:]:
			
			I_cons = ((Iq + ((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * orchestPlace_List[counter])) * (random.uniform(
			energy_cons_var[0], energy_cons_var[1])))  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted
			I_cons_list.append(I_cons)

			new_energy_level = cur_bat_level + ((slot_en_gen - I_cons) / 2)
			# print("orchestPlace_List[counter] => ", orchestPlace_List[counter], "I_cons => ", I_cons, "cur_bat_level => ", cur_bat_level, "new_energy_level => ", new_energy_level, "slot_en_gen => ", slot_en_gen)
			
			# This if takes care of the times when battery is full so we don't report greater than 100% storage
			if new_energy_level > initial_battery_capacity_mah:
				print(new_energy_level, ">", cur_bat_level)			
				batterylevel_list.append(initial_battery_capacity_mah)
				batterylevelflag_list.append(2) 
				energy_surplus = new_energy_level - initial_battery_capacity_mah
				energygensurplus_list.append(energy_surplus)
				energydeficit_list.append(0)				
				cur_bat_level = initial_battery_capacity_mah
				sens_freq_list.append(orchestPlace_List[counter])

			elif new_energy_level < 0:  # This takes care of when battery is empty. Doesn't report negative storage
				print("new_energy_level < 0")
				batterylevel_list.append(0)
				batterylevelflag_list.append(0)
				energygensurplus_list.append(0)
				energydeficit_list.append((slot_en_gen - I_cons) / 2)
				print("energy deficit =>", (slot_en_gen - I_cons) / 2)
				cur_bat_level = 0
				sens_freq_list.append(0)

			else:  # Normal operating for system, to calc new battery level
				print("normal")
				batterylevel_list.append(new_energy_level)
				batterylevelflag_list.append(1)
				energygensurplus_list.append(0)
				energydeficit_list.append(0)
				cur_bat_level = new_energy_level
				sens_freq_list.append(orchestPlace_List[counter])
	
			counter += 1



		# for a, b, c in zip(Icons_list[1:], currentgen_list[1:], orchestPlace_List[1:]):
		# 	x = cur_bat_capacity + ((b - a) / 2)
		# 	if x > initial_battery_capacity_mah:  # if there is a surplus energy and battery is full
		# 		# this is the energy wasted in mAh
		# 		energygensurplus_list.append(x - initial_battery_capacity_mah)
		# 		# this appends zero to the deficit list as we have not wasted energy
		# 		energydeficit_list.append(0)
		# 		# appends a 2 to the level flag list
		# 		batterylevelflag_list.append(2)
		# 		# records the battery level for final calculations
		# 		batterylevel_list.append(initial_battery_capacity_mah)
		# 		cur_bat_capacity = initial_battery_capacity_mah
		# 		sens_freq_list.append(c)  # Think about where to put this

		# 	elif x < 0:  # This takes care of when battery is empty. Doesn't report negative storage
		# 		batterylevel_list.append(0)
		# 		batterylevelflag_list.append(0)
		# 		energygensurplus_list.append(0)
		# 		energydeficit_list.append(x - cur_bat_capacity)
		# 		cur_bat_capacity = 0
		# 		sens_freq_list.append(0)

		# 	else:  # Normal operating for system, to calc new battery level
		# 		batterylevel_list.append(x)
		# 		batterylevelflag_list.append(1)
		# 		energygensurplus_list.append(0)
		# 		energydeficit_list.append(0)
		# 		cur_bat_capacity = x
		# 		sens_freq_list.append(c)

		# pass these metrics to a list so that the calcPerf can use them later
		df['Energy Consumption'] = I_cons_list
		df['Battery Level'] = batterylevel_list
		df['Battery Level Flag'] = batterylevelflag_list
		df['Sense Frequency'] = sens_freq_list
		# if debug:
		print(" => Orchestration Current consumption calculated")
