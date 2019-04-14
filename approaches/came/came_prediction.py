from context import ROOT_DIR, nnUtils

import numpy           as np
import tensorflow      as tf

import ast
import CAME
import csv
import os

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

def get_save_path(antipattern, history_length, net_number):
	models_dir = os.path.join(ROOT_DIR, 'approaches', 'came', 'trained_models', antipattern, 'hist_' + str(history_length))
	return os.path.join(models_dir, 'network' + str(net_number))

def get_optimal_parameters(antipattern, history_length):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'came_' + antipattern + '_' + str(history_length) + '.csv')

	with open(tuning_file, 'r') as file:
		reader = csv.DictReader(file, delimiter=';')

		for row in reader:
			if row['F-measure'] != 'nan':
				return {key:ast.literal_eval(row[key]) for key in row}

def getSmells(systemName, history_length):
	params = get_optimal_parameters('god_class', history_length)
	x = nnUtils.get_came_instances(systemName, 'god_class', history_length)

	# New graph
	tf.reset_default_graph()

	# Create model
	model = CAME.CAME(
		nb_metrics=x.shape[-1],
		history_length=history_length,
		filters=params['Filters'],
		kernel_sizes=params['Kernel'],
		pool_sizes=params['Pool'],
		dense_sizes=params['Dense'])

	# To restore a trained model
	saver = tf.train.Saver(max_to_keep=10)

	with tf.Session() as session:
		# Ensemble Prediction
		predictions = []
		for i in range(10):
			# Reload the variables into the TensorFlow graph.
			saver.restore(sess=session, save_path=get_save_path('god_class', history_length, i))

			# Perform forward calculation
			pred = session.run(model.inference, feed_dict={model.input_x: x})
			predictions.append(pred)
	  	
		return np.mean(np.array(predictions), axis=0)