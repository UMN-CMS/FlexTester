#!/usr/bin/python

import sys

board_id = sys.argv[1]

from wagon_rtd import id_resist_test
from run_iic_check import IIC_Check
from run_bert import BERT
from multiprocessing import Pipe

c1, c2 = Pipe()

test_info = {'board_sn': 'FlexCable_{}'.format(board_id), 'tester': "Billy"}

print()
print("RUNNING RESISTANCE TEST:")
print()
res_test = id_resist_test(c1, **test_info)
#print("Running IIC Check")
#IIC_Check(c1, **test_info)
print()
print("RUNNING BERT TEST:")
print()
bert_test = BERT(c1, **test_info) 

# Print final summary
print()
print("=" * 60)
print("  FINAL TEST SUMMARY -- {}".format(board_id))
print("=" * 60)
print()

# Resistance summary
res_data = res_test.results['data']
res_pass = res_test.results['pass']
criteria = res_data['passing_criteria']
print("Resistance Test: {}".format("PASS" if res_pass else "FAIL"))
print("{:<25} {:>12} {:>10}".format("Line", "Resistance", "Status"))
print("-" * 50)
for line, val in res_data['test_data']['wagon type chip'].items():
    status = "PASS" if criteria['min_resistance'] < val < criteria['max_resistance'] else "FAIL"
    print("{:<25} {:>8.2f} ohms {:>10}".format(line, val, status))
print("-" * 50)
print()

# BERT summary
bert_data = bert_test.results['data']
bert_pass = bert_test.results['pass']
bert_criteria = bert_data.get('passing_criteria', {})
min_eo = bert_criteria.get('min_fit_eo', 150)
max_mp_err = bert_criteria.get('max_midpoint_errors', 0)
print("BERT Test: {} (EO >= {}, Midpoint Errors <= {})".format("PASS" if bert_pass else "FAIL", min_eo, max_mp_err))
print("{:<25} {:>12} {:>10} {:>16} {:>8}".format("Link", "Eye Opening", "Midpoint", "Midpoint Errors", "Status"))
print("-" * 75)
for name, r in bert_data['test_data'].items():
    eo = r.get("Eye Opening", -999)
    mp = r.get("Midpoint", -999)
    mp_err = r.get("Midpoint Errors", -999)
    reasons = []
    if eo < min_eo:
        reasons.append("EO")
    if mp_err > max_mp_err:
        reasons.append("MpErr")
    status = "FAIL" if reasons else "PASS"
    print("{:<25} {:>12} {:>10} {:>16} {:>8}".format(name, eo, mp, mp_err, status))
print("-" * 75)
print()
print("All tests done")
