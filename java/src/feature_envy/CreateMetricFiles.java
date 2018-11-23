package fe;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.Set;

public class CreateMetricFiles {
	public static void main(String[] args) {
		if (args.length != 4) {
			System.out.println("Invalid arguments");
			return;
		}
		
		for (int i=0; i<args.length;i++) {
			String arg = args[i].split(":")[0];
			switch (arg) {
			case "snapshot":
				snapshot = args[i].split(":")[1];
				break;
			case "repo":
				repositoryPath = args[i].split(":")[1];
				break;
			case "dirs":
				dirsToAnalyze = args[i].split(":", -1)[1].split("@", -1);
				break;
			case "output":
				metricFilesDir = args[i].split(":")[1];
			
			}
		}
		gitCommand = "git --git-dir=" + repositoryPath + ".git" ;
		
		createMetricFiles();
	}
	
	private static String snapshot;
	private static String repositoryPath;
	private static String[] dirsToAnalyze;
	private static String metricFilesDir;
	
	private static String gitCommand;
	
	private static ASTReader reader;
	
	private static List<String> previousLines = new ArrayList<String>();
	private static Set<String> instances;
	private static int nbCommit = 0;
	
	
	private static void createMetricFiles() {
		System.out.println("Creating metric files at " + metricFilesDir);
		
		// Checkout to the desired version of the system
		checkout(snapshot);
		
		// Initialize the ASTReader
		reader = new ASTReader(repositoryPath, dirsToAnalyze);
		
		// Initialize instances to analyze (i.e., instance of the desired version of the system)
		instances = reader.getInstances();
		
		createMetricFile();
		nbCommit++;
		
		List<String> commits = getCommits();
		Iterator<String> iteratorOnCommits = commits.iterator();
		
		//skip the first commit (already been processed)
		iteratorOnCommits.next();
		
		while (nbCommit < 1000 && iteratorOnCommits.hasNext()) {
			if (nbCommit%10==0) {
				System.out.print("Processed " + String.valueOf(nbCommit) + " commits\r");
			}
			Map<String, String> changes = getChanges(snapshot);
			snapshot = iteratorOnCommits.next();
			checkout(snapshot);
			if (reader.update(changes))
				if (createMetricFile())
					nbCommit++;
		}
		System.out.println("");
	}
	
	private static void checkout(String sha) {
		String command = gitCommand + " --work-tree=" + repositoryPath + " checkout -f " + sha;
		try {
			Process cmdProc = Runtime.getRuntime().exec(command);
			
			String line;
			BufferedReader stderrReader = new BufferedReader(
			         new InputStreamReader(cmdProc.getErrorStream()));
			while ((line = stderrReader.readLine()) != null) {
				//System.out.println(line);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
	
	private static List<String> getCommits() {
		String command = gitCommand + " log --pretty=format:%H_%aD";
		List<String> commits = new ArrayList<String>();
		try {
			Process cmdProc = Runtime.getRuntime().exec(command);
			BufferedReader stdoutReader = new BufferedReader(
			         new InputStreamReader(cmdProc.getInputStream()));
			
			String line;
			while ((line = stdoutReader.readLine()) != null) {
				String sha = line.split("_")[0];
				commits.add(sha);
			}
			
			BufferedReader stderrReader = new BufferedReader(
			         new InputStreamReader(cmdProc.getErrorStream()));
			while ((line = stderrReader.readLine()) != null) {
				System.out.println(line);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		return commits;
	}
	
	private static Map<String, String> getChanges(String sha) {
		Map<String, String> changes = new HashMap<String, String>();
		
		String command = gitCommand + " diff-tree --no-commit-id --name-status -r " + sha;
		try {
			Process cmdProc = Runtime.getRuntime().exec(command);
			BufferedReader stdoutReader = new BufferedReader(
			         new InputStreamReader(cmdProc.getInputStream()));
			
			String line;
			while ((line = stdoutReader.readLine()) != null) {
				if (line.endsWith(".java")) {
					String changeType = line.split("\\s+")[0];
					String relativeFilePath = line.split("\\s+")[1];
					changes.put(relativeFilePath, changeType);	
				}
			}
			
			BufferedReader stderrReader = new BufferedReader(
			         new InputStreamReader(cmdProc.getErrorStream()));
			while ((line = stderrReader.readLine()) != null) {
				System.out.println(line);
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
		
		return changes;
	}
	
	private static boolean createMetricFile() {
		List<String> lines = getLines();
		if (lines.equals(previousLines)) {
			return false;
		}
		
		String metricFilePath = metricFilesDir + "commit" + String.valueOf(nbCommit) + ".csv";
		String firstLine = "Method;TargetClass;ATFD;ATSD;FDP;DIST_EC;DIST_TC;LOC_M;LOC_EC;LOC_TC";
		final Iterator<String> iter = lines.iterator();
		try (PrintWriter out = new PrintWriter(metricFilePath)) {
			out.println(firstLine);

			while (iter.hasNext()) {
				String csvLine = iter.next();
				if (csvLine != null) {
					out.println(csvLine);
				}
			}
			out.close();
		}
		catch (final java.io.FileNotFoundException e) {
			System.out.print("file not found");
		}
		previousLines = lines;
		return true;
	}
	
	private static List<String> getLines() {
		List<String> lines = new ArrayList<String>();
		
		Set<String> newInstances = reader.getInstances();
		for (String instance : instances) {
			String line;
			String method = instance.split(";")[0];
			String enclosingClass = Utils.getEnclosingClass(method);
			if (newInstances.contains(instance) && reader.contains(enclosingClass)) {
				String targetClass = instance.split(";")[1];
				
				StringBuffer lineBuffer = new StringBuffer();
				lineBuffer.append(instance);
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getNbAccesses(method, targetClass)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getNbAccesses(method, enclosingClass)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getFDP(method, enclosingClass)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getDistance(method, enclosingClass)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getDistance(method, targetClass)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getLOC(method)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getLOC(enclosingClass)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getLOC(targetClass)));
				
				
				line = lineBuffer.toString();
			}else {
				line = instance + ";0;0;0;0;0;0;0;0";
			}
			lines.add(line);
		}
		return lines;
	}
}