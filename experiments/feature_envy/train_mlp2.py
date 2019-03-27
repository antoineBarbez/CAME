from context import ROOT_DIR, nnUtils, mlp

import tensorflow        as tf
import numpy             as np
import matplotlib.pyplot as plt

import os


if __name__ == "__main__":
	os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

	tf.reset_default_graph()

	training_systems = ['xerces', 'apache-lucene', 'apache-ant', 'argouml', 'android-frameworks-opt-telephony']
	test_systems = ['apache-tomcat', 'jedit', 'android-platform-support']

	#constants
	starter_learning_rate = 0.05
	learning_rate_decay   = 0.7
	decay_steps           = 100
	dropout_keep_prob     = 1.0
	beta                  = 0.05
	num_steps             = 400
	num_networks          = 1

	layers = [30, 10]

	# Create datasets
	x_train = []
	c_train = []
	y_train = []
	for systemName in training_systems:
		x = nnUtils.getFEMLPInstances(systemName)
		y = nnUtils.getFELabels(systemName)
		c = nnUtils.getSystemConstants(systemName)
		x_train.append(x)
		y_train.append(y)
		c_train.append(c)
		
	x_test = []
	c_test = []
	y_test = []
	for systemName in test_systems:
		x = nnUtils.getFEMLPInstances(systemName)
		y = nnUtils.getFELabels(systemName)
		c = nnUtils.getSystemConstants(systemName)
		x_test.append(x)
		y_test.append(y)
		c_test.append(c)


	# Model constants
	input_size     = 8
	constants_size = 2
	output_size    = 2

	# Create model
	model = mlp.MLP(layers, input_size, constants_size)

	# To save and restore a trained model
	saver = tf.train.Saver()

	session = tf.Session()

	# Initialize the variables of the TensorFlow graph.
	session.run(tf.global_variables_initializer())
	
	learning_rate = starter_learning_rate

	learning_rates = []
	losses_train   = []
	losses_test    = []
	for step in range(num_steps):
		# Learning rate decay
		if (step%decay_steps == 0) & (step>1):
			learning_rate = learning_rate*learning_rate_decay

		learning_rates.append(learning_rate)

		#Imballanced batch trainning
		l_train = []
		for i in range(len(x_train)):
			constants, batch_x, batch_y = c_train[i], x_train[i], y_train[i]
			feed_dict_train = {
						model.input_x: batch_x,
						model.input_y: batch_y,
						model.constants: constants,
						model.dropout_keep_prob:dropout_keep_prob,
						model.learning_rate:learning_rate,
						model.beta:beta}

			session.run(model.learning_step, feed_dict=feed_dict_train)

			l = session.run(model.loss, feed_dict=feed_dict_train)
			l_train.append(l)
		mean_l_train = np.mean(np.array(l_train))
		losses_train.append(mean_l_train)


	# Print performances of the ensemble model on test set
	pre = []
	rec = []
	f_m = []
	acc = []
	for i in range(len(x_test)):
		feed_dict_test = {model.input_x: x_test[i], model.constants: c_test[i], model.dropout_keep_prob:1.0}
		output = session.run(model.inference, feed_dict=feed_dict_test)

		p = nnUtils.precision(output, y_test[i]).eval(session=session)
		r = nnUtils.recall(output, y_test[i]).eval(session=session)
		f = nnUtils.f_measure(output, y_test[i]).eval(session=session)
		a = nnUtils.accuracy(output, y_test[i]).eval(session=session)

		print(test_systems[i])
		print('P :' + str(p))
		print('R :' + str(r))
		print('F :' + str(f))
		print('A :' + str(a))
		print('')
			
		pre.append(p)
		rec.append(r)
		f_m.append(f)
		acc.append(a)

	session.close()

	print('')
	print('MEAN')
	print('Precision :' + str(np.mean(np.array(pre))))
	print('Recall    :' + str(np.mean(np.array(rec))))
	print('F-Mesure  :' + str(np.mean(np.array(f_m))))
	print('Accuracy  :' + str(np.mean(np.array(acc))))
	print('')

	# Plot learning curves
	plt.plot(range(num_steps), losses_train, range(num_steps), learning_rates)
	plt.show()