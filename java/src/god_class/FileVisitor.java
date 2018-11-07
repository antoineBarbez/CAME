package god_class;

import java.util.HashMap;
import java.util.HashSet;
import java.util.Map;
import java.util.Set;

import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.PackageDeclaration;
import org.eclipse.jdt.core.dom.TypeDeclaration;

public class FileVisitor extends ASTVisitor {
	private String packageName;
	
	private Set<String> types =  new HashSet<String>();
	private Set<String> dataClasses = new HashSet<String>();
	private Set<String> accessorMethods = new HashSet<String>();
	private Map<String, Integer> classToLOCMap = new HashMap<String,Integer>();
	private Map<String, Integer> classToNMDMap = new HashMap<String,Integer>();
	private Map<String, Integer> classToNADMap = new HashMap<String,Integer>();
	private Map<String, Double> classToLCOM5Map = new HashMap<String,Double>();
	private Map<String, Set<String>> classToAccessedClassesMap = new HashMap<String, Set<String>>();
	private Map<String, Set<String>> classToAccessedAttributesMap = new HashMap<String, Set<String>>();
	private Map<String, Set<String>> classToInvokedMethodsMap = new HashMap<String, Set<String>>();
	
	
	public Map<String, Integer> getClassToLOCMap() {
		return this.classToLOCMap;
	}
	
	public Map<String, Integer> getClassToNMDMap() {
		return this.classToNMDMap;
	}
	
	public Map<String, Integer> getClassToNADMap() {
		return this.classToNADMap;
	}
	
	public Map<String, Double> getClassToLCOM5Map() {
		return this.classToLCOM5Map;
	}
	
	public Map<String, Set<String>> getClassToAccessedClassesMap() {
		return this.classToAccessedClassesMap;
	}
	
	public Map<String, Set<String>> getClassToAccessedAttributesMap() {
		return this.classToAccessedAttributesMap;
	}
	
	public Map<String, Set<String>> getClassToInvokedMethodsMap() {
		return this.classToInvokedMethodsMap;
	}
	
	public Set<String> getDataClasses() {
		return this.dataClasses;
	}
	
	public Set<String> getTypes() {
		return this.types;
	}
	
	public Set<String> getAccessorMethods() {
		return this.accessorMethods;
	} 
	
	
	
	@Override
	public boolean visit(PackageDeclaration node) {
		packageName = node.getName().getFullyQualifiedName();
		return true;
	}
	
	@Override
	public boolean visit(TypeDeclaration node) {
		// Construct the class's name.
		String typeName;
		if (packageName != null) {
			typeName = packageName + "." + node.getName().getFullyQualifiedName();
		}else {
			typeName = node.getName().getFullyQualifiedName();
		}
		
		// Ignore interfaces and inner classes.
		if (node.isInterface() || node.isMemberTypeDeclaration()) {
			return true;
		}
		
		// Visit the class.
		ClassVisitor visitor = new ClassVisitor(typeName);
		node.accept(visitor);
		
		int nbMethods = node.getMethods().length;
		int nbAttributes = node.getFields().length;
		int nbNonAccessorMethods = Integer.max(1, nbMethods - visitor.getAccessorMethods().size());
		
		double ratio = nbAttributes/nbNonAccessorMethods;
		if (ratio >= 7) {
			dataClasses.add(typeName);
		}
		
		types.add(typeName);
		accessorMethods.addAll(visitor.getAccessorMethods());
		classToLOCMap.put(typeName, new Integer(visitor.getLoc()));
		classToNMDMap.put(typeName, new Integer(nbMethods));
		classToNADMap.put(typeName, new Integer(nbAttributes));
		classToLCOM5Map.put(typeName, new Double(visitor.computeLCOM5()));
		classToAccessedClassesMap.put(typeName, visitor.getAccessedClasses());
		classToAccessedAttributesMap.put(typeName, visitor.getAccessedAttributes());
		classToInvokedMethodsMap.put(typeName, visitor.getInvokedMethods());
		
		return true;
	}
}