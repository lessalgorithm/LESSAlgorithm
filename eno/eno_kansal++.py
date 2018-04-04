import random
import numpy as np
from nrel import *

class KansalWCEWMA_ENO():

    # --------------------------------------------------------------------------- #
    """ This function calculates energy consumption if the system only relies on the
    LESS algorithm (without taking into account the MORE aspect)"""


    def enoWSN(self, df, test):
        if debug:
            print(" => Working out ENO current consumption bits")

        # Eg_Nwi2 = [0.1] * Nw
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

        # This list contains the battery level of the system over the source of the system. Assumes state zero is full battery
        batterylevel_list = [initial_battery_capacity_mah]

        #  This is a simple flag to show when battery is full (2),  battery is empty/system dead (0) or nominally operating (1)
        batterylevelflag_list = [2]

        # This records surplus energy generation that otherwise wouldn't be used when there is no ENO utility stuff
        energygensurplus_list = [0]

        # This list records times of where energy consumption is greater than generation. This is then used to derive battery health
        energydeficit_list = [0]

        # Holds the total energy consumption per time slot
        I_cons_list = [0]
        
        # Holds the final sensing frequency (duty cycle) per time slot
        sens_freq_list = []
        sens_freq_list.append(duty_Nw[0])
        
        # Current battery level. Makes assumption that system starts with full battery.
        cur_bat_capacity = initial_battery_capacity_mah
        
        sanity = []
        loop = 0
        i = 0

        # Variables for EWMA filter
        for slot_en_gen in currentgen_list[1:]:
            sens_freq = duty_Nw[loop]

            # Compute the total energy consumption in time slot
            I_cons = ((Iq + ((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * sens_freq)) * (random.uniform(
                energy_cons_var[0], energy_cons_var[1])))  # Think about if I'm dividing by 2 before taking from battery is Iq being misquoted
            I_cons_list.append(I_cons)
            new_bat_capacity = cur_bat_capacity + ((slot_en_gen - I_cons) / 2)
            
            # This if takes care of the times when battery is full so we don't report greater than 100% storage
            if new_bat_capacity > cur_bat_capacity:
                batterylevel_list.append(cur_bat_capacity)
                batterylevelflag_list.append(2) # this is not true when shifting from low energy state and starting to experience surplus
                energy_surplus = new_bat_capacity - cur_bat_capacity
                energygensurplus_list.append(energy_surplus)
                energydeficit_list.append(0)
                sens_freq_list.append(sens_freq)

            # This takes care of when battery is empty. Doesn't report negative storage
            elif new_bat_capacity < 0:
                batterylevel_list.append(0)
                batterylevelflag_list.append(0)
                energygensurplus_list.append(0)
                energy_deficit = new_bat_capacity - cur_bat_capacity # shouldn't be + instead???
                energydeficit_list.append(energy_deficit)
                cur_bat_capacity = 0
                sens_freq_list.append(0)

            # Normal operating for system, to calc new battery level
            else:
                batterylevel_list.append(new_bat_capacity)
                batterylevelflag_list.append(1)
                energygensurplus_list.append(0) # shouldn't rather be the difference between new and cur?
                cur_bat_capacity = new_bat_capacity
                sens_freq_list.append(sens_freq)

            # ???
            Eg_Nwi[loop] = round(Eg_Nwi[loop], 2)
            Eg_Nwi[loop] = slot_en_gen

            # Sensing frequency considerations
            I_cons_per_tx = ((((((Is * Ss) / 1800) + ((Icomp * Scomp) / 1800) + ((Itx * Stx) / 1800)) * 1))
                           * (random.uniform(energy_cons_var[0], energy_cons_var[1])))
            
            # why not use slot_en_gen ???? instead of Eg_Nwi[loop]
            # residual_energy = (Eg_Nwi[loop] - Iq) - (sens_freq * I_cons_per_tx)
            residual_energy = (Eg_Nwi[loop] - Iq) - (duty_Nw[loop] * I_cons_per_tx)

            # Check if there is more energy generated than used in the timeslot
            if loop == Nw:
                pass
            else:
                # If residual energy can be used for at least one tx
                if residual_energy >= I_cons_per_tx:
                    # no temp here !!! just copying the reference to point to the same list !!!
                    duty_temp = duty_Nw
                    
                    # Returns the indices of the minimum values along an axis.
                    # Only the first occurrence is returned.
                    index_min = np.argmin(duty_temp)
                    print("loop =>", loop, "index_min =>", index_min)
                    surplus_tx_count = round(residual_energy / I_cons_per_tx)
                    new_duty = duty_Nw[index_min] + surplus_tx_count

                    # If duty cycle with surplus tx more than max duty allowed
                    if new_duty > max_tx_freq:
                        duty_diff = max_tx_freq - duty_Nw[index_min]
                        duty_Nw[index_min] = max_tx_freq
                        
                        # why again ???
                        duty_temp = duty_Nw
                        
                        # this should be rather recursive for all the upcoming slots isn't it?
                        new_duty = surplus_tx_count - duty_diff
                        index_min = np.argmin(duty_temp)
                        if new_duty > max_tx_freq:
                            duty_Nw[index_min] = max_tx_freq
                        else:
                            duty_Nw[index_min] = new_duty
                    else:
                        duty_Nw[index_min] = new_duty

                # There is a deficit in energy greater than the energy needed to send a transmission
                if residual_energy < 0 and abs(residual_energy) > I_cons_per_tx:
                    duty_temp = duty_Nw
                    index_max = np.argmax(duty_temp)
                    print("loop =>", loop, "index_max =>", index_max)
                    lacking_tx_count = abs(round(residual_energy / I_cons_per_tx))
                    new_duty = duty_Nw[index_max] - lacking_tx_count
                    if new_duty < min_tx_freq:
                        duty_diff = abs(min_tx_freq - duty_Nw[index_max])
                        duty_Nw[index_max] = min_tx_freq
                        
                        # why again ???
                        duty_temp = duty_Nw

                        # this should be rather recursive for all the upcoming slots isn't it?
                        index_max = np.argmax(duty_temp)
                        new_duty = lacking_tx_count - duty_diff
                        if new_duty < min_tx_freq:
                            duty_Nw[index_max] = min_tx_freq
                        else:
                            duty_Nw[index_max] = new_duty

                    else:
                        duty_Nw[index_max] = new_duty
                else:
                    pass

            loop += 1
            if loop > Nw - 1:
                # This checks the number of transmissions over or under utilised + is surplus energy, negative is energy deficit
                sanity_check = round(
                    ((sum(Eg_Nwi)) - (sum(duty_Nw) * I_cons_per_tx)), 1)
                sanity.append(sanity_check)
                loop = 0

        df['Battery Level'] = batterylevel_list
        df['Battery Level Flag'] = batterylevelflag_list
        #df['Energy Surplus List'] = energygensurplus_list
        #df['Energy Deficit List'] = energydeficit_list
        df['Energy Consumption'] = I_cons_list
        df['Sense Frequency'] = sens_freq_list
        # Find a way to record the window characteristics

        if debug:
            print(" => Battery level calculated for battery aware model and added to dataframe")
        output = sum(sanity) / len(sanity)
