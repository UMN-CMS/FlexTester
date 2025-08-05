#!/usr/bin/python3

'''
Utility class for running tests on wagon tester

This class assumes that your results dictionary stores only certain fields.
Make sure that you are syncronizing your return from the test function with that of the test class.
'''

import json
import os

class Test():
    
    def __init__(self, test_func, info_dict, conn, **kwargs):
#        print("Inside of Test.py.__init__")
        self.conn = conn
#        print("Below are the arguments passed from run_bert_tmp to Test.py")
#        print("test_func:", test_func)
#        print("info_dict:", info_dict)
#        print("conn:", self.conn)
#        print("**kwargs: output='BERT.csv', iskip=5, nbits=1e8, module=None, clock=True")
        self.conn.send("Initializing a test")

        # All information that should be provided from the GUI to every test
        try:
            self.name = info_dict['name']
            self.board_sn = info_dict['board_sn']
            self.tester = info_dict['tester']
        except:
            self.conn.send("Please provide the name of the test, board serial number, and tester name")
 
       # Info that will be provided from running the test
#        print("Calling self.run_test(test_func, **kwargs). This is another method in Test.py\n")
        self.passed, self.data = self.run_test(test_func, **kwargs)
#        print("self.passed:", self.passed)
#        print("self.data:", self.data)

        # Package up results into a dictionary for parsing into a JSON
        self.results = {'name': self.name, 'board_sn': self.board_sn, 'tester': self.tester, 'pass': self.passed, 'data': self.data}
#        print("Dumping Results")
        self.conn.send(self.dump_results())
        
        self.save_results()
#        print("Gets stuck here")
        self.send_results()
#        print("Sent")

    # Dump results in JSON format for uploading to the database
    def dump_results(self):
        # This used to conn.send("Dumping Results.") but that was clogging the pipe for the results.
        return json.dumps(self.results)

    # Save JSON file under <serial_number>_<test_name>.json
    def save_results(self):
        print("Saving the json files")
        save_path = "/home/HGCAL_dev/FlexTest/FlexCableTesting/jsons/"
        if not os.path.exists(save_path):
            os.makedirs(save_path)
        if not os.path.exists(os.path.join(save_path, self.name.replace(" ", ""))):
            os.makedirs(os.path.join(save_path, self.name.replace(" ", "")))
        self.conn.send("\nSaving results...\n")
        with open("{2}/{0}/{0}_{1}.json".format(self.name.replace(" ",""), self.board_sn, save_path), "w") as f:
            f.write(self.dump_results())

        f.close()

    # Get results as a python dictionary
    def get_results(self):
#        print("Getting the results as a python dictionary")
        self.conn.send(self.results)
        return self.results

    # Send results via the PUB Server
    def send_results(self):
        self.conn.send(self.dump_results())

    # Function for running your test, kwargs must agree with defined kwargs for your test
    # This function assumes that the output of the test will be the pass/fail condition (bool)
    # and a dictionary (of any depth) containing the extra data to store for the test
    def run_test(self, test_func, **kwargs):
#        print("Inside of the run_test method in Test.py")
#        print("Leaving Test.py and going back to the bert(self,**kwargs) method in run_bert_tmp.py\n")  
        self.conn.send("Running the test: run_test")
        return test_func(**kwargs)

