import re

def normalizeMethodName(methodName):
	m1 = re.match('(.+)\((.*)\)', methodName)

	name = m1.group(1)
	parameters = m1.group(2)
	paramList = parameters.split(', ')

	normalizedParamList = []
	for param in paramList:
		normalizedParam = param.split('.')[-1]
		m2 = re.match('(\w*)\W*', normalizedParam)

		normalizedParamList.append(m2.group(1))

	normalizedParamList = [s.lower() for s in normalizedParamList]
	normalizedParamList.sort()

	return name + '(' + ', '.join(normalizedParamList) + ')'