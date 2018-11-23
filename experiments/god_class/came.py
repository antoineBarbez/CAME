from context import ROOT_DIR, nnUtils, came

import numpy           as np
import tensorflow      as tf

import os

os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

# This module is used to detect God Classes in new systems using the pre-trained model.

num_networks   = 5

# Model constants
nb_metrics      = 6
nb_filters1     = 40
pool_size1      = 20
nb_filters2     = 20
kernel_size2    = 3
pool_size2      = 20
dense_shape     = [11, 8]

test_systems = ['apache-tomcat', 'jedit', 'android-platform-support']

def get_save_path(net_number):
	return os.path.join(ROOT_DIR, 'neural_networks/came/trained_models/god_class/network' + str(net_number))

# Returns the Bayesian averaging between all network's prediction
def ensemble_predictions(c, x):
	predictions = []
	for i in range(num_networks):
		# Reload the variables into the TensorFlow graph.
		saver.restore(sess=session, save_path=get_save_path(i))

		#Perform forward calculation
		feed_dict_test = {model.input_x: x, model.constants: c, model.training: False}
		pred = session.run(model.inference, feed_dict=feed_dict_test)
		predictions.append(pred)
  	
  	return np.mean(np.array(predictions), axis=0)

if __name__ == '__main__':
	# Load Inputs in vector form
	x_test = []
	c_test = []
	y_test = []
	for systemName in test_systems:
		x = nnUtils.getGCCAMEInstances(systemName)
		y = nnUtils.getGCLabels(systemName)
		c = nnUtils.getSystemConstants(systemName)
		x_test.append(x)
		y_test.append(y)
		c_test.append(c)

	# New graph
	tf.reset_default_graph()

	# Create model
	model = came.CAME(
		nb_metrics, 
		nb_filters1, 
		pool_size1, 
		nb_filters2, 
		kernel_size2, 
		pool_size2, 
		dense_shape
	)

	# To restore the trained models
	saver = tf.train.Saver()
	# Create session
	session = tf.Session()
	
	# Print performances of the ensemble model on test set
	pre = []
	rec = []
	f_m = []
	acc = []
	for i in range(len(x_test)):
		output = ensemble_predictions(c_test[i], x_test[i])
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