import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, ROOT_DIR)

import utils.nnUtils as nnUtils

import neural_networks.mlp.MLP   as mlp
import neural_networks.came.CAME as came