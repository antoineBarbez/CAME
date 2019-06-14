from context import ROOT_DIR, nnUtils, came

import tensorflow        as tf
import numpy             as np
import matplotlib.pyplot as plt

import argparse
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

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
	parser.add_argument("antipattern", help="either 'god_class' or 'feature_envy'")
	parser.add_argument("history_length", type=int)
	parser.add_argument("-lr", type=float)
	parser.add_argument("-beta", type=float)
	parser.add_argument("-gamma", type=int)
	parser.add_argument('-filters', nargs='+', type=int, default=[])
	parser.add_argument('-kernel_sizes', nargs='+', type=int, default=[])
	parser.add_argument('-pool_sizes', nargs='+', type=int, default=[])
	parser.add_argument('-dense_sizes', nargs='+', type=int)
	parser.add_argument("-n_batch", type=int, default=5)
	parser.add_argument("-n_net", type=int, default=10)
	parser.add_argument("-n_step", type=int, default=300)
	parser.add_argument("-decay_step", type=int, default=100)
	parser.add_argument("-lr_decay", type=float, default=0.5)
	return parser.parse_args()

def get_save_path(antipattern, history_length, net_number):
	models_dir = os.path.join(ROOT_DIR, 'approaches', 'came', 'trained_models', antipattern, 'hist_' + str(history_length))
	if not os.path.exists(models_dir):
			os.makedirs(models_dir)

	return os.path.join(models_dir, 'network' + str(net_number))

def build_dataset(systems, antipattern, history_length):
	X = np.empty(shape=[0, history_length, nnUtils.get_nb_metric(antipattern)])
	Y = np.empty(shape=[0, 1])
	for system in systems:
		X = np.concatenate((X, nnUtils.get_came_instances(system, antipattern, history_length)), axis=0)
		Y = np.concatenate((Y, nnUtils.get_labels(system, antipattern)), axis=0)

	return X, Y

def train(session, model, x_train, y_train, x_test, y_test, num_step, num_batch, start_lr, beta, gamma, decay_step, lr_decay):
	learning_rate = start_lr
	losses_train = []
	losses_test  = []
	for step in range(num_step):
		# Learning rate decay
		if (step%decay_step == 0) & (step>0):
			learning_rate = learning_rate*lr_decay

		shuffled_x, shuffled_y = nnUtils.shuffle(x_train, y_train)
		batch_x, batch_y = nnUtils.split(shuffled_x, shuffled_y, num_batch)
		for i in range(num_batch):
			feed_dict_train = {
						model.input_x: batch_x[i],
						model.input_y: batch_y[i],
						model.learning_rate:learning_rate/num_batch,
						model.beta:beta,
						model.gamma:gamma}

			session.run(model.learning_step, feed_dict=feed_dict_train)

		loss_train = session.run(model.loss, feed_dict={model.input_x:x_train, model.input_y:y_train, model.gamma:gamma})
		loss_test  = session.run(model.loss, feed_dict={model.input_x:x_test, model.input_y:y_test, model.gamma:gamma})
		losses_train.append(loss_train)
		losses_test.append(loss_test)
	return losses_train, losses_test

def cool_plot(losses_train, losses_test):
    plt.figure()
    mean_train = np.mean(losses_train, axis=0)
    mean_test = np.mean(losses_test, axis=0)
    percentile90_train = np.percentile(losses_train, 90, axis=0)
    percentile90_test  = np.percentile(losses_test, 90, axis=0)
    percentile10_train = np.percentile(losses_train, 10, axis=0)
    percentile10_test = np.percentile(losses_test, 10, axis=0)
    plt.grid()

    plt.fill_between(range(len(losses_train[0])), percentile90_train,
                     percentile10_train, alpha=0.2,
                     color="r")
    plt.fill_between(range(len(losses_test[0])), percentile90_test,
                     percentile10_test, alpha=0.2,
                     color="g")
    plt.plot(range(len(losses_train[0])), mean_train, color="r")
    plt.plot(range(len(losses_test[0])), mean_test, color="g")
    plt.show()

if __name__ == "__main__":
	args = parse_args()

	# Create dataset
	x_train, y_train = build_dataset(training_systems, args.antipattern, args.history_length)
	x_test,  y_test  = build_dataset(test_systems, args.antipattern, args.history_length)

	tf.reset_default_graph()

	# Create model
	model = came.CAME(
		nb_metrics=x_train.shape[-1],
		history_length=args.history_length,
		filters=args.filters,
		kernel_sizes=args.kernel_sizes,
		pool_sizes=args.pool_sizes,
		dense_sizes=args.dense_sizes)

	# To save and restore a trained model
	saver = tf.train.Saver(max_to_keep=args.n_net)

	with tf.Session() as session:
		# Train several neural networks
		all_losses_train = []
		all_losses_test  = []
		for i in range(args.n_net):
			print('Training Neural Network :' + str(i+1))

			# Initialize the variables of the TensorFlow graph.
			session.run(tf.global_variables_initializer())

			# Train the model
			losses_train, losses_test = train(
				session=session,
				model=model,
				x_train=x_train,
				y_train=y_train,
				x_test=x_test,
				y_test=y_test,
				num_step=args.n_step,
				num_batch=args.n_batch,
				start_lr=args.lr,
				beta=args.beta,
				gamma=args.gamma,
				decay_step=args.decay_step,
				lr_decay=args.lr_decay)

			all_losses_train.append(losses_train)
			all_losses_test.append(losses_test)

			# Save the model
			saver.save(sess=session, save_path=get_save_path(args.antipattern, args.history_length, i))

		# Print performances
		pre = []
		rec = []
		f_m = []
		for i in range(args.n_net):
			# Reload the variables into the TensorFlow graph.
			saver.restore(sess=session, save_path=get_save_path(args.antipattern, args.history_length, i))

			prediction = session.run(model.inference, feed_dict={model.input_x: x_test})

			pre.append(nnUtils.precision(prediction, y_test))
			rec.append(nnUtils.recall(prediction, y_test))
			f_m.append(nnUtils.f_measure(prediction, y_test))

		print('')
		print('OVERALL')
		print('Precision :' + str(np.mean(pre)))
		print('Recall    :' + str(np.mean(rec)))
		print('F-Mesure  :' + str(np.mean(f_m)))

		# Plot learning curve
		cool_plot(all_losses_train, all_losses_test)
		