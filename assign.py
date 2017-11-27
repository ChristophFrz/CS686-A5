# -*- coding: utf-8 -*-
"""
Created on Thu Jun 01 08:57:52 2017

"""
import math	


def read_lotData(full_path_instance):
    
    data = []
    inputf = open(full_path_instance)
    for line in inputf:
    	input_line = line.split(",")
    	# convert string to integer
    	for i in range(len(input_line)-1):
    		input_line[i] = float(input_line[i])

    	data.append(input_line)
    inputf.close()
    return data

def get_unique_values(data, attribute_number):
	values = []

	for i in range(len(data)):
		if data[i][attribute_number] not in values:
			values.append(data[i][attribute_number])

	values = sorted(values)
	return values

def get_thresholds(unique_values):
	thresholds = []
	for i in range(len(unique_values)-1):
		mean = (unique_values[i] + unique_values[i+1])/2
		thresholds.append(mean)
	return thresholds

def MODE(examples):
	count_h = 0;
	count_c = 0;
	for i in range(len(examples)):
		if examples[i][16].find("healthy") != -1:
			count_h += 1
		else:
			count_c += 1

	if count_c >= count_h:
		return "colic.\\n"
	else:
		return "healty.\\n"

def calculate_entropy(n,p):
	if n != 0:
		I_partOne = - (n / (n+p)) * math.log((n / (n+p)), 2)
	else:
		I_partOne = 0

	if p != 0:
		I_partTwo = - (p / (n+p)) * math.log((p / (n+p)), 2)
	else:
		I_partTwo = 0
	I =  I_partOne + I_partTwo
	return I

def calculate_IG(current_n, current_p, list_poss_n, list_poss_p):
	# list_poss should contain two elements
	# have a threshold that devides the examples into two sets
	# each set has an indvidual number of n and p
	I = calculate_entropy(current_n, current_p)
	remainder = 0
	for i in range(len(list_poss_n)):
		remainder += ((list_poss_n[i]+list_poss_p[i])/(current_p+current_n))*calculate_entropy(list_poss_n[i], list_poss_p[i])

	IG = I - remainder
	return IG



def get_best_attribute(examples, dict_thresholds, attributes):
	# examples is a reduced version of data or has to be reduced according to the thresholds of attributes
	# attributes is reduced too

	# get the number of current p and n
	current_n, current_p = 0, 0
	for i in range(len(examples)):
		#if examples[i][16] == "healthy\.":
		if examples[i][16].find("healthy") != -1:
			current_n += 1
		else:
			current_p += 1


	max_IG = -1
	best_attribute = -1
	best_threshold = -1

	for j in attributes:
		for threshold in dict_thresholds[j]:
			# pretend to sort according to attribute i and threshold
			list_poss_p, list_poss_n = [], []
			n0, n1, p0, p1 = 0, 0, 0, 0

			for i in range(len(examples)):
				
				if examples[i][j] <= threshold:
					#if examples[i][16] == "healthy\.":
					if examples[i][16].find("healthy") != -1:
						n0 += 1
					else:
						p0 += 1
				else:
					#if examples[i][16] == "healthy\.":
					if examples[i][16].find("healthy") != -1:
						n1 += 1
					else:
						p1 += 1

			# append values to lists
			list_poss_n.append(n0)
			list_poss_n.append(n1)
			list_poss_p.append(p0)
			list_poss_p.append(p1)

			# calculate IG

			IG = calculate_IG(current_n, current_p, list_poss_n, list_poss_p)

			if IG > max_IG or max_IG == -1:
				best_attribute = j
				best_threshold = threshold
				max_IG = IG

	return (best_attribute, best_threshold)

def check_same_classification(examples):
	same_classification = True
	classification = examples[0][16]
	for i in range(1,len(examples)):
		if examples[i][16] != classification:
			same_classification = False
			break

	return same_classification

def restrict_examples(examples, attribute, threshold, separation):
	restr_examples = []
	if separation == 0:
		for i in range(len(examples)):
			if examples[i][attribute] <= threshold:
				restr_examples.append(examples[i])
	else:
		for i in range(len(examples)):
			if examples[i][attribute] > threshold:
				restr_examples.append(examples[i])

	return restr_examples

def restrict_attributes(attributes, best_attribute):
	new_attributes = list(attributes)
	new_attributes.remove(best_attribute)
	return new_attributes


def DTL(examples, attributes, default, last_attribute, last_threshold, last_separation):


	if len(examples) == 0:
		subtree = {}
		subtree[(last_attribute, last_threshold, last_separation)] = default
		#print("Examples: ", examples)
		#print("Subtree: ", subtree)
		return subtree
	elif check_same_classification(examples) == True:
		subtree = {}
		subtree[(last_attribute, last_threshold, last_separation)] = examples[0][16]
		#print("Examples: ", examples)
		#print("Subtree: ", subtree)
		return subtree
	elif len(attributes) == 0:
		majority = MODE(examples)
		subtree = {}
		subtree[(last_attribute, last_threshold, last_separation)] = majority
		#print("Examples: ", examples)
		#print("Subtree: ", subtree)
		return subtree
	else:
		# create the thresholds for all attributes
		dict_thresholds = {}
		for a in attributes:
			values = get_unique_values(examples, a)
			thresholds = get_thresholds(values)
			dict_thresholds[a] = thresholds

		# get the best threshold and the corresponding attribute
		best_attribute, best_threshold = get_best_attribute(examples, dict_thresholds, attributes)

		# to distinguish between <= threshold and > threshold use separation
		separation = [0, 1]
		tree = {}
		for s in separation:
			majority = MODE(examples)
			new_examples = restrict_examples(examples, best_attribute, best_threshold, s)
			subtree = DTL(new_examples, restrict_attributes(attributes, best_attribute), majority, best_attribute, best_threshold, s)
			# add subtree to tree
			tree.update(subtree)
			# add new branch to tree
			

		tmp_tree = {}
		tmp_tree[(last_attribute, last_threshold, last_separation)] = best_attribute
		tree.update(tmp_tree)

		return tree


    
def main():
	# dictionary for the tree
	tree = {}

	# list with number of attributes
	attributes = [i for i in range(16)]

	full_path_instance = "horseTrain.txt"
	# read in data
	data = read_lotData(full_path_instance)


	tree = DTL(data, attributes, "error.", -1, -1, -1)

	print(tree)
	
	



main()

                   
                   
    