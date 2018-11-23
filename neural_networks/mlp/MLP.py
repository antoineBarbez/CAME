from context import customLoss

import tensorflow as tf


class MLP(object):
	def __init__(self, shape, input_size, constants_size):
		output_size = 2

		# Placeholders for instances and labels
		self.input_x = tf.placeholder(tf.float32,[None, input_size], name="input_x")
		self.input_y = tf.placeholder(tf.float32,[None, output_size], name="input_y")

		# Placeholders for batch constants
		self.constants = tf.placeholder(tf.float32, [constants_size], name="batch_constants")
		
		# Placeholders for learning parameters
		self.dropout_keep_prob = tf.placeholder(tf.float32, name="dropout_keep_prob")
		self.learning_rate     = tf.placeholder(tf.float32, name="learning_rate")
		self.beta              = tf.placeholder(tf.float32, name="beta")

		# L2 regularization & initialization
		l2_reg = tf.contrib.layers.l2_regularizer(scale=self.beta)
		xavier = tf.contrib.layers.xavier_initializer()

		# Add batch constants to the input
		with tf.name_scope("input"):
			batch_constants = tf.expand_dims(self.constants, 0)
			batch_constants = tf.tile(batch_constants, [tf.shape(self.input_x)[0], 1])
			x = tf.concat([self.input_x, batch_constants], axis=1)

		# Dropout
		with tf.name_scope("dropout"):
			h_drop = tf.nn.dropout(x, self.dropout_keep_prob)

		# Hidden layers
		h_in = h_drop
		for size in shape:
			with tf.name_scope("hidden-%s" % size):
				h_in = tf.layers.dense(h_in,
									size,
									activation=tf.tanh,
									kernel_initializer=xavier,
									kernel_regularizer=l2_reg,
									bias_regularizer=l2_reg)

		# Output layer
		with tf.name_scope("output"):
			self.logits = tf.layers.dense(h_in,
										output_size,
										kernel_initializer=xavier,
										kernel_regularizer=l2_reg,
										bias_regularizer=l2_reg)
			self.inference = tf.nn.softmax(self.logits)

		# Loss function
		with tf.name_scope("loss"):
			self.loss = customLoss.loss(self.logits, self.input_y)
			l2_loss = tf.losses.get_regularization_loss()
			loss_reg = self.loss + l2_loss

		# Learning mechanism
		self.learning_step = tf.train.GradientDescentOptimizer(self.learning_rate).minimize(loss_reg)