from context import ROOT_DIR

import csv
import os

def getAntipatterns(systemName, antipattern):
	assert antipattern in ['god_class', 'feature_envy'], antipattern + ' not valid antipattern name. Choose either "god_class" or "feature_envy"'

	apFile = os.path.join(ROOT_DIR, 'data', 'antipatterns', systemName, antipattern + '.txt')
	with open(apFile, 'r') as file:
		return file.read().splitlines()

def getEntities(systemName, antipattern):
	assert antipattern in ['god_class', 'feature_envy'], antipattern + ' not valid antipattern name. Choose either "god_class" or "feature_envy"'

	metricFile = os.path.join(ROOT_DIR, 'data', 'metric_files', systemName, antipattern, 'commit_0.csv')
	with open(metricFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')

		if antipattern == 'god_class':
			return [row['Class'] for row in reader]
		else:
			return [row['Method'] + ';' + row['Class'] for row in reader]


