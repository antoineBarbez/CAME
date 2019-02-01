# CAME (Convolutional Analysis of code Metrics Evolution)
Most of the anti-patterns detection approaches rely on structural properties of software systems (i.e., source code metrics). However, anti-patterns also impact how code components (i.e., classes or methods) evolve together when changes are applied to the system via commits. This project leverages both structural and historical informations to detect anti-patterns. The main idea is to analyze how code metrics related to code components evolve throught the history of the systems. For each component to be classified, the input vector consists in a matrix containing the values of several code metrics computed at each revision of the system under investigation. We then use a Convolutional Neural Network to process this matrix and perform classification.

This approach have been experimented for **God Class** and we are currently extending it for **Feature Envy**.

## Repository Structure
This repository is organized as follows:
* **data:** Contains necessary data to run the experiments.
  * **antipatterns:** The oracle, i.e., manually-tagged occurrences of God Class and Feature Envy in eight software systems.
  * **metric_files:** Files containing the metrics related to code components. Each file corresponds to one commit in the history of the system.
* **data_construction:** Code used to generate the metric files through the *repository_miner* component.
* **experiments:** The source code of our experiments: training, comparison, parameter tuning, etc.
* **java:** Jars and src of the Java code implemented in this work. These jars are used in *~/data_construction/repository_miner/repository_miner.py* to create the metric files.
* **neural_networks:** Tensorflow code of the different NNs implemented in this work.
* **utils:** Modules used to access and manipulate the data.
