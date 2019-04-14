from context import ROOT_DIR, nnUtils, train_came, came

import tensorflow        as tf
import numpy             as np
import matplotlib.pyplot as plt

import ast
import csv
import os
os.environ['TF_CPP_MIN_LOG_LEVEL']='2'

num_networks = 10
history_lengths = [1, 10, 50, 100, 250, 500, 1000]

def get_optimal_parameters(antipattern, history_length):
	tuning_file = os.path.join(ROOT_DIR, 'experiments', 'tuning', 'results', 'came_' + antipattern + '_' + str(history_length) + '.csv')

	with open(tuning_file, 'r') as file:
		reader = csv.DictReader(file, delimiter=';')

		for row in reader:
			if row['F-measure'] != 'nan':
				return {key:ast.literal_eval(row[key]) for key in row} 

f_measures = []
precisions = []
recalls = []
for history_length in history_lengths:
	params = get_optimal_parameters('god_class', history_length)
	x_test, y_test = train_came.build_dataset(train_came.test_systems, 'god_class', history_length)

	tf.reset_default_graph()

	# Create model
	model = came.CAME(
		nb_metrics=x_test.shape[-1],
		history_length=history_length,
		filters=params['Filters'],
		kernel_sizes=params['Kernel'],
		pool_sizes=params['Pool'],
		dense_sizes=params['Dense'])

	# To restore a trained model
	saver = tf.train.Saver(max_to_keep=num_networks)

	with tf.Session() as session:
		f_ms = []
		pres = []
		recs = []
		for i in range(num_networks):
			# Reload the variables into the TensorFlow graph.
			saver.restore(sess=session, save_path=train_came.get_save_path('god_class', history_length, i))

			prediction = session.run(model.inference, feed_dict={model.input_x: x_test})
			f_ms.append(nnUtils.f_measure(prediction, y_test))
			pres.append(nnUtils.precision(prediction, y_test))
			recs.append(nnUtils.recall(prediction, y_test))
		f_measures.append(f_ms)
		precisions.append(pres)
		recalls.append(recs)


plt.figure()
plt.ylim((0.2, 1.0))
plt.xlabel("History length")
plt.ylabel("Score")

f_measures_mean = np.mean(f_measures, axis=1)
precisions_mean = np.mean(precisions, axis=1)
recalls_mean = np.mean(recalls, axis=1)

f_measures_std = np.std(f_measures, axis=1)
precisions_std = np.std(precisions, axis=1)
recalls_std = np.std(recalls, axis=1)
plt.grid()

plt.fill_between(history_lengths, f_measures_mean - f_measures_std,
                 f_measures_mean + f_measures_std, alpha=0.1,
                 color="g")
plt.fill_between(history_lengths, precisions_mean - precisions_std,
                 precisions_mean + precisions_std, alpha=0.1,
                 color="r")
plt.fill_between(history_lengths, recalls_mean - recalls_std,
                 recalls_mean + recalls_std, alpha=0.1,
                 color="b")
plt.plot(history_lengths, f_measures_mean, color="g", marker='o', label='F-measure')
plt.plot(history_lengths, precisions_mean, color="r", marker='o', label='Precision')
plt.plot(history_lengths, recalls_mean, color="b", marker='o', label='Recall')
plt.legend(loc='lower right')
plt.show()

