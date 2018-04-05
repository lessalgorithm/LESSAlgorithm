# coding: utf-8

import random
from nrel import *

class OrchestratorENO():

	# --------------------------------------------------------------------------- #
	""" This function calculates the energy consumption of the WSN if only
	controlled by the MORE algorithm. """

	def orchasWSN(self, df, test):
		if debug:
			print(" => Working out MORE current consumption bits")
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
		# if debug:
		print(" => Orchestration Current consumption calculated")
