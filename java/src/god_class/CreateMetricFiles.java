package god_class;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
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
				dirsToAnalyze = args[i].split(":")[1].split("@", -1);
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
	private static Set<String> classes;
	private static int nbCommit = 0;
	
	
	private static void createMetricFiles() {
		System.out.println("Creating metric file...");
		
		// Checkout to the desired version of the system
		checkout(snapshot);
		
		// Initialize the ASTReader
		reader = new ASTReader(repositoryPath, dirsToAnalyze);
		
		// Initialize instances to analyze (i.e., instance of the desired version of the system)
		setClasses();
		
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
	}
	
	private static void setClasses() {
		//Get all classes in the first version of the system
		classes = new HashSet<String>();
		for (String c : reader.getTypes()) {
			classes.add(c);
		}
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
		
		String metricsFilePath = metricFilesDir + "commit" + String.valueOf(nbCommit) + ".csv";
		String firstLine = "Class;LOC;NMD;NAD;LCOM5;DataClass;ATFD";
		final Iterator<String> iter = lines.iterator();
		try (PrintWriter out = new PrintWriter(metricsFilePath)) {
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
		for (String c : classes) {
			String line;
			if (reader.getTypes().contains(c)) {
				StringBuffer lineBuffer = new StringBuffer();
				lineBuffer.append(c);
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getLOC(c)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getNMD(c)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getNAD(c)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getLCOM5(c)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getNbAssociatedDataClasses(c)));
				lineBuffer.append(";");
				lineBuffer.append(String.valueOf(reader.getATFD(c)));
				
				line = lineBuffer.toString();
			}else{
				line = c + ";0;0;0;0;0;0";
			}
			lines.add(line);
		}
		
		return lines;
	}
}