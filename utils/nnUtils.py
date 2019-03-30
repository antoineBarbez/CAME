from context import ROOT_DIR
from sklearn.preprocessing import StandardScaler

import numpy     as np

import csv
import dataUtils
import entityUtils
import os
import random

### EVALUATION ####

def detected(output):
	return np.sum((output > 0.5).astype(float))

def positive(labels):
	return np.sum(labels)

def true_positive(output, labels):
	return np.sum((output + labels > 1.5).astype(float))

def precision(output, labels):
	return true_positive(output, labels)/detected(output)

def recall(output, labels):
	return true_positive(output, labels)/positive(labels)

def f_measure(output, labels):
	p = precision(output, labels)
	r = recall(output, labels)

	return 2*p*r/(p+r)


### UTILS ###

def shuffle(instances, labels):
	assert len(instances) == len(labels), 'instances and labels must have the same number of elements'

	idx = range(len(instances))
	random.shuffle(idx)

	x = np.array([instances[i] for i in idx])
	y = np.array([labels[i] for i in idx])
	
	return x, y

def split(instances, labels, nb_batch):
	assert len(instances) == len(labels), 'instances and labels must have the same number of elements' 
	
	len_batch = len(instances)//nb_batch
	sections  = [(i+1)*len_batch for i in range(nb_batch-1)]

	return np.split(instances, sections), np.split(labels, sections)

def get_nb_metric(antipattern):
	if antipattern == 'god_class':
		return 7

	if antipattern == 'feature_envy':
		return 13 


###   GETTERS   ###

def get_labels(systemName, antipattern):
	entities = dataUtils.getEntities(systemName, antipattern)
	if antipattern == 'feature_envy':
		entities = map(lambda x: entityUtils.normalizeMethodName(x.split(';')[0]) + ';' + x.split(';')[1], entities)

	antipatterns = dataUtils.getAntipatterns(systemName, antipattern)

	labels = []
	for entity in entities:
		if entity in antipatterns:
			labels.append([1.])
		else:
			labels.append([0.])

	return np.array(labels)

def get_instances(systemName, antipattern):
	metricFile = os.path.join(ROOT_DIR, 'data', 'metric_files', systemName, antipattern, 'commit_0.csv')

	with open(metricFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')
		instances =  np.array([[float(row[key]) for key in row if (key != 'Class') & (key != 'Method')] for row in reader])
		
		# Normalization
		scaler = StandardScaler()
		scaler.fit(instances)
		return scaler.transform(instances)

def get_came_instances(systemName, antipattern, history_length):
	entities = dataUtils.getEntities(systemName, antipattern)
	instances = np.zeros((len(entities), history_length, get_nb_metric(antipattern)))
	for j in range(history_length):
		metricFile = os.path.join(ROOT_DIR, 'data', 'metric_files', systemName, antipattern, 'commit_' + str(j) + '.csv')
		if os.path.exists(metricFile):
			with open(metricFile, 'rb') as csvfile:
				reader = csv.DictReader(csvfile, delimiter=';')
				for i, row in enumerate(reader):
					k = 0
					for key in reader.fieldnames:
						if (key != 'Class') & (key != 'Method'):
							instances[i, j, k] = float(row[key])
							k += 1
		else:
			break

	# Normalization
	scaler = StandardScaler()
	scaler.fit(instances[:,0,:])

	for i in range(len(entities)):
		instances[i, :, :] = scaler.transform(instances[i, :, :])
	
	return instances
