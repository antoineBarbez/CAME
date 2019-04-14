import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import utils.nnUtils    as nnUtils

import experiments.training.train_came as train_came
import experiments.training.train_svm as train_svm
import experiments.training.train_decision_tree as train_decision_tree

import approaches.came.CAME as came
import approaches.HIST.hist_prediction as hist