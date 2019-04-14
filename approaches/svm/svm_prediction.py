from context import ROOT_DIR, nnUtils
from sklearn import svm

import numpy           as np

import ast
import csv
import os
import pickle

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

def get_save_path(model_number):
	return os.path.join(ROOT_DIR, 'approaches', 'svm', 'trained_models', 'svm_' + str(model_number) + '.pickle')


def getSmells(systemName):
	x = nnUtils.get_instances(systemName, 'god_class').tolist()

	# Ensemble Prediction
	predictions = []
	for i in range(10):
		with open(get_save_path(i), 'r') as file:
			clf = pickle.load(file)
			predictions.append(clf.predict(x))
  	
	return np.mean(np.array(predictions), axis=0)