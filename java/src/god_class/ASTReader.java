package god_class;

import java.io.File;
import java.io.IOException;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.apache.commons.io.FileUtils;
import org.eclipse.jdt.core.JavaCore;
import org.eclipse.jdt.core.dom.AST;
import org.eclipse.jdt.core.dom.ASTParser;
import org.eclipse.jdt.core.dom.CompilationUnit;

public class ASTReader {
	private String repositoryPath = null;
	private Set<String> sources = null;
	
	private Set<String> types =  new HashSet<String>();
	private Set<String> dataClasses =  new HashSet<String>();
	private Set<String> accessorMethods = new HashSet<String>();
	private Map<String, Set<String>> fileToClassMap = new HashMap<String,Set<String>>();
	private Map<String, Integer> classToLOCMap = new HashMap<String,Integer>();
	private Map<String, Integer> classToNMDMap = new HashMap<String,Integer>();
	private Map<String, Integer> classToNADMap = new HashMap<String,Integer>();
	private Map<String, Double> classToLCOM5Map = new HashMap<String,Double>();
	private Map<String, Set<String>> classToAccessedClassesMap = new HashMap<String, Set<String>>();
	private Map<String, Set<String>> classToAccessedAttributesMap = new HashMap<String, Set<String>>();
	private Map<String, Set<String>> classToInvokedMethodsMap = new HashMap<String, Set<String>>();
	
	public ASTReader(String repositoryPath, String[] dirsToAnalyze) {
		this.repositoryPath = repositoryPath;
		
		updateSources();
		
		for (int i=0;i<dirsToAnalyze.length;i++) {
			Collection<File> filesInDirectory = FileUtils.listFiles(new File(repositoryPath + dirsToAnalyze[i]), new String[]{"java"}, true);
			for (File file : filesInDirectory) {
				try {
					addFile(file.getAbsolutePath());
				}
				catch (IOException e) {
					e.printStackTrace();
				}
			}
		}
	}
		
	
	// METRICS GETTERS //
	public Set<String> getTypes() {
		return this.types;
	}
	
	public int getLOC(String c) {
		return this.classToLOCMap.get(c);
	}
	
	public int getNMD(String c) {
		return this.classToNMDMap.get(c);
	}
	
	public int getNAD(String c) {
		return this.classToNADMap.get(c);
	}
	
	public double getLCOM5(String c) {
		return this.classToLCOM5Map.get(c);
	}
	
	public int getNbAssociatedDataClasses(String c) {
		Set<String> associatedDataClasses = new HashSet<String>();
		for (String associatedClass : classToAccessedClassesMap.get(c)) {
			if (dataClasses.contains(associatedClass)) {
				associatedDataClasses.add(associatedClass);
			}
		}
		
		return associatedDataClasses.size();
	}
	
	public int getATFD (String c) {
		int atfd = 0;
		for (String attribute : classToAccessedAttributesMap.get(c)) {
			if (!attribute.startsWith(c + ".")) {
				atfd++;
			}
		}
		
		// A class never invoked its own accessors
		// so just check if the invoked method is an accessor
		for (String method : classToInvokedMethodsMap.get(c)) {
			if (accessorMethods.contains(method)) {
				atfd++;
			}
		}
		
		return atfd;
	}
	
	
	// UPDATE MECHANISM //
	
	//Return true if something has been changed in the system
	public boolean update(Map<String, String> changes) {
		updateSources();
		boolean changed = false;
		for (Map.Entry<String, String> entry : changes.entrySet()) {
			String changeType = entry.getValue();
			String absoluteFilePath = repositoryPath + entry.getKey();
			switch (changeType) {
				case "A":
					if (removeFile(absoluteFilePath))
						changed = true;
					break;
					
				case "M":
					try {
						if (updateFile(absoluteFilePath))
							changed = true;
					}
					catch (IOException e) {
						e.printStackTrace();
					}
					break;
					
				case "D":
					try {
						addFile(absoluteFilePath);
						changed = true;
					}
					catch (IOException e) {
						e.printStackTrace();
					}
			}
		}
		
		return changed;
		
	}
	
	private void updateSources() {
		File rootDir = new File(repositoryPath);
		sources = getSourcepathEntries(rootDir);
	}
	private Set<String> getSourcepathEntries(File directory) {
		Set<String> sourcepathEntries = new HashSet<String>();
		Set<File> subDirectories = getDirectories(directory);
		for (File subDirectory: subDirectories) {
			String sourceDir=null;
			try {
				sourceDir = getSourceDir(subDirectory);
			} catch (IOException e) {
				// TODO Auto-generated catch block
				e.printStackTrace();
			}
			if (sourceDir != null) {
				sourcepathEntries.add(sourceDir);
			}
		}
		return sourcepathEntries;
	}
	
	private Set<File> getDirectories(File directory) {
		Set<File> directories = new HashSet<File>();
		File[] files = directory.listFiles();
		for (File file : files) {
			if (file.isDirectory() && !file.getName().equals(".git")) {
				directories.add(file);
				directories.addAll(getDirectories(file));
			}
		}
		return directories;
	}
	
	private String getSourceDir(File directory) throws IOException {
		File[] files = directory.listFiles();
		for (File file : files) {
			if (file.getName().endsWith(".java")) {
				String fileString = FileUtils.readFileToString(file, "UTF-8");
				Pattern p = Pattern.compile("package\\s+(.+);");
				Matcher m = p.matcher(fileString);
				if(m.find()) {
					String sourcePath = "/"+ directory.getAbsolutePath().substring(1,directory.getAbsolutePath().length()- m.group(1).length());
					File sourceFile = new File(sourcePath);
					if (sourceFile.exists())
						return sourcePath;
				}
			}
		}
		return null;
		
	}
	
	
	private void addFile(String absoluteFilePath) throws IOException {
		File file = new File(absoluteFilePath);
		if (!file.exists()) {
			return;
		}
		
		String fileString = FileUtils.readFileToString(file, "UTF-8");
		String projectName = repositoryPath.split("/")[repositoryPath.split("/").length-1];
		String fileName = "/" + projectName + absoluteFilePath.split(projectName)[absoluteFilePath.split(projectName).length -1];
		
		String[] sourcePathEntries = new String[sources.size()];
		int i=0;
		for (String path : sources) {
			sourcePathEntries[i] = path;
			i++;
		}
		
		ASTParser parser = ASTParser.newParser(AST.JLS8);
		parser.setKind(ASTParser.K_COMPILATION_UNIT);
		parser.setResolveBindings(true);
		parser.setBindingsRecovery(true);
		parser.setCompilerOptions(JavaCore.getOptions());
		parser.setUnitName(fileName);
		
		parser.setEnvironment(null, sourcePathEntries, null, true);
		parser.setSource(fileString.toCharArray());
		
		CompilationUnit cu = (CompilationUnit) parser.createAST(null);
		
		FileVisitor visitor = new FileVisitor();
		cu.accept(visitor);
		
		types.addAll(visitor.getTypes());
		dataClasses.addAll(visitor.getDataClasses());
		accessorMethods.addAll(visitor.getAccessorMethods());
		fileToClassMap.put(absoluteFilePath, visitor.getTypes());
		classToLOCMap.putAll(visitor.getClassToLOCMap());
		classToNMDMap.putAll(visitor.getClassToNMDMap());
		classToNADMap.putAll(visitor.getClassToNADMap());
		classToLCOM5Map.putAll(visitor.getClassToLCOM5Map());
		classToAccessedClassesMap.putAll(visitor.getClassToAccessedClassesMap());
		classToAccessedAttributesMap.putAll(visitor.getClassToAccessedAttributesMap());
		classToInvokedMethodsMap.putAll(visitor.getClassToInvokedMethodsMap());
	
	} 
	
	private boolean removeFile(String absoluteFilePath) {
		if(fileToClassMap.containsKey(absoluteFilePath)) {
			Set<String> classes = fileToClassMap.get(absoluteFilePath);
			fileToClassMap.remove(absoluteFilePath);
			
			for (String c : classes) {
				types.remove(c);
				dataClasses.remove(c);
				classToLOCMap.remove(c);
				classToNMDMap.remove(c);
				classToNADMap.remove(c);
				classToLCOM5Map.remove(c);
				classToAccessedClassesMap.remove(c);
				classToAccessedAttributesMap.remove(c);
				classToInvokedMethodsMap.remove(c);
				
				accessorMethods.removeAll(getEntitiesToRemove(accessorMethods, c));
			}
			return true;
		}
		
		return false;
	}
	
	
	private boolean updateFile(String absoluteFilePath) throws IOException {
		if(fileToClassMap.containsKey(absoluteFilePath)) {
			removeFile(absoluteFilePath);
			addFile(absoluteFilePath);
			return true;
		}
		
		return false;
	}
	
	
	// UTILS //
	
	private Set<String> getEntitiesToRemove(Set<String> set, String c) {
		Set<String> entitiesToRemove = new HashSet<String>();
		for (String e : set) {
			if (e.startsWith(c + ".")) {
				entitiesToRemove.add(c);
			}
		}
		return entitiesToRemove;
	}
}