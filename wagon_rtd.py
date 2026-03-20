#!/usr/bin/python                                                               
#
# TODO [FFH SUPPORT]: This resistance test currently only works correctly for
# FBH (Front/Back Hadronic) flex cables. FFH (Front/Forward Hadronic) cables
# give max/open-circuit resistance readings with the current pin configuration.
#
# To support FFH cables:
#   1. Determine the correct ADS124 analog input pin mappings for FFH cables.
#      The current pin assignments (X_PWR_EN=1, X_RESETb=2, VMON_REF0=4, etc.)
#      are specific to FBH. FFH cables have a different physical layout and
#      the wires connect to different ADS124 input channels.
#   2. Determine the correct IDAC-to-channel assignments for FFH.
#   3. Determine the correct mux pairings (which lines to measure across).
#      FBH measures 4 lines:
#        - VMON_REF0 -> PROBE_DC  (IDAC1)
#        - PWR_EN -> X_RESETb     (IDAC4)
#        - VMON_REF1 -> WAGON_TYPE (IDAC2)
#        - VMON_REF2 -> PROBE_DC  (IDAC3)
#      FFH may have different line pairings and/or a different number of lines.
#   4. Add auto-detection of cable type from board_sn (like run_bert.py does)
#      and select the appropriate pin config at runtime.
#   5. No old FFH resistance configuration was ever saved in git history -
#      the FFH pin mappings need to be re-derived from the hardware/schematics.
#
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

    # TODO [FFH SUPPORT]: These pin mappings are for FBH cables ONLY.
    # FFH cables have different wire-to-ADS124-channel connections.
    # Need to add FFH-specific pin mappings and select based on cable type.
    # Consider restructuring as:
    #   FBH_PINS = { 'X_PWR_EN': 1, 'X_RESETb': 2, ... }
    #   FFH_PINS = { ... }  # To be determined from hardware/schematics
    #
    # wire connections to analog input number (12 is common) -- FBH ONLY
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
        # TODO [FFH SUPPORT]: This method's mux pairings and IDAC channel
        # assignments are FBH-specific. For FFH cables, the measurement lines
        # (VMON_REF0->PROBE_DC, PWR_EN->X_RESETb, etc.) and their associated
        # IDAC channels will be different. Add cable_type parameter or detect
        # from board_sn and branch accordingly.

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
                self.comments.append('Short identified on path {}'.format(line))
            else:
                self.comments.append('Open identified on path {}'.format(line))
        self.data[line] = resistance[0]



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
                self.comments.append('Short identified on path {}'.format(line))
            else:
                self.comments.append('Open identified on path {}'.format(line))
        self.data[line] = resistance[0]
     

 
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
                self.comments.append('Short identified on path {}'.format(line))
            else:
                self.comments.append('Open identified on path {}'.format(line))
        self.data[line] = resistance[0]



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
                self.comments.append('Short identified on path {}'.format(line))
            else:
                self.comments.append('Open identified on path {}'.format(line))
        self.data[line] = resistance[0]



        # Print resistance summary table
        min_r = self.passing_criteria['min_resistance']
        max_r = self.passing_criteria['max_resistance']
        print("Resistance Test: {}".format("PASS" if all_passed else "FAIL"))
        print("{:<25} {:>12} {:>10}".format("Line", "Resistance", "Status"))
        print("-" * 50)
        for ln, val in self.data.items():
            st = "PASS" if min_r < val < max_r else "FAIL"
            print("{:<25} {:>8.2f} ohms {:>10}".format(ln, val, st))
        print("-" * 50)

        self.chip.powerdown()

        return all_passed, self.comments


class id_resist_test(Test):

    def __init__(self, conn, board_sn=-1, tester=""):
        # TODO [FFH SUPPORT]: Auto-detect cable type from board_sn here
        # (check for 'FFH' vs 'FBH' in serial number, like run_bert.py does)
        # and pass cable_type to id_ADS124 so it uses the correct pin config.
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
