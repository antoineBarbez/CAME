from context import ROOT_DIR, nnUtils
from sklearn import svm

import numpy as np

import argparse
import os
import pickle


training_systems = [
	'android-frameworks-opt-telephony',
	'apache-ant',
	'apache-lucene',
	'argouml',
	'xerces'
]

test_systems = [
	'android-platform-support',
	'jedit',
	'apache-tomcat'
]

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-n_model", type=int, default=10)
	parser.add_argument("-kernel",  default='rbf')
	parser.add_argument("-C", type=float, default=10.0)
	parser.add_argument("-gamma", type=float, default=0.01)
	return parser.parse_args()


def build_dataset(systems, antipattern):
	X = []
	Y = []
	for system in systems:
		X += nnUtils.get_instances(system, antipattern).tolist()
		Y += np.reshape(nnUtils.get_labels(system, antipattern), -1).tolist()

	return X, Y

def get_save_path(model_number):
	return os.path.join(ROOT_DIR, 'approaches', 'svm', 'trained_models', 'svm_' + str(model_number) + '.pickle')

if __name__ == "__main__":
	args = parse_args()

	# Create dataset
	x_train, y_train = build_dataset(training_systems, 'god_class')
	x_test, y_test = build_dataset(test_systems, 'god_class')

	for i in range(args.n_model):
		clf = svm.SVC(C=args.C, gamma=args.gamma, kernel=args.kernel, probability=True)
		clf = clf.fit(x_train, y_train)

		with open(get_save_path(i), 'wb') as save_file:
			pickle.dump(clf, save_file)

