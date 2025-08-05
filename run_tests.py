#!/usr/bin/python

import sys

board_id = sys.argv[1]

from wagon_rtd import gen_resist_test
from wagon_rtd import id_resist_test
from run_iic_check import IIC_Check
from run_bert_tmp import BERT
from multiprocessing import Pipe

print("Starting")
c1, c2 = Pipe()

test_info = {'board_sn': 'FlexCable_{}'.format(board_id), 'tester': "Bryan"}

#print("Running General Resistance")
#gen_resist_test(c1, **test_info)
print("Running ID Resistance Check")
id_resist_test(c1, **test_info)
#print("Running IIC Check")
#IIC_Check(c1, **test_info)
print("Running BERT")
print()
BERT(c1, **test_info) 

print("All tests done")
