from context import ROOT_DIR, nnUtils, hist

import numpy as np
import matplotlib.pyplot as plt


tuning_systems = [
	'android-frameworks-opt-telephony',
	'apache-ant',
	'apache-lucene',
	'argouml',
	'xerces'
]

if __name__ == "__main__":
	# Get labels
	overall_labels = np.empty(shape=[0, 1])
	for system in tuning_systems:
		overall_labels = np.concatenate((overall_labels, nnUtils.get_labels(system, 'god_class')), axis=0)


	thresholds = np.arange(0.01, 0.30, 0.01)
	performances = []
	for t in thresholds:
		overall_prediction_hist = np.empty(shape=[0, 1])
		for system in tuning_systems:
			overall_prediction_hist = np.concatenate((overall_prediction_hist, hist.getSmells(system, t)), axis=0)
		performances.append(nnUtils.f_measure(overall_prediction_hist, overall_labels))

	print("Best value: " + str(thresholds[np.argmax(performances)]))

	plt.plot(thresholds, performances)
	plt.show()

