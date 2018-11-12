package fe;

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
	private Set<String> staticEntities = new HashSet<String>();
	private Map<String, String> accessorToAccessedFieldMap = new HashMap<String,String>();
	private Map<String, Set<String>> classToEntitySetMap = new HashMap<String,Set<String>>();
	private Map<String, Set<String>> classToMethodSetMap = new HashMap<String,Set<String>>();
	private Map<String, Set<String>> methodToEntitySetMap = new HashMap<String,Set<String>>();
	private Map<String, Set<String>> methodToTargetClassSetMap = new HashMap<String,Set<String>>();
	private Map<String, Integer> methodToLOCMap = new HashMap<String, Integer>();
	
	public Map<String, Set<String>> getClassToEntitySetMap() {
		return this.classToEntitySetMap;
	}
	
	public Map<String, Set<String>> getClassToMethodSetMap() {
		return this.classToMethodSetMap;
	}
	
	public Map<String, Set<String>> getMethodToEntitySetMap() {
		return this.methodToEntitySetMap;
	}
	
	public Map<String,Set<String>> getMethodToTargetClassSetMap() {
		return this.methodToTargetClassSetMap;
	}
	
	public Map<String, Integer> getMethodToLOCMap() {
		return this.methodToLOCMap;
	}
	
	public Set<String> getTypes() {
		return this.types;
	}
	
	public Set<String> getStaticEntities() {
		return this.staticEntities;
	}
	
	public Map<String, String> getaccessorToAccessedFieldMap() {
		return this.accessorToAccessedFieldMap;
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
		
		types.add(typeName);
		
		// Visit the class.
		ClassVisitor visitor = new ClassVisitor(typeName);
		node.accept(visitor);
		
		classToEntitySetMap.put(typeName, visitor.getEntitySet());
		classToMethodSetMap.put(typeName, visitor.getMethodSet());
		methodToEntitySetMap.putAll(visitor.getMethodToEntitySetMap());
		methodToTargetClassSetMap.putAll(visitor.getMethodToTargetClassSetMap());
		methodToLOCMap.putAll(visitor.getMethodToLOCMap());
		staticEntities.addAll(visitor.getStaticEntities());
		accessorToAccessedFieldMap.putAll(visitor.getaccessorToAccessedFieldMap());
		
		
		return true;
	}
}