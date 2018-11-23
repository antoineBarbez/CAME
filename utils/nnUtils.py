from context import ROOT_DIR
from sklearn.preprocessing import StandardScaler

import numpy     as np
import tensorflow as tf

import csv
import dataUtils
import entityUtils
import os

### EVALUATION ####
def true_positive(output, labels):
	tp = tf.cast(tf.equal(tf.argmax(output,1) + tf.argmax(labels,1), 0), tf.float32)

	return tp

def precision(output, labels):
	tp = true_positive(output, labels)
	detected = tf.cast(tf.equal(tf.argmax(output,1), 0), tf.float32)

	return tf.reduce_sum(tp)/tf.reduce_sum(detected)

def recall(output, labels):
	tp = true_positive(output, labels)
	positive = tf.cast(tf.equal(tf.argmax(labels,1), 0), tf.float32)

	return tf.reduce_sum(tp)/tf.reduce_sum(positive)

def f_measure(output, labels):
	prec = precision(output, labels)
	rec = recall(output, labels)

	return 2*prec*rec/(prec+rec)

def accuracy(output, labels):
	correct_prediction = tf.equal(tf.argmax(output, 1), tf.argmax(labels,1))

	return tf.reduce_mean(tf.cast(correct_prediction, tf.float32))


###   LABELS GETTERS   ###

def getFELabels(systemName):
	entities = dataUtils.getFEEntities(systemName)

	labels = []
	true = dataUtils.getAntipatterns(systemName, 'feature_envy')
	for entity in entities:
		normalizedEntity = entityUtils.normalizeMethodName(entity.split(';')[0]) + ';' + entity.split(';')[1]
		if normalizedEntity in true:
			labels.append([1, 0])
		else:
			labels.append([0, 1])

	return np.array(labels)

def getGCLabels(systemName):
	entities = dataUtils.getGCEntities(systemName)

	labels = []
	true = dataUtils.getAntipatterns(systemName, 'god_class')
	for entity in entities:
		if entity in true:
			labels.append([1, 0])
		else:
			labels.append([0, 1])

	return np.array(labels)


###   INSTANCES GETTERS FOR MLP   ###

def getGCMLPInstances(systemName):
	metricFile = os.path.join(ROOT_DIR, 'data/metric_files/god_class/' + systemName + '/commit0.csv')

	instances = []
	with open(metricFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')

		for row in reader:
			instance = []
			instance.append(float(row['LOC']))
			instance.append(float(row['NMD']))
			instance.append(float(row['NAD']))
			instance.append(float(row['LCOM5']))
			instance.append(float(row['DataClass']))
			instance.append(float(row['ATFD']))
			instances.append(instance)

	instances = np.array(instances)

	# Batch normalization
	scaler = StandardScaler()
	scaler.fit(instances)
	rescaledInstances = scaler.transform(instances)
	
	return rescaledInstances


def getFEMLPInstances(systemName):
	metricFile = os.path.join(ROOT_DIR, 'data/metric_files/feature_envy/' + systemName + '/commit0.csv')

	instances = []
	with open(metricFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')

		for row in reader:
			instance = []
			instance.append(float(row['ATFD']))
			instance.append(float(row['ATSD']))
			instance.append(float(row['FDP']))
			instance.append(float(row['DIST_EC']))
			instance.append(float(row['DIST_TC']))
			instance.append(float(row['LOC_M']))
			instance.append(float(row['LOC_EC']))
			instance.append(float(row['LOC_TC']))
			instances.append(instance)
	
	instances = np.array(instances)

	# Batch normalization
	scaler = StandardScaler()
	scaler.fit(instances)
	rescaledInstances = scaler.transform(instances)
	
	return rescaledInstances


### INSTANCES GETTERS FOR CAME   ###

def getGCCAMEInstances(systemName, maxSize=1000):
	entities = dataUtils.getGCEntities(systemName)
	instances = np.zeros((len(entities), maxSize + 1, 6))
	for j in range(maxSize):
		metricFile = os.path.join(ROOT_DIR, 'data/metric_files/god_class/' + systemName + '/commit' + str(j) + '.csv')
		if os.path.exists(metricFile):
			with open(metricFile, 'rb') as csvfile:
				reader = csv.DictReader(csvfile, delimiter=';')
				
				for i, row in enumerate(reader):
					instances[i, j, 0] = float(row['LOC'])
					instances[i, j, 1] = float(row['NMD'])
					instances[i, j, 2] = float(row['NAD'])
					instances[i, j, 3] = float(row['LCOM5'])
					instances[i, j, 4] = float(row['DataClass'])
					instances[i, j, 5] = float(row['ATFD'])
		else:
			break


	# Batch normalization
	scaler = StandardScaler()
	scaler.fit(instances[:,0,:])

	for i in range(len(entities)):
		instances[i, :, :] = scaler.transform(instances[i, :, :])
	
	return instances

def getFECAMEInstances(systemName, maxSize=1000):
	entities = dataUtils.getFEEntities(systemName)
	instances = np.zeros((len(entities), maxSize + 1, 8))
	for j in range(maxSize):
		metricFile = os.path.join(ROOT_DIR, 'data/metric_files/feature_envy/' + systemName + '/commit' + str(j) + '.csv')
		if os.path.exists(metricFile):
			with open(metricFile, 'rb') as csvfile:
				reader = csv.DictReader(csvfile, delimiter=';')
				
				for i, row in enumerate(reader):
					instances[i, j, 0] = float(row['ATFD'])
					instances[i, j, 1] = float(row['ATSD'])
					instances[i, j, 2] = float(row['FDP'])
					instances[i, j, 3] = float(row['DIST_EC'])
					instances[i, j, 4] = float(row['DIST_TC'])
					instances[i, j, 5] = float(row['LOC_M'])
					instances[i, j, 6] = float(row['LOC_EC'])
					instances[i, j, 7] = float(row['LOC_TC'])
		else:
			return instances
	
	return instances


###   SYSTEMS CONSTANTS   ###

def getSystemConstants(systemName):
	systemConstantsMap = {
		'android-frameworks-opt-telephony': [190, 98],
		'android-platform-support': [104, 195],
		'apache-ant': [755, 6397],
		'apache-derby': [1022, 1338],
		'apache-jena': [686, 403],
		'apache-log4j': [313, 734],
		'apache-lucene': [160, 429],
		'apache-tomcat': [1005, 3289],
		'apache-velocity': [164, 1241],
		'argouml': [1246, 5559],
		'javacc': [155, 315],
		'jedit': [437, 1181],
		'jgraphx': [177, 117],
		'jgroups': [276, 3138],
		'jhotdraw': [549, 503],
		'jspwiki': [330, 3993],
		'mongodb': [111, 909],
		'pmd': [815, 4656],
		'xerces': [658, 3453]
	}

	systemConstants = np.array([systemConstantsMap[s] for s in systemConstantsMap]).astype(float)

	# Normalization
	scaler = StandardScaler()
	scaler.fit(systemConstants)

	constants = [systemConstantsMap[systemName]]
	return scaler.transform(constants)[0]


if __name__ == '__main__':
	print(getGCCAMEInstances('apache-derby')[0])

