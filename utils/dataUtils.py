from context import ROOT_DIR

import csv
import os

def getGCEntities(systemName):
	metricFile = os.path.join(ROOT_DIR, 'data/metric_files/god_class/' + systemName + '/commit0.csv')

	with open(metricFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')

		return [row['Class'] for row in reader]

def getFEEntities(systemName):
	metricFile = os.path.join(ROOT_DIR, 'data/metric_files/feature_envy/' + systemName + '/commit0.csv')

	with open(metricFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')

		return [row['Method'] + ';' + row['TargetClass'] for row in reader]

def getAntipatterns(systemName, antipattern):
	apFile = os.path.join(ROOT_DIR, 'data/antipatterns/' + antipattern + '/' + systemName + '.txt')

	with open(apFile, 'r') as file:
		return file.read().splitlines()
