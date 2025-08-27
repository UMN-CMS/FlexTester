#!/usr/bin/python                                                               
from HwInterface.ADS124 import ADS124
from Test import Test 

import argparse
from datetime import datetime
import time
import json


def parse_ID(ID): #likely will come from an imported utility class, right now just return a basic configuration
    num_modules = 1
    east = False
    return num_modules, east

def check_value(value, minimum, maximum):
    passed = (minimum < value) and (value < maximum)
    if passed:
        message = "passed"
    else:
        message = "FAILED"
    return passed, message


class id_ADS124:

    # wire connections to analog input number (12 is common)                                                                                         
    X_PWR_EN = 1
    X_RESETb = 2
    VMON_REF0 = 4
    VMON_REF1 = 8
    VMON_REF2 = 10
    PROBE_DC = 12
    WAGON_TYPE = 6
    GND = 7
    IDAC1 = 3
    IDAC2 = 5
    IDAC3 = 9
    IDAC4 = 0
    IDAC5 = 11

    def __init__(self, conn, targets=None):
        
        # Initalizing the PIPE as an attribute
        self.conn = conn

        self.chip = ADS124(bus=1, device=3)
        self.chip.wakeup()
        self.chip.reset()
        self.passing_criteria = {
            'min_resistance': 0.5,
            'max_resistance': 70.,
        }
        self.chip.reset_POR_flag()
        self.data = {}
        self.comments = []

        self.targets = [[64,1],[12,1],[39,1]] #placeholder



    def get_resistances(self, num_modules=1, east=False):

        print("testing ID chip")
        all_passed = True


        # VMON_REF0 -> PROBE_DC 
        self.chip.ref_config(1) # internal reference on (needed for IDAC)
        self.chip.set_conv_delay(7)

        self.chip.ref_input(0) # set reference source to REFP0, REFN0
        self.chip.set_gain(1,enable=False)

        self.chip.set_idac_current(500)
        self.chip.set_idac_channel(self.IDAC1,13)

        self.chip.setup_mux(self.VMON_REF0,self.PROBE_DC)
        line = 'VMON_REF0 -> PROBE_DC'
        resistance = self.chip.read_volts(vref=2000,ave=4)
        passed, message = check_value(resistance[0], self.passing_criteria['min_resistance'], self.passing_criteria['max_resistance'])
        if not passed:
            all_passed = False
            if resistance[0] <= self.passing_criteria['min_resistance']:
                self.comments.append('Short identified on module {} path {}'.format(self.module, line))
            else:
                self.comments.append('Open identified on module {} path {}'.format(self.module, line))
        self.data[line] = resistance[0]
        print("line %s resistance is %.2f ohms; %s" % (line, resistance[0], message))



        ############## Next line        
        self.chip.ref_config(1) # internal reference on (needed for IDAC)                                                                        
        self.chip.set_gain(1,enable=False)
        self.chip.set_conv_delay(7)
        self.chip.ref_input(0) # set reference source to REFP0, REFN0                                                                            
        self.chip.set_idac_channel(self.IDAC4,13)
        self.chip.set_idac_current(500)
#        self.chip.setup_mux(self.X_PWR_EN, self.PROBE_DC)
#        self.chip.setup_mux(self.X_RESETb, self.X_PWR_EN)

        self.chip.setup_mux(self.X_PWR_EN, self.X_RESETb)
        line = 'PWR_EN -> X_RESETb'
        resistance = self.chip.read_volts(vref=2000,ave=4)
        passed, message = check_value(resistance[0], self.passing_criteria['min_resistance'], self.passing_criteria['max_resistance'])
        if not passed:
            all_passed = False
            if resistance[0] <= self.passing_criteria['min_resistance']:
                self.comments.append('Short identified on module {} path {}'.format(self.module, line))
            else:
                self.comments.append('Open identified on module {} path {}'.format(self.module, line))
        self.data[line] = resistance[0]
        print("line %s resistance is %.2f ohms; %s" % (line, resistance[0], message))
     

 
        ############### Next line
        self.chip.set_idac_channel(self.IDAC2,13)
        self.chip.set_idac_current(500)
#        self.chip.setup_mux(self.WAGON_TYPE,self.VMON_REF1)
        self.chip.setup_mux(self.VMON_REF1, self.WAGON_TYPE)
        line = 'VMON_REF1 -> WAGON_TYPE'
        resistance = self.chip.read_volts(vref=2000,ave=4)
        passed, message = check_value(resistance[0], self.passing_criteria['min_resistance'], self.passing_criteria['max_resistance'])
        if not passed:
            all_passed = False
            if resistance[0] <= self.passing_criteria['min_resistance']:
                self.comments.append('Short identified on module {} path {}'.format(self.module, line))
            else:
                self.comments.append('Open identified on module {} path {}'.format(self.module, line))
        self.data[line] = resistance[0]
        print("line %s resistance is %.2f ohms; %s" % (line, resistance[0], message))



        ############## Next line        
        self.chip.set_idac_channel(self.IDAC3,13)
        #self.chip.set_idac_current(500)
        self.chip.setup_mux(self.VMON_REF2,self.PROBE_DC)
        line = 'VMON_REF2 -> PROBE_DC'
        resistance = self.chip.read_volts(vref=2000,ave=4)
        passed, message = check_value(resistance[0], self.passing_criteria['min_resistance'], self.passing_criteria['max_resistance'])
        if not passed:
            all_passed = False
            if resistance[0] <= self.passing_criteria['min_resistance']:
                self.comments.append('Short identified on module {} path {}'.format(self.module, line))
            else:
                self.comments.append('Open identified on module {} path {}'.format(self.module, line))
        self.data[line] = resistance[0]
        print("line %s resistance is %.2f ohms; %s" % (line, resistance[0], message))


        print("Did all pass? : {}".format(all_passed))

        self.chip.powerdown()

        return all_passed, self.comments


class id_resist_test(Test):

    def __init__(self, conn, board_sn=-1, tester=""):
        self.info_dict = {'name': "Flex Cable Resistance Test", 'board_sn': board_sn, 'tester': tester}
        
        
        Test.__init__(self, self.run_ID_test, self.info_dict, conn, num_modules=1, east=False)

    def run_ID_test(self, **kwargs):
        
        self.id_chip = id_ADS124(self.conn)

        passed = True
        num_modules = kwargs['num_modules']
        east = kwargs['east']
        data = {}

#        if not self.id_chip.get_resistances(num_modules, east): passed = False

        passed, comments = self.id_chip.get_resistances(num_modules, east)

        data.update({'wagon type chip': self.id_chip.data})

        comments = '\n'.join(comments)

        passing_criteria = self.id_chip.passing_criteria

        data = {'test_data': data, 'passing_criteria': passing_criteria} 
       
        self.conn.send("Done.")

        print({"pass": passed, "data": data})

        return passed, data

###############################################################################

# Main method
if __name__=="__main__":
    parser=argparse.ArgumentParser(description="RTD Test Config")
    parser.add_argument('--SN', type=str, default="dummySN", help='Wagon serial number string')
    parser.add_argument('--tester', type=str, default="anonymous", help='who is performing the test?')
    args=parser.parse_args()
    test = {'board_sn': args.SN, 'tester': args.tester}
    
    id_resist_test(**test)
