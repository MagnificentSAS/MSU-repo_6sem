"""This is good func."""

import calendar
import sys

def cool_func(year, mon):
	"""Func makes good table for calendar.

	:param year: year for cal
	:param mon: month for cal
	:return: rst table
	"""
	cal_strs = calendar.month(theyear=year, themonth=mon).split("\n")
	cal_strs[0] = ".. table:: " + cal_strs[0].strip()
	cal_strs_new = []

	frst = cal_strs[2].split()

	cal_strs[2] = " ".join(["\\ "] * (7 - len(frst)) + frst)

	pos = 1
	cal_strs_new.append("MONTH")
	cal_strs_new.append("=====")
	cal_strs_new.append("")
	cal_strs_new.append(cal_strs[0])
	cal_strs_new.append("")

	for i in range(2, len(cal_strs) + 3):
	    if i == 2 or i == 4 or i == len(cal_strs) + 2:
	        cal_strs_new.append("    == == == == == == ==")
	    else:
	        cal_strs_new.append("    " + cal_strs[pos])
	        pos += 1

	return "\n".join(cal_strs_new)

if __name__ == "__main__":
	year = int(sys.argv[1])
	mon = int(sys.argv[2])
	print(cool_func(year, mon))
