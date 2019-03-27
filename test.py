import utils.entityUtils as entityUtils
import csv

systems = [
	'android-frameworks-opt-telephony',
	'android-platform-support',
	'apache-ant',
	'apache-lucene',
	'apache-tomcat',
	'argouml',
	'jedit',
	'xerces'
]


def printMissingEntities(systemName):
	entityFile = './data/metric_files/' + systemName + '/feature_envy/commit_0.csv'
	entities = []
	with open(entityFile, 'r') as file:
		reader = csv.DictReader(file, delimiter=';')
		for row in reader:
			normalizedMethodName = entityUtils.normalizeMethodName(row['Method'])
			entities.append(normalizedMethodName + ';' + row['Class'])


	smellFile = './data/antipatterns/' + systemName + '/feature_envy.txt'
	with open(smellFile, 'r') as file:
		for fe in file.read().splitlines():
			if fe not in entities:
				print(fe)

if __name__ == "__main__":
	for system in systems:
		printMissingEntities(system)
		print()