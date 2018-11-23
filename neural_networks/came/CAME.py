from context import customLoss

import tensorflow as tf
import numpy as np


class CAME(object):
	def __init__(self, nb_metrics, nb_filters1, pool_size1, nb_filters2, kernel_size2, pool_size2, dense_shape):
		history_length = 1001
		output_size = 2
		constants_size = 2

		# Placeholders for instances and labels
		self.input_x = tf.placeholder(tf.float32,[None, history_length, nb_metrics], name="input_x")
		self.input_y = tf.placeholder(tf.float32,[None, output_size], name="input_y")

		# Placeholders for batch constants
		self.constants = tf.placeholder(tf.float32, [constants_size], name="batch_constants")
		
		# Placeholders for learning parameters
		#self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
		self.learning_rate     = tf.placeholder(tf.float32, name="learning_rate")
		self.beta              = tf.placeholder(tf.float32, name="beta")

		# L2 regularization & initialization
		l2_reg = tf.contrib.layers.l2_regularizer(scale=self.beta)
		xavier = tf.contrib.layers.xavier_initializer()

		# Convolution layers
		with tf.name_scope("conv1"):
			conv1 = tf.layers.conv1d(
				inputs=self.input_x,
				filters=nb_filters1,
				kernel_size=2,
				padding = "valid",
				activation=tf.tanh,
				kernel_regularizer=l2_reg,
				kernel_initializer=xavier
			)

		with tf.name_scope("pool1"):
			pool1 = tf.layers.max_pooling1d(
				inputs= conv1,
				pool_size= pool_size1,
				strides = pool_size1,
				padding= "valid"
			)

		with tf.name_scope("conv2"):
			conv2 = tf.layers.conv1d(
				inputs=pool1,
				filters=nb_filters2,
				kernel_size=kernel_size2,
				padding = "same",
				activation=tf.tanh,
				kernel_regularizer=l2_reg,
				kernel_initializer=xavier
			)

		with tf.name_scope("pool2"):
			pool2 = tf.layers.max_pooling1d(
				inputs= conv2,
				pool_size= pool_size2,
				strides = pool_size2,
				padding="same"
			)

		with tf.name_scope("pool_flat"):
			pool_flat = tf.contrib.layers.flatten(pool2)


		# Add batch constants to the input of the dense layers
		with tf.name_scope("dense_input"):
			batch_constants = tf.expand_dims(self.constants, 0)
			batch_constants = tf.tile(batch_constants, [tf.shape(self.input_x)[0], 1])
			dense_input = tf.concat([pool_flat, batch_constants], axis=1)

		
		# Dense layers
		h_in = dense_input
		for size in dense_shape:
			with tf.name_scope("dense%s" % size):
				h_in = tf.layers.dense(
					inputs=h_in,
					units=size,
					activation=tf.tanh,
					kernel_initializer=xavier,
					kernel_regularizer=l2_reg,
					bias_regularizer=l2_reg
				)


		# Output layer
		with tf.name_scope("output"):
			self.logits = tf.layers.dense(
				inputs=h_in,
				units=output_size,
				kernel_initializer=xavier,
				kernel_regularizer=l2_reg,
				bias_regularizer=l2_reg
			)

			self.inference = tf.nn.softmax(self.logits)


		# Loss function
		with tf.name_scope("loss"):
			self.loss = customLoss.loss(self.logits, self.input_y)
			l2_loss = tf.losses.get_regularization_loss()
			loss_reg = self.loss + l2_loss

		# Learning mechanism
		self.learning_step = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(loss_reg)