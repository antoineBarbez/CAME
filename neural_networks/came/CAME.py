from context import loss

import tensorflow as tf
import numpy as np


class CAME(object):
	def __init__(self, nb_metrics, history_length, filters, kernel_sizes, pool_sizes, dense_sizes):
		assert (len(filters) == len(kernel_sizes)) & (len(kernel_sizes) == len(pool_sizes)), "filters, kernel_sizes and pool_sizes must have same length"

		# Placeholders for instances and labels
		self.input_x = tf.placeholder(tf.float32,[None, history_length, nb_metrics], name="input_x")
		self.input_y = tf.placeholder(tf.float32,[None, 1], name="input_y")
		
		# Placeholders for learning parameters
		self.learning_rate = tf.placeholder(tf.float32, name="learning_rate")
		self.beta          = tf.placeholder(tf.float32, name="beta")
		self.gamma         = tf.placeholder(tf.float32, name="gamma")

		# L2 regularization & initialization
		l2_reg = tf.contrib.layers.l2_regularizer(scale=self.beta)
		xavier = tf.contrib.layers.xavier_initializer()


		# Convolutional layers
		previous_layer = self.input_x
		for i in range(len(kernel_sizes)):
			with tf.name_scope("conv-%s" % str(i+1)):
				previous_layer = tf.layers.conv1d(
					inputs=previous_layer,
					filters=filters[i],
					kernel_size=kernel_sizes[i],
					padding = "same",
					activation=tf.tanh,
					kernel_regularizer=l2_reg,
					kernel_initializer=xavier
				)

				print(previous_layer.get_shape())

			with tf.name_scope("pool-%s" % str(i+1)):
				previous_layer = tf.layers.max_pooling1d(
					inputs= previous_layer,
					pool_size= pool_sizes[i],
					strides = pool_sizes[i],
					padding= "same"
				)

				print(previous_layer.get_shape())

		with tf.name_scope("pool_flat"):
			previous_layer = tf.contrib.layers.flatten(previous_layer)

			print(previous_layer.get_shape())
		
		
		# Dense layers
		for i in range(len(dense_sizes)):
			with tf.name_scope("dense-%s" % str(i+1)):
				previous_layer = tf.layers.dense(
					inputs=previous_layer,
					units=dense_sizes[i],
					activation=tf.tanh,
					kernel_initializer=xavier,
					kernel_regularizer=l2_reg,
					bias_regularizer=l2_reg
				)


		# Output layer
		with tf.name_scope("output"):
			self.logits = tf.layers.dense(
				inputs=previous_layer,
				units=1,
				kernel_initializer=xavier,
				kernel_regularizer=l2_reg,
				bias_regularizer=l2_reg
			)

			self.inference = tf.nn.sigmoid(self.logits)


		# Loss function
		with tf.name_scope("loss"):
			self.loss = loss.compute(self.logits, self.input_y, self.gamma)
			l2_loss = tf.losses.get_regularization_loss()
			loss_reg = self.loss + l2_loss

		# Learning mechanism
		self.learning_step = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(loss_reg)