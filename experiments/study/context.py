import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import utils.nnUtils as nnUtils

import experiments.training.train_came as train_came

import approaches.came.CAME as came

import approaches.came.came_prediction as came_prediction
import approaches.svm.svm_prediction as svm_prediction
import approaches.decision_tree.decision_tree_prediction as decision_tree_prediction
import approaches.DECOR.decor_prediction as decor_prediction
import approaches.JDeodorant.jdeodorant_prediction as jdeodorant_prediction
import approaches.HIST.hist_prediction as hist_prediction