# coding: utf-8

import random
from NREL import *

class LESSENO():

    # --------------------------------------------------------------------------- #
    """ This function calculates the energy consumption of the whole performance
    of the system where LESS is MORE. """

    def lessWSN(self, df, test):
        # if debug:
        print(" => Working out LESS current consumption bits")
        orchastPlace_list = df['Orchastration Requirements'].tolist()
        #Eg_Nwi2 = [0.1] * Nw
        #Eg_Nwi = [0.1] * Nw
        # duty_Nw = []
        # # This defines the duty cycle starting point for any window size Nw (following Kansal method)
        # for key in range(0, Nw):
        #     if key <= round((0.333 * Nw), 0):
        #         duty_Nw.append(min_tx_freq)
        #     elif key > round((0.333 * Nw), 0) and key <= round((0.666 * Nw)):
        #         duty_Nw.append(max_tx_freq)
        #     elif key > round((0.666 * Nw)):
        #         duty_Nw.append(min_tx_freq)
        #     else:
        #         pass

        # Modify to introduce energy prediction separately
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
        sens_freq_list.append(min_tx_freq)
        
        # current battery level. Makes assumption that system starts full
        cur_bat_level = initial_battery_capacity_mah


        counter = 0
        time_slot = 0

        for slot_en_gen in currentgen_list[1:]:
           
            sens_freq_needed = orchastPlace_list[time_slot]

            if time_slot == 0:
                # sens_freq_eno = duty_Nw[loop]
                # Start of Planning Phase
                day_energy_pred = currentgen_list[counter:counter+Nw]
                # day_energy_pred = currentgen_list[counter:counter+Nw]
                # print("day_energy_pred", [ '%.1f' % elem for elem in day_energy_pred ])                
            
                # Sensing frequency considerations
                I_cons_per_tx = ((((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * 1))
                               * (random.uniform(energy_cons_var[0], energy_cons_var[1])))

                duty_Nw = []
                for slot_pred in day_energy_pred:
                    slot_duty = round(slot_pred/I_cons_per_tx)
                    
                    if slot_duty > max_tx_freq:
                        duty_Nw.append(max_tx_freq)
                    elif slot_duty < min_tx_freq:
                        duty_Nw.append(min_tx_freq)
                    else:
                        duty_Nw.append(slot_duty)

                #print("duty_Nw =>", duty_Nw)                
           
            ### End of Planning Phase

            ### Start of Operations Phase
            sens_freq_eno = duty_Nw[time_slot]

            test = 'tmin'
            if "tmin" in test:
                # Think about this, this needs to choose the orchastrator amount unless that will kill the sustainability of the system
                sens_freq = min(sens_freq_eno, sens_freq_needed)            
            if "tmax" in test:
                sens_freq = max(sens_freq_eno, sens_freq_needed)            
            if "tfair" in test:
                #if   
                sens_freq = avg(sens_freq_eno, sens_freq_needed)
            if "tbatt" in test:
                x += (c * (random.uniform(teg_prod_var[0], teg_prod_var[1])))



            # sens_freq = duty_Nw[loop] #added this in instead the line above with hopes it would have been simpler. It wasn't
            # if sens_freq_needed > sens_freq_eno:
            #	duty_Nw[loop] = sens_freq_needed
            # So there's 4 version of the algo. 1. max 2. min. 3. max + if statement. 4. min + if statement
            Icons = ((Iq + ((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * sens_freq)) * (random.uniform(
                energy_cons_var[0], energy_cons_var[1])))  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted
            Icons_list.append(Icons)
            
            x = cur_bat_level + (((slot_en_gen) - Icons) / 2)
            if x > initial_battery_capacity_mah:  # This if takes care of the times when battery is full so we don't report greater than 100% storage
                batterylevel_list.append(initial_battery_capacity_mah)
                batterylevelflag_list.append(2)
                y = ((slot_en_gen) - Icons) / 2
                energygensurplus_list.append(y)
                energydeficit_list.append(0)
                sens_freq_list.append(sens_freq)

            elif x < 0:  # This takes care of when battery is empty. Doesn't report negative storage
                batterylevel_list.append(0)
                batterylevelflag_list.append(0)
                energygensurplus_list.append(0)
                temp = x - cur_bat_level
                energydeficit_list.append(temp)
                cur_bat_level = 0
                # Here I could ammend to the amount of tx's they were able to do before the battery died?
                sens_freq_list.append(0)
                
            else:  # Normal operating for system, to calc new battery level
                batterylevel_list.append(x)
                batterylevelflag_list.append(1)
                energygensurplus_list.append(0)
                cur_bat_level = x
                sens_freq_list.append(sens_freq)

            #Eg_Nwi[time_slot] = round(Eg_Nwi[time_slot], 2)
            # Have a think about how I abstracted the ENO function with EWMA between N_w and Eg_nwi, should I expand for clarity?
            #Eg_Nwi[time_slot] = slot_en_gen

            # Sensing frequency considerations
            cost_per_tx = ((((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * 1))
                           * (random.uniform(energy_cons_var[0], energy_cons_var[1])))
            # residual_energy = (Eg_Nwi[loop] - Iq) - (duty_Nw[loop]*cost_per_tx) # Editing this line to calculate residual energy from the chosen sens freq and not the duty_Nw loop every time
            #residual_energy = (Eg_Nwi[time_slot] - Iq) - (sens_freq * cost_per_tx)
            # There is more energy generated than used in the timeslot
            #if time_slot == Nw:
            #    pass
            #else:
            #    while abs(residual_energy) > (cost_per_tx + (0.5 * cost_per_tx)):
            #        if residual_energy >= cost_per_tx:  # If theres a surplus energy
            #            diff_1 = 0
            #            counter = time_slot
                        # This finds the point further along in the loop where the ENO is furthest below the orchestrator
            #            for a, b in zip(duty_Nw[time_slot:], orchastPlace_list[time_slot:]):
             #               diff = b - a
            #                if diff > 0:
            #                    if diff > diff_1:
            #                       index_diff = counter
            #                        diff_1 = diff
            #                counter = counter + 1
                        # These don't do anything unless you change pass to break.
            #            if duty_Nw[index_diff] == max_tx_freq:
            #                break
            #            duty_Nw[index_diff] = duty_Nw[index_diff] + 1
            #            residual_energy = residual_energy - cost_per_tx

                    # There is a deficit in energy greater than the energy needed to send a transmission
            #        if residual_energy < 0 and abs(residual_energy) > cost_per_tx:
            #            diff_1 = 0
            #            counter = time_slot
                        # This finds the point further along in the loop where the ENO is furthest below the orchestrator
            #            for a, b in zip(duty_Nw[time_slot:], orchastPlace_list[time_slot:]):
            #                diff = a - b
            #                if diff > 0:
            #                    if diff > diff_1:
            #                        index_diff = time_slot
            #                        diff_1 = diff
            #                counter = counter + 1
                        # These don't do anything unless you change pass to break.
            #            if duty_Nw[index_diff] == min_tx_freq:
            #                break
            #            duty_Nw[index_diff] = duty_Nw[index_diff] - 1
            #            residual_energy = residual_energy + cost_per_tx
            #        else:
            #            pass
            #loop2 += 1

            counter += 1
            time_slot += 1          
            if time_slot > Nw - 1:  
                time_slot = 0

        df['Battery Level'] = batterylevel_list
        df['Battery Level Flag'] = batterylevelflag_list
        #df['Energy Surplus List'] = energygensurplus_list
        #df['Energy Deficit List'] = energydeficit_list
        df['Energy Consumption'] = Icons_list
        df['Sense Frequency'] = sens_freq_list
        # Find a way to record the window characteristics

        # if debug:
        print(" => Battery level calculated for battery aware model and added to dataframe")
        #output = sum(sanity) / len(sanity)