# CAME
CAME (Convolutional Analysis of code Metrics Evolution) is a deep-learning based anti-patterns detection approach. CAME uses a Convolutional Neural Network architecture to detect anti-patterns from both structural and historical information mined from version control systems (e.g., Git).

This approach has been experimented for the detection of **God Class**.

If you want to train/test CAME on other java software systems or using a different set of metrics, you will need to produce some *metric files* in order to build the input matrices for our CNN. This can be done with the [RepositoryMiner](https://github.com/antoineBarbez/RepositoryMiner/) component. 

## Repository Structure
This repository is organized as follows:
* **approaches:** The source code of the God Class detection approaches investigated in this work, i.e., CAME, MLP, decision tree, svm, DECOR, HIST and JDeodorant.
* **data:** Contains necessary data to run the experiments.
  * **antipatterns:** The oracle, i.e., manually-tagged occurrences of God Class in eight software systems.
  * **metric_files:** Files containing the metrics related to code components. Each file corresponds to one commit in the history of the system.
* **data_construction:** Code used to generate the metric files through the *repository_miner* component.
* **experiments:** The source code of our experiments: training, comparison, parameter tuning, etc.
* **utils:** Modules used to access and manipulate the data.

## Research 
The paper associated to this repository has been accepted for inclusion in the Research Track of the 35th IEEE International Conference on Software Maintenance and Evolution (ICSME), 2019.
