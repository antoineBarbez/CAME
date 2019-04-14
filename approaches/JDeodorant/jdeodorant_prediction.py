from context    import ROOT_DIR, dataUtils

import numpy as np

import os

def getSmells(systemName):
	classToIdxMap = {c:i for i, c in enumerate(dataUtils.getEntities(systemName, 'god_class'))}
	prediction = np.zeros((len(classToIdxMap), 1))

	JDGCFile = os.path.join(ROOT_DIR, 'approaches', 'JDeodorant', 'output', systemName + '.txt')
	with open(JDGCFile, 'r') as file:
		for line in file:
			className = line.split()[0]
			if className in classToIdxMap:
				prediction[classToIdxMap[className]][0] = 1.0

	return prediction
