from context import ROOT_DIR, dataUtils

import numpy as np

import csv
import os

def getHistory(systemName):
    # Create an history list containing the names of the classesthat changed in each commit 

    # For example, if class1 and class2 changed in the first commit, 
    # and class1, class2, class3 changed in the second commit, etc ...
    # The history list will be [[class1, class3], [class1, class2, class3], ...]

    historyFile = os.path.join(ROOT_DIR, 'approaches', 'HIST', 'history_files', systemName + '.csv')
    with open(historyFile, 'rb') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=';')
        rawHistory = [{key: row[key] for key in row} for row in reader]

        history  = []
        commit   = []
        snapshot = rawHistory[0]['Snapshot']
        for i, change in enumerate(rawHistory):
            if snapshot != change['Snapshot']:
                history.append(list(set(commit)))
                commit = []
                snapshot = change['Snapshot']

            commit.append(change['Class'])
            
            if i == len(rawHistory)-1:
                history.append(list(set(commit)))

    return history


def getSmells(systemName, threshold):
    classToIdxMap = {c:i for i, c in enumerate(dataUtils.getEntities(systemName, 'god_class'))}
    history = getHistory(systemName)

    # Compute for each class, the number of commits involving at least another class,
    # and the number of occurences in this set of commit.
    nbCommit = np.zeros(len(classToIdxMap))
    occurences = np.zeros(len(classToIdxMap))
    for commit in history:
        nbCommit += 1.0
        if len(commit) > 1:
            for className in commit:
                if className in classToIdxMap:
                    idx = classToIdxMap[className]
                    occurences[idx] = occurences[idx] + 1.0
        else:
            className = commit[0]
            if className in classToIdxMap:
                idx = classToIdxMap[className]
                nbCommit[idx] = nbCommit[idx] - 1


    return np.array([[1.0] if (occurences[i]/nbCommit[i])>threshold else [0.0] for i in range(len(classToIdxMap))])