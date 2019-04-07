from context import ROOT_DIR, nnUtils, train_came, came

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
	parser.add_argument("history_length", type=int)
	parser.add_argument("-n_fold", type=int, default=5)
	parser.add_argument("-n_step", type=int, default=100)
	parser.add_argument("-n_test", type=int, default=100)
	return parser.parse_args()

def generateRandomHyperParameters(history_length):
	learning_rate = 10**-random.uniform(0.0, 2.5)
	beta = 10**-random.uniform(0.0, 2.5)
	gamma = random.randint(1, 10)

	nb_filters    = []
	kernel_sizes  = []
	pool_sizes    = []
	nb_conv_layer = 0 if history_length <= 1 else random.randint(0,1) if history_length <= 10 else random.randint(1,2) if history_length <= 100 else 2
	for _ in range(nb_conv_layer):
		nb_filter   = random.randint(10,60)
		kernel_size = random.randint(2,4)
		pool_size   = random.choice([2, 5, 10]) if history_length <=100 else random.choice([5, 10, 15, 20])
		
		nb_filters.append(nb_filter)
		kernel_sizes.append(kernel_size)
		pool_sizes.append(pool_size)

	minBound = 4
	maxBound = 100
	dense_sizes = []
	nb_dense_layer = random.randint(1, 3)
	for _ in range(nb_dense_layer):
		dense_size = random.randint(minBound, maxBound)
		dense_sizes.append(dense_size)
		maxBound = dense_size

	return learning_rate, beta, gamma, nb_filters, kernel_sizes, pool_sizes, dense_sizes

def get_cross_validation_dataset(X, Y, fold_index, n_fold):
	folds_x, folds_y = nnUtils.split(X, Y, n_fold)
	x_train = np.empty(shape=[0, X.shape[1], X.shape[2]])
	y_train = np.empty(shape=[0, 1])
	for i in range(n_fold):
		if i != fold_index:
			x_train = np.concatenate((x_train, folds_x[i]), axis=0)
			y_train = np.concatenate((y_train, folds_y[i]), axis=0)

	return x_train, y_train, folds_x[fold_index], folds_y[fold_index]

def train(session, model, x_train, y_train, num_step, lr, beta, gamma):
	learning_rate = lr
	for step in range(num_step):
		feed_dict_train = {
					model.input_x: x_train,
					model.input_y: y_train,
					model.learning_rate:learning_rate,
					model.beta:beta,
					model.gamma:gamma}

		session.run(model.learning_step, feed_dict=feed_dict_train)

if __name__ == "__main__":
	args = parse_args()

	data_x, data_y = train_came.build_dataset(train_came.training_systems, args.antipattern, args.history_length)
	data_x, data_y = nnUtils.shuffle(data_x, data_y)

	bar = progressbar.ProgressBar(maxval=args.n_test, \
		widgets=['Performing cross validation: ' ,progressbar.Percentage()])
	bar.start()

	output_file_path = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'came_' + args.antipattern + '_' + str(args.history_length) + '.csv')

	params = []
	perfs  = []
	for i in range(args.n_test):
		learning_rate, beta, gamma, nb_filters, kernel_sizes, pool_sizes, dense_sizes = generateRandomHyperParameters(args.history_length)
		params.append([learning_rate, beta, gamma, nb_filters, kernel_sizes, pool_sizes, dense_sizes])

		predictions = np.empty(shape=[0, 1])
		for j in range(args.n_fold):
			x_train, y_train, x_test, y_test = get_cross_validation_dataset(data_x, data_y, j, args.n_fold)

			# New graph
			tf.reset_default_graph()
            
			# Create model
			model = came.CAME(
				nb_metrics=x_train.shape[-1],
				history_length=args.history_length,
				filters=nb_filters,
				kernel_sizes=kernel_sizes,
				pool_sizes=pool_sizes,
				dense_sizes=dense_sizes)
			

			with tf.Session() as session:
				# Initialize the variables of the TensorFlow graph.
				session.run(tf.global_variables_initializer())

				train(
					session=session,
					model=model,
					x_train=x_train,
					y_train=y_train,
					num_step=args.n_step,
					lr=learning_rate,
					beta=beta,
					gamma=gamma)

				predictions = np.concatenate((predictions, session.run(model.inference, feed_dict={model.input_x: x_test})), axis=0)
		
		perfs.append(nnUtils.f_measure(predictions, data_y))
		indexes = np.argsort(np.array(perfs))
		with open(output_file_path, 'w') as file:
			file.write("Learning rate;Beta;Gamma;Filters;Kernel;Pool;Dense;F-measure\n")
			for j in reversed(indexes):
				for k in range(len(params[j])):
					file.write(str(params[j][k]) + ';')
				file.write(str(perfs[j]) + '\n')
		bar.update(i+1)
	bar.finish()