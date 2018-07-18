# coding: utf-8

import random
from NREL import *

class LESSENO():

    # --------------------------------------------------------------------------- #
    """ This function calculates the energy consumption of the whole performance
    of the system where LESS is MORE. """

    # def lessWSN(self, df, test,initial_battery_capacity_mah):
    def lessWSN(self, df, test):

        # if debug:
       # print(" => Working out LESS current consumption bits")
        orchastPlace_list = df['Orchastration Requirements'].tolist()
  
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
        # sens_freq_list.append(min_tx_freq)
        
        # current battery level. Makes assumption that system starts full
        cur_bat_level = initial_battery_capacity_mah
        #cur_bat_levelp = initial_battery_capacity_mah
        counter = 0
        time_slot = 0
        test = 'tbatt' # Replace this by calling the function 4 times. 

        for slot_en_gen in currentgen_list[1:]:
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


                if "tbatt" in test:
                    cur_bat_levelp = cur_bat_level

                    # Works out in advance the sustainable OP for the system
                    p1_sens_freq = []
                    p1_sens_freq_diff =[]
                    batt_level = []
                    for dt,op in zip(duty_Nw,orchastPlace_list):
                        p1_sens_freq.append(min(dt, op))
                        #p1_sens_freq_diff.append(op - dt)
                        p1_sens_freq_diff.append(min(dt, op) -op)

                    # print p1_sens_freq_diff
                    batt_level = LESSENO.battLevel(self,p1_sens_freq,day_energy_pred,I_cons_per_tx,cur_bat_levelp,initial_battery_capacity_mah)
                    
                    cur_bat_levelp = batt_level[-1:]
                    cur_bat_levelp = cur_bat_levelp[0]

                # Then predicts the battery storages over the data at this rate
                
                # Then looks through for timeslots where sens_freq is lower than op. It increments the first timeslot by one and then reassesses if the battery will die. If not it keeps going. 
                p2_sens_freq = p1_sens_freq
                loopervar = True
                while loopervar is True:
                    loopvar3 = True
                    indexd = 0 
                    for diff in p1_sens_freq_diff:
                        
                        if diff < 0:
                            p2_sens_freq[indexd] = p2_sens_freq[indexd] + 1
                            p1_sens_freq_diff[indexd] = p1_sens_freq_diff[indexd] + 1
                            #print p2_sens_freq
                        batt_level = LESSENO.battLevel(self,p2_sens_freq,day_energy_pred,I_cons_per_tx,cur_bat_levelp,initial_battery_capacity_mah)
                        #print batt_level
                        loopervar2 = True
                        for level in batt_level:
                            if level < 2:
                               # print ("called")
                                break
                                loopervar2 = False
                                loopervar = False
                                #print ("I've broken the loop")
                            else:
                                p1_sens_freq = p2_sens_freq


                        if loopervar2 is False:
                            loopvar3 = False
                            break

                        if indexd == (Nw -1):
                            indexd = 0
                        
                        else:
                            indexd += 1

                        counter = 0
                        for count in p1_sens_freq_diff:
                            if count < 0:
                                counter += 1 

                        if counter == 0:
                            p1_sens_freq = p2_sens_freq
                            loopervar = False
                        else: 
                            pass 

                        counter = 0
                        #print (p1_sens_freq_diff)
                    if loopvar3 is False:
                        break 
                        # print (p1_sens_freq_diff)
                         


                # Finally updates the current battery level for the next day so it doesn't always take the global one outside the loop

            ### End of Planning Phase

            ### Start of Operations Phase

            if "tmin" in test:
                # Think about this, this needs to choose the orchastrator amount unless that will kill the sustainability of the system
                sens_freq_eno = duty_Nw[time_slot]
                sens_freq_needed = orchastPlace_list[time_slot]

                sens_freq = min(sens_freq_eno, sens_freq_needed)            
                
            if "tmax" in test:
                sens_freq_eno = duty_Nw[time_slot]
                sens_freq_needed = orchastPlace_list[time_slot]
                sens_freq = max(sens_freq_eno, sens_freq_needed)            
            
            if "tfair" in test:
                sens_freq_eno = duty_Nw[time_slot]
                sens_freq_needed = orchastPlace_list[time_slot]
                sens_freq = avg(sens_freq_eno, sens_freq_needed)

            #sens_freq = duty_Nw[loop] #added this in instead the line above with hopes it would have been simpler. It wasn't
            # if sens_freq_needed > sens_freq_eno:
            #	duty_Nw[loop] = sens_freq_needed
            # So there's 4 version of the algo. 1. max 2. min. 3. max + if statement. 4. min + if statement
            sens_freq = p1_sens_freq[time_slot] # Placeholder
           
            Icons = ((Iq + ((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * sens_freq)) * (random.uniform(energy_cons_var[0], energy_cons_var[1])))  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted
            Icons_list.append(Icons)
            
            x = cur_bat_level + (((slot_en_gen) - Icons) / 2)
            if x > initial_battery_capacity_mah:  # This if takes care of the times when battery is full so we don't report greater than 100% storage
                batterylevel_list.append(initial_battery_capacity_mah)
                #batterylevelflag_list.append(2)
                batterylevelflag_list.append(2)
                y = ((slot_en_gen) - Icons) / 2
                #energygensurplus_list.append(y)
                energydeficit_list.append(0)
                sens_freq_list.append(sens_freq)
                surp = LESSENO.setWSN(self, df, y,)
                energygensurplus_list.append(surp)
                cur_bat_level = initial_battery_capacity_mah

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
            #cost_per_tx = ((((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * 1))
                         #  * (random.uniform(energy_cons_var[0], energy_cons_var[1])))
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

        sens_freq_list.append(min_tx_freq)

        #print batterylevel_list
        df['Battery Level'] = batterylevel_list
        df['Battery Level Flag'] = batterylevelflag_list
        df['Energy Surplus List'] = energygensurplus_list
        #df['Energy Deficit List'] = energydeficit_list
        df['Energy Consumption'] = Icons_list
        df['Sense Frequency'] = sens_freq_list
        # Find a way to record the window characteristics

        # if debug:
       # print(" => Battery level calculated for battery aware model and added to dataframe")
        #output = sum(sanity) / len(sanity)

    def battLevel(self,p1_sens_freq,day_energy_pred,I_cons_per_tx,cur_bat_levelp,initial_battery_capacity_mah):
        p1_cons = []

        for dt in p1_sens_freq:
          p1_cons.append(dt*I_cons_per_tx)

       # print ("what is the p1_cons level =>",p1_cons)

        batt_levelf = []
        #print batt_levelf
        for cons,gen in zip(p1_cons,day_energy_pred):
            new_bat_capacity = cur_bat_levelp + ((gen - cons) / 2)
            if new_bat_capacity > initial_battery_capacity_mah: # This if takes care of the times when battery is full so we don't report greater than 100% storage
                batt_levelf.append(initial_battery_capacity_mah)
            elif new_bat_capacity < 0: # This takes care of when battery is empty. Doesn't report negative storage
                batt_levelf.append(0)
            else: # Normal operating for system, to calc new battery level
                batt_levelf.append(new_bat_capacity)
        #print ("what is the batt level =>",batt_levelf)

        return batt_levelf
        
    def setWSN(self, df, surplusE):
        if  surplusE > ec_tracking:
            surplusE = surplusE - ec_tracking 
        if  surplusE > ec_ota:
            surplusE = surplusE - ec_ota
        if  surplusE > ec_datacom:
            surplusE = surplusE - ec_datacom

        return surplusE