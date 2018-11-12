package fe;

import java.io.File;
import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
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
	private Set<String> staticEntities = new HashSet<String>();
	private Map<String, Set<String>> fileToClassMap = new HashMap<String,Set<String>>();
	private Map<String, String> accessorToAccessedFieldMap = new HashMap<String,String>();
	private Map<String, Set<String>> classToEntitySetMap = new HashMap<String,Set<String>>();
	private Map<String, Set<String>> classToMethodSetMap = new HashMap<String,Set<String>>();
	private Map<String, Set<String>> methodToEntitySetMap = new HashMap<String,Set<String>>();
	private Map<String, Set<String>> methodToTargetClassSetMap = new HashMap<String,Set<String>>();
	private Map<String, Integer> methodToLOCMap = new HashMap<String, Integer>();
	
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
		replaceAccessorsByAccessedFields(methodToEntitySetMap);

		removeSystemMemberAccesses(classToEntitySetMap);
		removeSystemMemberAccesses(methodToEntitySetMap);
		
		removeStaticEntities(methodToEntitySetMap);
	}
	
	public Set<String> getInstances() {
		Set <String> instances = new HashSet<String>();
		for (Map.Entry<String, Set<String>> entry : methodToTargetClassSetMap.entrySet()) {
			String method = entry.getKey();
			String enclosingClass = Utils.getEnclosingClass(method);
			 
			//Avoid foreign classes and enclosing class
			for (String targetClass : entry.getValue()) {
				if (classToEntitySetMap.containsKey(targetClass) && !targetClass.equals(enclosingClass)) {
					String instance = method + ";" + targetClass;
					instances.add(instance);
				}
			}
		}
		
		return instances;
	}
	
	public boolean contains(String c) {
		if (classToEntitySetMap.containsKey(c)) {
			return true;
		}else {
			return false;
		}
	}
	
	
	// METRICS GETTERS //
	public int getNbAccesses(String m, String c) {
		Set<String> entitySet_m = methodToEntitySetMap.get(m);
		int count = 0;
		for (String entity : entitySet_m) {
			if (entity.startsWith(c + ".")) {
				count++;
			}
		}
		return count;
	}
	
	public int getFDP(String m, String ec) {
		Set<String> targetClassSet_m = methodToTargetClassSetMap.get(m);
		int count = 0;
		for (String tc : targetClassSet_m) {
			if (classToEntitySetMap.containsKey(tc) && !tc.equals(ec))
				count++;
		}
		return count;
	}
	
	public double getDistance(String m, String c) {
		Set<String> entitySet_m = methodToEntitySetMap.get(m);
		Set<String> entitySet_c = classToEntitySetMap.get(c);
		
		if (!classToEntitySetMap.containsKey(c)) {
			entitySet_c = new HashSet<String>();
		}
		
		return Utils.getDistance(entitySet_m, entitySet_c);
	}
	
	public int getLOC(String component) {
		if(methodToLOCMap.containsKey(component))
			return methodToLOCMap.get(component);
		
		int count = 0;
		for (String method : classToMethodSetMap.get(component)) {
			count += methodToLOCMap.get(method);
		}
		
		return count;
	}
	
	
	// UPDATE MECHANISM //
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
		
		if (changed) {
			replaceAccessorsByAccessedFields(methodToEntitySetMap);

			removeSystemMemberAccesses(classToEntitySetMap);
			removeSystemMemberAccesses(methodToEntitySetMap);
			
			removeStaticEntities(methodToEntitySetMap);
		}
		
		return changed;
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
		staticEntities.addAll(visitor.getStaticEntities());
		fileToClassMap.put(absoluteFilePath, visitor.getTypes());
		accessorToAccessedFieldMap.putAll(visitor.getaccessorToAccessedFieldMap());
		classToEntitySetMap.putAll(visitor.getClassToEntitySetMap());
		classToMethodSetMap.putAll(visitor.getClassToMethodSetMap());
		methodToEntitySetMap.putAll(visitor.getMethodToEntitySetMap());
		methodToTargetClassSetMap.putAll(visitor.getMethodToTargetClassSetMap());
		methodToLOCMap.putAll(visitor.getMethodToLOCMap());
	} 
	
	private boolean removeFile(String absoluteFilePath) {
		if(fileToClassMap.containsKey(absoluteFilePath)) {
			Set<String> classes = fileToClassMap.get(absoluteFilePath);
			fileToClassMap.remove(absoluteFilePath);
			
			for (String c : classes) {
				types.remove(c);
				
				if (classToEntitySetMap.containsKey(c)) {
					Set<String> entities = classToEntitySetMap.get(c);
					for (String entity : entities) {
						staticEntities.remove(entity);
						accessorToAccessedFieldMap.remove(entity);
						methodToEntitySetMap.remove(entity);
						methodToTargetClassSetMap.remove(entity);
					}
					classToEntitySetMap.remove(c);
					
					Set<String> methods = classToMethodSetMap.get(c);
					for (String method : methods) {
						methodToLOCMap.remove(method);
					}
					classToMethodSetMap.remove(c);
				}
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
	
	private void replaceAccessorsByAccessedFields(Map<String, Set<String>> map) {
		for(Map.Entry<String, Set<String>> entry : map.entrySet()) {
			List<String> entitiesToRemove = new ArrayList<String>();
			List<String> entitiesToAdd = new ArrayList<String>();
			for(String entity :entry.getValue()) {
				if (accessorToAccessedFieldMap.containsKey(entity)) {
					entitiesToRemove.add(entity);
					entitiesToAdd.add(accessorToAccessedFieldMap.get(entity));
				}	
			}
			map.get(entry.getKey()).removeAll(entitiesToRemove);
			map.get(entry.getKey()).addAll(entitiesToAdd);
		}
	}
	
	private void removeSystemMemberAccesses(Map<String, Set<String>> map) {
		Pattern p = Pattern.compile(".+:(.+)");
		
		for(Map.Entry<String, Set<String>> entry : map.entrySet()) {
			List<String> entitiesToRemove = new ArrayList<String>();
			for(String entity :entry.getValue()) {
				Matcher m = p.matcher(entity);
				if (m.matches()) 
					if(types.contains(m.group(1)))
						entitiesToRemove.add(entity);
			}
			map.get(entry.getKey()).removeAll(entitiesToRemove);
		}
	}
	
	private void removeStaticEntities(Map<String, Set<String>> map) {
		for(Map.Entry<String, Set<String>> entry : map.entrySet()) {
			List<String> entitiesToRemove = new ArrayList<String>();
			for(String entity :entry.getValue()) {
				if (staticEntities.contains(entity))
					entitiesToRemove.add(entity);
			}
			map.get(entry.getKey()).removeAll(entitiesToRemove);
		}
	}
}