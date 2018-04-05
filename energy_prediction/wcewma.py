# coding: utf-8


class WCEWMA():
	"""Provides the implementation of the WC-EWMA energy prediction algorithm."""

	def __init__(self, slotPerDayCount):
		self.slotPerDayCount = slotPerDayCount;


	def compute_wcewma_pred_vector(self, df):
		total_slot_count = len(df['Energy Solar Gen'].tolist())
		day_count = total_slot_count / 48

		print("day_count =>", day_count)

		wvList = []
		refSolarPowerVector = [[]]
		wcewma_pred_vector = []

		for i in range(1, round(day_count + 1)):
			start_slot = (i - 1) * self.slotPerDayCount
			end_slot = (i * self.slotPerDayCount) - 1                     
			wvList.append(self.weather_volatility_value(df, start_slot, end_slot, 5, 0.8))
			print("wv(", i,") = ", wvList[i-1])
                
            # df, cloudiness_degree_threshold, currentDayIndex, currentDayRefSolarPower, weighting_factor
                
		for i in range(1, round(day_count + 1)):
			refSolarPowerVector.insert(i,(self.getNextDayRefSolarPowerVector(df, 3, i, 0.5)))

		wcewma_pred_vector = self.get_wcewma_for_day(df, refSolarPowerVector)

		return wcewma_pred_vector

	# --------------------------------------------------------------------------- #
	""" This function creates a prediction of current energy generated. This is a
	placeholder """

	# Distributed Networking in Autonomic
	# Solar Powered Wireless Sensor Networks

	# A day is divided into M non- overlapping prediction intervals, each of which consists of 
	# L slot(s) with a duration T (i.e. M · L · T = 24 hours).
	# 
	# We can use the triple (i, l, d) to refer to a slot i in the prediction interval l of 
	# the dth day.

	# Let Pre(i, l, d) be the reference solar power in slot (i, l, d) to reflect the seasonal 
	# stable solar pofile governed by the long-term geographical climate. The reference power 
	# vector is only updated once at the end of a day as follows:

	# Pre(i, l, d + 1) =  
	#                     Pre(i, l, d),           wv(d) ≥ wvT 
	#                     αrePreal (i,l,d)+(1−αre)Pre(i,l,d) otherwise

	# where preal (i, l, d) is the real solar power metered in slot solar (i, l, d); αre ∈ [0, 1] 
	# is the weighting factor; wv(d) is weather condition level of the dth day (explained in next 
	# subsection), i.e. the more sunny the dth day is, the smaller wv(d) is; wvT is a predefined cloudiness 
	# degree threshold. Consequently, P (i,l,d) is only updated when the dth day is not quite cloudy, 
	# which aims to filter the influence of bad weather days (noise) on the seasonal stable reference power.
	def get_wcewma_for_day(self, df, ref_solar_power_vector):
		real_solar_data = df['Energy Solar Gen'].tolist()
		ref_solar_power_list = []
		vector = []

		for i in range(len(ref_solar_power_vector)):
			for j in range(len(ref_solar_power_vector[i])):
				ref_solar_power_list.append(ref_solar_power_vector[i][j])
    
		# print("len(real_solar_data)", len(real_solar_data))
		# print("len(ref_solar_power_list)", len(ref_solar_power_list))

		for i in range(len(ref_solar_power_list)):
			# if(i == 0):
			#     pred_slot = ref_solar_power_list[i]
			# else:
			if((i > 0) and (ref_solar_power_list[i - 1] > 0)):
				pred_slot = (real_solar_data[i - 1] / ref_solar_power_list[i - 1]) * ref_solar_power_list[i]
			else:
				pred_slot = ref_solar_power_list[i]

			vector.append(pred_slot)

		return vector

	# Return weather volatility value (wv(d))
	#   wv_0(d) => fluctuation frequency; total number of peaks and troughs
	#   wv_1(d) => fluctuation intensity
	#   h_i => indicates increase in real harvested solar energy
	def weather_volatility_value(self, df, start_slot, end_slot, threshold, weighting_factor):
		wv_0 = 0
		wv_1 = 0

		# print(df['Energy Solar Gen'])

		# loop over the duration of (M intervals * L slots)
		for i in range (start_slot + 2, end_slot) :
			h_i = (1 if df['Energy Solar Gen'][i] > df['Energy Solar Gen'][i-1] else 0)
			h_i_1 = (1 if df['Energy Solar Gen'][i-1] > df['Energy Solar Gen'][i-2] else 0)
			g_i = (1 if (df['Energy Solar Gen'][i] - df['Energy Solar Gen'][i-1] >= threshold) else 0)

			wv_0 += (bool(h_i) ^ bool(h_i_1)) # bitwise xor
			wv_1 += (bool(h_i) ^ bool(h_i_1)) and g_i # bitwise xor    

		wv = weighting_factor*wv_1 + (1 - weighting_factor) * (wv_0 - wv_1)

		return wv


	# # αre ∈ [0, 1]
	# def weightin_factor():
	# 	return 0

	# wv(d);  the more sunny the dth day is, the smaller wv(d) is
	# wv(d) = αwv · wv1(d) + (1 − αwv) · (wv0(d) − wv1(d))
	# def weather_volatility_value():
	#     return 0

	# Pre (i, l, d); i -> slot. l -> interval, d -> day
	# Reflects the seasonal stable solar profile governed by the long-term geographical climate
	def getNextDayRefSolarPowerVector(self, df, cloudiness_degree_threshold, currentDayIndex, weighting_factor):
		vector = []

		startSlotInDF = (currentDayIndex - 1) * self.slotPerDayCount
		endSlotInDF = currentDayIndex * self.slotPerDayCount

		print("reference solar power vector for day: ", currentDayIndex, "\n")

		if currentDayIndex == 1:
			return df['Energy Solar Gen'][startSlotInDF:endSlotInDF].tolist()

		wv = self.weather_volatility_value(df, startSlotInDF, endSlotInDF, 5, 0.8)    

		previousDayVector = self.getNextDayRefSolarPowerVector(df, cloudiness_degree_threshold, currentDayIndex - 1, weighting_factor)    
		if  wv >= cloudiness_degree_threshold:        
			vector = previousDayVector
		else:
			print("start: ", startSlotInDF, "end: ", endSlotInDF-1)
			for i in range(startSlotInDF, endSlotInDF):        
				vectorIndex = i - (48 * (currentDayIndex - 1)) # the vector start at 0 and ends at 47 
				vector.append(weighting_factor * df['Energy Solar Gen'][i] + (1 - weighting_factor) * previousDayVector[vectorIndex])           

		return vector

	# # wv1(d); 
	# def fluctuation_intensity():
	# 	return 0

	# # wvT is a predefined cloudiness degree threshold
	# def cloudiness_degree_thres():
	# 	return 0
