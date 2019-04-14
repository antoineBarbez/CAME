from __future__ import division
from context    import ROOT_DIR, dataUtils

import numpy as np

import csv
import os

def getSmells(systemName):
	classToIdxMap = {c:i for i, c in enumerate(dataUtils.getEntities(systemName, 'god_class'))}
	prediction = np.zeros((len(classToIdxMap), 1))

	decorMetricsFile = os.path.join(ROOT_DIR, 'approaches', 'DECOR', 'output', systemName + '.csv')
	with open(decorMetricsFile, 'rb') as csvfile:
		reader = csv.DictReader(csvfile, delimiter=';')
		for row in reader:
			nmdNad      = float(row['NMD+NAD'])
			nmdNadBound = float(row['nmdNadBound'])
			lcom5       = float(row['LCOM5'])
			lcom5Bound  = float(row['lcom5Bound'])
			cc          = int(row['ControllerClass'])
			nbDataClass = int(row['nbDataClass'])

			if (nbDataClass > 0) & (row['ClassName'] in classToIdxMap):
				if nmdNad/nmdNadBound > 1:
					prediction[classToIdxMap[row['ClassName']]][0] = 1.0

				elif lcom5/lcom5Bound > 1:
					prediction[classToIdxMap[row['ClassName']]][0] = 1.0 

				elif cc == 1:
					prediction[classToIdxMap[row['ClassName']]][0] = 1.0

	return prediction