
class Orchestrator():

    # def __init__(self, Name="there"):
    #     pass

    def read_sensor_reqs(self, file):
        req_dict = {}
        f = open(file)

        try:
            for line in f:
                if (len(line) > 1 and (not line.startswith('#')) and
                                      (not line.startswith('@'))):
                    line = line.strip('<>\n')
                    line = line.replace(' ', '')
                    values = line.split(',')

                    if values[1] in req_dict:
                        req_dict.get(values[1]).append(
                                values[0] + "->" + values[2])
                    else:
                        req_dict[values[1]] = [values[0] + '->' + values[2]]

        finally:
            f.close()
            # for values in req_dict:
            #     print values, ':', req_dict.get(values)
        return req_dict

    def read_app_reqs(self, file):
        req_dict = {}
        f = open(file)

        try:
            for line in f:
                if (len(line) > 1 and (line.startswith('@'))):
                    line = line.strip('@\n')
                    line = line.replace(' ', '')
                    values = line.split('=')
                    values[1] = values[1].strip('[]')

                    reqs = values[1].split(',')

                    for req in reqs:
                        if values[0] in req_dict:
                            req_dict.get(values[0]).append(req)
                        else:
                            req_dict[values[0]] = [req]
        finally:
            f.close()

        return req_dict

    # Parses the orchestrator requirements from a file
    # loc_reqs => loc : ['9:00pm-6:00am:2', ...]
    # return => loc: [rate_ts1, rate_ts2, rate_ts3, rate_tsn]
    #        => ex.: AVENUE_22: [2,2,2,2,5,5,5,15,15,...]
    def parse_reqs(self, loc_reqs):
        profile = [0]*48
        loc = loc_reqs[0]

        for req in loc_reqs[1]:
            values = req.split('->')
            time_window = values[0].split('-')            
            duty_cycle = int(values[1])

            self.generate_operational_profile(
                        profile,
                        self.get_time_window_slots(time_window),
                        duty_cycle)

        return profile

    def generate_operational_profile(self, profile, time_window_slots,
                                     duty_cycle):
        start_time_slot = time_window_slots[0]
        end_time_slot = time_window_slots[1]

        if (start_time_slot < end_time_slot):
            for x in range(start_time_slot, end_time_slot):
                profile[x] = duty_cycle
        else:
            for x in range(0, end_time_slot):
                profile[x] = duty_cycle

            for x in range(start_time_slot, 48):
                profile[x] = duty_cycle

        return profile

    def get_time_window_slots(self, time_window):
        start_time_window = time_window[0][:-2]
        start_time_period = time_window[0][-2:]

        end_time_window = time_window[1][:-2]
        end_time_period = time_window[1][-2:]

        start_time_slot = self.get_slot_index(start_time_window,
                                              start_time_period)
        end_time_slot = self.get_slot_index(end_time_window, end_time_period)

        return start_time_slot, end_time_slot

    def get_slot_index(self, time, time_period):
        mins = (int(time.split(':')[0]) * 60 +
                int(time.split(':')[1]))
        if (time_period == 'pm'):
            mins = mins + 12*60

        return int(mins)//30

# if __name__ == '__main__':
    # pass
