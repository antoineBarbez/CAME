from context import ROOT_DIR, train_svm
from sklearn.model_selection import RandomizedSearchCV
from sklearn import svm

import argparse
import os

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("-n_fold", type=int, default=5)
	parser.add_argument("-n_test", type=int, default=100)
	return parser.parse_args()


if __name__ == "__main__":
	args = parse_args()

	# Create dataset
	data_x, data_y = train_svm.build_dataset(train_svm.training_systems, 'god_class')

	random_grid = {
		'C': [0.001, 0.01, 0.1, 1, 10, 100],
		'gamma': [0.001, 0.01, 0.1, 1, 10, 100],
		'kernel': ['linear', 'rbf', 'sigmoid']}

	svm_cross_validation = RandomizedSearchCV(
		estimator = svm.SVC(),
		param_distributions = random_grid, 
		n_iter = args.n_test, 
		cv = args.n_fold,
		verbose=2, 
		n_jobs = -1)

	svm_cross_validation.fit(data_x, data_y)
	best_params = svm_cross_validation.best_params_

	tuning_results_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'svm.csv')
	with open(tuning_results_file, 'w') as file:
		for key in best_params:
			file.write(str(key) + ';')
		file.write('\n')
		for key in best_params:
			file.write(str(best_params[key]) + ';')
