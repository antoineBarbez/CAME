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
    true_positive = tf.reduce_sum(tf.multiply(labels, tf.nn.sigmoid(gamma*logits)))
    positive = tf.reduce_sum(labels)
    detected = tf.reduce_sum(tf.nn.sigmoid(gamma*logits))

    return 2*true_positive/(positive+detected)

# Custom loss function that maximizes f-measure  
def compute(logits, labels, gamma):
    return 1 - f_measure_approx(logits, labels, gamma)