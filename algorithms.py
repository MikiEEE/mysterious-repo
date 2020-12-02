import numpy as np
import math
from models.Battery import Battery
from Errors import Max_Discharge

def calculate_new_step(current_step):
	power = int(math.log10(current_step))
	power -= 1
	return 10**power


def find_threshold_recursive(data,kwh_storage,precision=1,floor=None,ceiling=None,step=None):
	
	if kwh_storage  < 0:
		return -1
	
	if not ceiling:
		ceiling = np.amax(data)
	if not floor:
		floor = 0
	if not step:
		step = 10 ** int(math.log10(ceiling))

	answer = -1
	for threshold in np.arange(floor,ceiling,step):
		usage = int()
		battery = Battery(kwh_storage,kwh_storage,threshold)
		for kwh_usage in data:
			try:
				charge = battery.charge(kwh_usage)
				discharge = battery.discharge(kwh_usage)
				usage += 1
			except Max_Discharge as e:
				break
		if usage == len(data):
			answer = threshold
			break
	if step > precision:
		floor = threshold - step
		step = calculate_new_step(step)
		return find_threshold_recursive(data,kwh_storage,precision,floor,ceiling,step)
	else:
		return answer


def find_threshold_iterative(data,kwh_storage,precision=1,floor=None,ceiling=None):
	
	if kwh_storage < 0:
		return -1

	if not floor:
		floor = 0
	if not ceiling:
		ceiling = np.amax(data)
	step = int(math.log10(ceiling))
	step = 10**(step)
	answer = -1
	while step >= precision: # x log(ceiling) - log(precision)
		for threshold in np.arange(floor,ceiling,step): #x 10
			usage = int()
			battery = Battery(kwh_storage,kwh_storage,threshold)
			for kwh_usage in data: #x n
				try:
					charge = battery.charge(kwh_usage)
					discharge = battery.discharge(kwh_usage)
					usage += 1
				except Max_Discharge as e:
					break
			if usage == len(data):
				answer = threshold
				break
		if answer != -1:
			floor = answer - step
		step = calculate_new_step(step)	
	return answer


def find_minimum_capacity_recursive(data,threshold,c_precision=1,t_precision=1,value=None,step=None):
	
	if threshold < 0:
		return -1

	if not value:
		value = 0
	if not step:
		step = 10 ** int(math.log10(sum(data)))

	kwh_storage = value

	answer = find_threshold_recursive(data,kwh_storage,t_precision)
	while answer == -1 or answer > threshold:
		kwh_storage += step
		answer = find_threshold_recursive(data,kwh_storage,t_precision)
	
	if step > c_precision:
		start = kwh_storage - step
		step = calculate_new_step(step)
		return find_minimum_capacity_recursive(data,threshold,c_precision,t_precision,start,step)
	else:
		return kwh_storage


def find_minimum_capacity_iterative(data,threshold,c_precision=1,t_precision=1):
	
	if threshold < 0: 
		return -1
	
	step = 10**int(math.log10(sum(data)))

	kwh_storage = 0
	temp = -1

	cont = True
	while cont:#X log(sum) - log(tolerance)
		temp = find_threshold_iterative(data,kwh_storage,t_precision) 
		while temp == -1 or temp > threshold: #X10
			kwh_storage += step
			temp = find_threshold_iterative(data,kwh_storage,t_precision) #klog(n)
		if step > c_precision:
			kwh_storage = kwh_storage - step
			step = calculate_new_step(step)
		else:
			cont = False
	return kwh_storage

