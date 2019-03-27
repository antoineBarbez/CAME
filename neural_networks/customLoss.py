from __future__ import division

import tensorflow as tf


def f_measure_approx(logits, labels, gamma):
    ''' 
    This function implements the Differentiable approximation of the f-measure from:
    Martin Jansche (2005):
        [Maximum Expected F-Measure Training of Logistic Regression Models]

    true_positive:  sum(sigmoid(gamma*logits)) for label = +1
    detected: sum(sigmoid(gamma*logits))
    gamma > 0
    '''
    true_positive = tf.reduce_sum(tf.multiply(labels, tf.nn.softmax(gamma*logits)), 0)[0]
    positive = tf.reduce_sum(labels, 0)[0]
    detected = tf.reduce_sum(tf.nn.softmax(gamma*logits), 0)[0]

    return 2*true_positive/(positive+detected)

# Custom loss function that maximizes f-measure  
def loss(logits, labels):
	return 1 - f_measure_approx(logits, labels, 4)