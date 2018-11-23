from context import ROOT_DIR, mlp, nnUtils

import tensorflow        as tf
import numpy             as np
import matplotlib.pyplot as plt

import math
import os
import progressbar
import random



def generateRandomHyperParameters():
	beta = 10**-random.uniform(0.0, 2.5)
	learning_rate = 10**-random.uniform(0.0, 2.5)
	nbLayer = random.randint(2,3)
	dropout = random.randint(1, 2)*0.5
	
	layers = []
	minBound = 4
	maxBound = 140
	for _ in range(nbLayer):
		nb = random.randint(minBound, maxBound)
		layers.append(nb)
		maxBound = nb

	return learning_rate, beta, layers, dropout



# Train and evaluate
def trainAndTest(learning_rate, beta, layers, dropout):
	# New graph
	tf.reset_default_graph()

	# Create model
	model = mlp.MLP(layers, input_size, constants_size)
	session = tf.Session()

	# Initialize the variables of the TensorFlow graph.
	session.run(tf.global_variables_initializer())

	for step in range(num_steps):
		#Imballanced batch trainning
		for i in range(len(x_train)):
			feed_dict_train = {
				model.input_x: x_train[i],
				model.input_y: y_train[i],
				model.constants: c_train[i],
				model.dropout_keep_prob:dropout,
				model.learning_rate:learning_rate,
				model.beta:beta}

			session.run(model.learning_step, feed_dict=feed_dict_train)

	#Perform forward calculation
	f_ms = []
	for i in range(len(x_test)):
		feed_dict_test = {
			model.input_x: x_test[i], 
			model.constants: c_test[i],
			model.dropout_keep_prob:1.0}
		output = session.run(model.inference, feed_dict=feed_dict_test)
		f_m = nnUtils.f_measure(output, y_test[i]).eval(session=session)
		if math.isnan(f_m):
			f_m = 0.0
		f_ms.append(f_m)

	session.close()
	return np.mean(np.array(f_ms))
			

if __name__ == "__main__":
	os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

	tf.reset_default_graph()

	fold1 = ['apache-derby', 'jspwiki', 'apache-velocity', 'android-frameworks-opt-telephony']
	fold2 = ['pmd', 'jhotdraw', 'apache-log4j', 'apache-lucene']
	fold3 = ['apache-ant', 'argouml', 'jgroups', 'javacc']
	fold4 = ['xerces', 'apache-jena', 'jgraphx', 'mongodb']
	
	folds = [fold1, fold2, fold3, fold4]

	#Constants
	num_tests      = 200
	num_steps      = 100
	num_networks   = 1

	input_size     = 8
	constants_size = 2
	output_size    = 2

		
	x_folds = []
	y_folds = []
	c_folds = []
	for fold in folds:
		x_fold = []
		y_fold = []
		c_fold = []
		for systemName in fold:
			x = nnUtils.getFEMLPInstances(systemName)
			y = nnUtils.getFELabels(systemName)
			c = nnUtils.getSystemConstants(systemName)
			x_fold.append(x)
			y_fold.append(y)
			c_fold.append(c)
		x_folds.append(x_fold)
		y_folds.append(y_fold)
		c_folds.append(c_fold)


	bar = progressbar.ProgressBar(maxval=num_tests, \
		widgets=['Performing cross validation: ' ,progressbar.Percentage()])
	bar.start()

	output_file_path = os.path.join(ROOT_DIR, 'experiments/feature_envy/tuning/outputs/mlp_cv_results.csv')


	params = []
	perfs  = []
	for i in range(num_tests):
		learning_rate, beta, layers, dropout = generateRandomHyperParameters()
		params.append([learning_rate, beta, layers, dropout])
		f_measures = []
		for j in range(4):
			x_train = list(x_folds)
			y_train = list(y_folds)
			c_train = list(c_folds)

			x_test = x_train.pop(j)
			y_test = y_train.pop(j)
			c_test = c_train.pop(j)

			x_train = [s for f in x_train for s in f]
			y_train = [s for f in y_train for s in f]
			c_train = [s for f in c_train for s in f]

			f_measure = trainAndTest(learning_rate, beta, layers, dropout)
			f_measures.append(f_measure)
		perfs.append(np.mean(np.array(f_measures)))
		args = np.argsort(np.array(perfs))

		F = open(output_file_path, 'w')
		F.write("Learning rate;Beta;Layers;Dropout;F-mesure\n")
		for k in reversed(args):
			F.write(str(params[k][0]) + ';' + str(params[k][1]) + ';' + str(params[k][2]) + ';' + str(params[k][3]) + ';' + str(perfs[k]) + '\n')
		F.close()
		bar.update(i+1)

	bar.finish()