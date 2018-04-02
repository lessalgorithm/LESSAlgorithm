import random
import numpy as np
from nrel import *

class KansalENO():

    # --------------------------------------------------------------------------- #
    """ This function calculates energy consumption if the system only relies on the
    LESS algorithm (without taking into account the MORE aspect)"""


    def enoWSN(self, df, test):
        if debug:
            print(" => Working out ENO current consumption bits")

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
            print(" => Battery level calculated for battery aware model and added to dataframe")
        output = sum(sanity) / len(sanity)