from context import nnUtils, came_prediction, svm_prediction, decision_tree_prediction, decor_prediction, jdeodorant_prediction, hist_prediction

import numpy as np

systems = ['apache-tomcat', 'jedit', 'android-platform-support']

overall_prediction_decor = np.empty(shape=[0, 1])
overall_prediction_hist = np.empty(shape=[0, 1])
overall_prediction_jd = np.empty(shape=[0, 1])
overall_prediction_dt = np.empty(shape=[0, 1])
overall_prediction_mlp = np.empty(shape=[0, 1])
overall_prediction_svm = np.empty(shape=[0, 1])
overall_prediction_came = np.empty(shape=[0, 1])

overall_labels = np.empty(shape=[0, 1])
for system in systems:
	# Get occurrences manually detected on the considered system
	labels = nnUtils.get_labels(system, 'god_class')
	overall_labels = np.concatenate((overall_labels, labels), axis=0)

	# Compute performances for DECOR
	prediction_decor = decor_prediction.getSmells(system)
	overall_prediction_decor = np.concatenate((overall_prediction_decor, prediction_decor), axis=0)

	# Compute performances for HIST
	prediction_hist = hist_prediction.getSmells(system, 0.08)
	overall_prediction_hist = np.concatenate((overall_prediction_hist, prediction_hist), axis=0)

	# Compute performances for JDeodorant
	prediction_jd = jdeodorant_prediction.getSmells(system)
	overall_prediction_jd = np.concatenate((overall_prediction_jd, prediction_jd), axis=0)

	# Compute performances for Decision Tree
	prediction_dt = np.array(decision_tree_prediction.getSmells(system)).reshape(-1, 1)
	overall_prediction_dt = np.concatenate((overall_prediction_dt, prediction_dt), axis=0)

	# Compute performances for MLP
	prediction_mlp = came_prediction.getSmells(system, 1)
	overall_prediction_mlp = np.concatenate((overall_prediction_mlp, prediction_mlp), axis=0)

	# Compute performances for SVM
	prediction_svm = np.array(svm_prediction.getSmells(system)).reshape(-1, 1)
	overall_prediction_svm = np.concatenate((overall_prediction_svm, prediction_svm), axis=0)

	# Compute performances for CAME
	prediction_came = came_prediction.getSmells(system, 500)
	overall_prediction_came = np.concatenate((overall_prediction_came, prediction_came), axis=0)


	# Print performances for the considered system
	print(system)
	print('              |precision  |recall  |f_measure')
	print('-------------------------------------------------')
	print('DECOR         |' + "{0:.3f}".format(nnUtils.precision(prediction_decor, labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(prediction_decor, labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(prediction_decor, labels)))
	print('-------------------------------------------------')
	print('HIST          |' + "{0:.3f}".format(nnUtils.precision(prediction_hist, labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(prediction_hist, labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(prediction_hist, labels)))
	print('-------------------------------------------------')
	print('JDeodorant    |' + "{0:.3f}".format(nnUtils.precision(prediction_jd, labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(prediction_jd, labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(prediction_jd, labels)))
	print('-------------------------------------------------')
	print('-------------------------------------------------')
	print('Decision Tree |' + "{0:.3f}".format(nnUtils.precision(prediction_dt, labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(prediction_dt, labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(prediction_dt, labels)))
	print('-------------------------------------------------')
	print('MLP           |' + "{0:.3f}".format(nnUtils.precision(prediction_mlp, labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(prediction_mlp, labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(prediction_mlp, labels)))
	print('-------------------------------------------------')
	print('SVM           |' + "{0:.3f}".format(nnUtils.precision(prediction_svm, labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(prediction_svm, labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(prediction_svm, labels)))
	print('-------------------------------------------------')
	print('-------------------------------------------------')
	print('CAME          |' + "{0:.3f}".format(nnUtils.precision(prediction_came, labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(prediction_came, labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(prediction_came, labels)))
	print('\n\n')



# Print overall performances
print('OVERALL')
print('              |precision  |recall  |f_measure')
print('-------------------------------------------------')
print('DECOR         |' + "{0:.3f}".format(nnUtils.precision(overall_prediction_decor, overall_labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(overall_prediction_decor, overall_labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(overall_prediction_decor, overall_labels)))
print('-------------------------------------------------')
print('HIST          |' + "{0:.3f}".format(nnUtils.precision(overall_prediction_hist, overall_labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(overall_prediction_hist, overall_labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(overall_prediction_hist, overall_labels)))
print('-------------------------------------------------')
print('JDeodorant    |' + "{0:.3f}".format(nnUtils.precision(overall_prediction_jd, overall_labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(overall_prediction_jd, overall_labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(overall_prediction_jd, overall_labels)))
print('-------------------------------------------------')
print('-------------------------------------------------')
print('Decision Tree |' + "{0:.3f}".format(nnUtils.precision(overall_prediction_dt, overall_labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(overall_prediction_dt, overall_labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(overall_prediction_dt, overall_labels)))
print('-------------------------------------------------')
print('MLP           |' + "{0:.3f}".format(nnUtils.precision(overall_prediction_mlp, overall_labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(overall_prediction_mlp, overall_labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(overall_prediction_mlp, overall_labels)))
print('-------------------------------------------------')
print('SVM           |' + "{0:.3f}".format(nnUtils.precision(overall_prediction_svm, overall_labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(overall_prediction_svm, overall_labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(overall_prediction_svm, overall_labels)))
print('-------------------------------------------------')
print('-------------------------------------------------')
print('CAME          |' + "{0:.3f}".format(nnUtils.precision(overall_prediction_came, overall_labels)) + '      |' + "{0:.3f}".format(nnUtils.recall(overall_prediction_came, overall_labels)) + '   |' + "{0:.3f}".format(nnUtils.f_measure(overall_prediction_came, overall_labels)))
print('\n\n')

