from context import ROOT_DIR

import os
import progressbar
import subprocess
import systems

class RepositoryMiner(object):
	def setup(self, system):
		self.REPOSITORY_URL   = system['url']
		self.SYSTEM_NAME      = system['name']
		self.SHA              = system['snapshot']
		self.MAIN_DIRS        = system['directory']

		self.JAR = os.path.join(ROOT_DIR, 'data_generation', 'jars', 'RepositoryMiner.jar')

		# Directories
		TEMP = os.path.join(ROOT_DIR, 'data_generation', 'TEMP')
		self.REPOSITORY_DIR = os.path.join(TEMP, self.SYSTEM_NAME)

		if not os.path.exists(TEMP):
			os.makedirs(TEMP)

		# Clone if not exists
		if not os.path.exists(self.REPOSITORY_DIR):
			cloneCommand = 'git clone ' + self.REPOSITORY_URL + ' ' + self.REPOSITORY_DIR
			subprocess.call(cloneCommand, shell=True)


	def mine(self, system, antipattern):
		self.setup(system)
		self.__createMetricFiles(antipattern)

	
	def __createMetricFiles(self, antipattern):
		assert antipattern in ['god_class', 'feature_envy'], antipattern + ' not valid antipattern name. Choose either "god_class" or "feature_envy"'
		
		if antipattern == 'god_class':
			option = ' -gc'
		else:
			option = ' -fe'

		metric_files_dir = os.path.join(ROOT_DIR, 'data', 'metric_files', self.SYSTEM_NAME)
		
		if not os.path.exists(metric_files_dir):
			os.makedirs(metric_files_dir)

		command = 'java -jar ' + self.JAR + option + ' ' + self.REPOSITORY_DIR + ' ' + self.SHA + ' ' + "@".join(self.MAIN_DIRS) + ' ' + metric_files_dir
		subprocess.call(command, shell=True)
