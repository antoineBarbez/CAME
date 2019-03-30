from context import ROOT_DIR, nnUtils, train_mlp, mlp

import tensorflow        as tf
import numpy             as np

import argparse
import os
import progressbar
import random
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

def parse_args():
	parser = argparse.ArgumentParser()
	parser.add_argument("antipattern", help="either 'god_class' or 'feature_envy'")
	parser.add_argument("-n_batch", type=int, default=1)
	parser.add_argument("-n_fold", type=int, default=5)
	parser.add_argument("-n_step", type=int, default=100)
	parser.add_argument("-n_test", type=int, default=200)
	return parser.parse_args()

def generateRandomHyperParameters():
	learning_rate = 10**-random.uniform(0.0, 2.5)
	beta = 10**-random.uniform(0.0, 2.5)
	gamma = random.randint(1, 10)
	nbLayer = random.randint(1, 3)
	
	layers = []
	minBound = 4
	maxBound = 140
	for _ in range(nbLayer):
		nb = random.randint(minBound, maxBound)
		layers.append(nb)
		maxBound = nb

	return learning_rate, beta, gamma, layers

def get_cross_validation_dataset(X, Y, fold_index, n_fold):
	folds_x, folds_y = nnUtils.split(X, Y, n_fold)
	x_train = np.empty(shape=[0, X.shape[-1]])
	y_train = np.empty(shape=[0, 1])
	for i in range(n_fold):
		if i != fold_index:
			x_train = np.concatenate((x_train, folds_x[i]), axis=0)
			y_train = np.concatenate((y_train, folds_y[i]), axis=0)

	return x_train, y_train, folds_x[fold_index], folds_y[fold_index]

if __name__ == "__main__":
	args = parse_args()

	data_x, data_y = train_mlp.build_dataset(train_mlp.training_systems, args.antipattern)
	data_x, data_y = nnUtils.shuffle(data_x, data_y)

	bar = progressbar.ProgressBar(maxval=args.n_test, \
		widgets=['Performing cross validation: ' ,progressbar.Percentage()])
	bar.start()

	output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'mlp_' + args.antipattern + '.csv')

	params = []
	perfs  = []
	for i in range(args.n_test):
		learning_rate, beta, gamma, layers = generateRandomHyperParameters()
		params.append([learning_rate, beta, gamma, layers])

		predictions = np.empty(shape=[0, 1])
		for j in range(args.n_fold):
			x_train, y_train, x_test, y_test = get_cross_validation_dataset(data_x, data_y, j, args.n_fold)

			# New graph
			tf.reset_default_graph()

			# Create model
			model = mlp.MLP(layers, nnUtils.get_nb_metric(args.antipattern))

			with tf.Session() as session:
				# Initialize the variables of the TensorFlow graph.
				session.run(tf.global_variables_initializer())

				train_mlp.train(
					session=session,
					model=model,
					x_train=x_train,
					y_train=y_train,
					num_step=args.n_step,
					num_batch=args.n_batch,
					start_lr=learning_rate,
					beta=beta,
					gamma=gamma,
					decay_step=1000,
					lr_decay=1.0)

				predictions = np.concatenate((predictions, session.run(model.inference, feed_dict={model.input_x: x_test})), axis=0)
		
		perfs.append(nnUtils.f_measure(predictions, data_y))
		indexes = np.argsort(np.array(perfs))
		with open(output_file_path, 'w') as file:
			file.write("Learning rate;Beta;Gamma;Layers;F-measure\n")
			for j in reversed(indexes):
				for k in range(len(params[j])):
					file.write(str(params[j][k]) + ';')
				file.write(str(perfs[j]) + '\n')
		bar.update(i+1)
	bar.finish()