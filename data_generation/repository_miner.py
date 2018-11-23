from context import ROOT_DIR

import os
import progressbar
import subprocess
import systems

class RepositoryMiner(object):
	def setup(self, system):
		self.repositoryURL   = system['url']
		self.systemName      = system['name']
		self.snapshot        = system['snapshot']
		self.mainDirectories = system['directory']

		print(self.systemName)

		# Directories
		TEMP = os.path.join(ROOT_DIR, 'data_generation', 'TEMP')
		self.REPOSITORY_DIR = os.path.join(TEMP, self.systemName)

		if not os.path.exists(TEMP):
			os.makedirs(TEMP)

		cloneCommand = 'git clone ' + self.repositoryURL + ' ' + self.REPOSITORY_DIR
		subprocess.call(cloneCommand, shell=True)


	def mine(self, system):
		self.setup(system)

		self.__createMetricFiles('god_class')
		self.__createMetricFiles('feature_envy')

	
	def __createMetricFiles(self, antipattern):
		assert antipattern in ['god_class', 'feature_envy'], antipattern + ' not valid antipattern name. Choose "god_class" or "feature_envy instead"'

		if antipattern == 'god_class':
			jarFile = os.path.join(ROOT_DIR, 'java', 'jar', 'GodClassMetricFilesCreator.jar')
		else:
			jarFile = os.path.join(ROOT_DIR, 'java', 'jar', 'FeatureEnvyMetricFilesCreator.jar')

		metric_files_dir = os.path.join(ROOT_DIR, 'data', 'metric_files', antipattern, self.systemName)
		if not os.path.exists(metric_files_dir):
			os.makedirs(metric_files_dir)

		command = "java -jar " + jarFile + " snapshot:" + self.snapshot + " repo:" + self.REPOSITORY_DIR + '/' + " dirs:" + "@".join(self.mainDirectories) + " output:" + metric_files_dir + '/'
		subprocess.call(command, shell=True)


if __name__ == "__main__":
	rm = RepositoryMiner()
	for system in systems.systems_git + systems.systems_svn:
		rm.mine(system)

