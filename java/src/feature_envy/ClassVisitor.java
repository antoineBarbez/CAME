package fe;

import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.Assignment;
import org.eclipse.jdt.core.dom.ExpressionStatement;
import org.eclipse.jdt.core.dom.FieldAccess;
import org.eclipse.jdt.core.dom.FieldDeclaration;
import org.eclipse.jdt.core.dom.ITypeBinding;
import org.eclipse.jdt.core.dom.IVariableBinding;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.ReturnStatement;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;


public class ClassVisitor extends ASTVisitor {
	private Set<String> staticEntities = new HashSet<String>();
	private Set<String> entitySet = new HashSet<String>();
	private Set<String> methodSet = new HashSet<String>();
	private Map<String, String> accessorToAccessedFieldMap = new HashMap<String,String>();
	private Map<String,Set<String>> methodToEntitySetMap = new HashMap<String,Set<String>>();
	private Map<String,Set<String>> methodToTargetClassSetMap = new HashMap<String,Set<String>>();
	private Map<String, Integer> methodToLOCMap = new HashMap<String, Integer>();
	private String className;
	
	public ClassVisitor(String className) {
		this.className = className;
	}
	
	public Set<String> getStaticEntities() {
		return this.staticEntities;
	}
	
	public Set<String> getEntitySet() {
		return this.entitySet;
	}
	
	public Set<String> getMethodSet() {
		return this.methodSet;
	}
	
	public Map<String,Set<String>> getMethodToEntitySetMap() {
		return this.methodToEntitySetMap;
	}
	
	public Map<String,Set<String>> getMethodToTargetClassSetMap() {
		return this.methodToTargetClassSetMap;
	}
	
	public Map<String, String> getaccessorToAccessedFieldMap() {
		return this.accessorToAccessedFieldMap;
	}
	
	public Map<String, Integer> getMethodToLOCMap() {
		return this.methodToLOCMap;
	}
	
	private static int countLines(String str){
	   String[] lines = str.split("\r\n|\r|\n+");
	   return  lines.length;
	}
	
	@Override
	public boolean visit(FieldDeclaration node) {
		ITypeBinding bind = node.getType().resolveBinding();
		if (bind == null) {
			return true;
		}
		
		Set<String> attributes = new HashSet<String>();
		String type = bind.getQualifiedName();
		for (VariableDeclarationFragment vdf : (List<VariableDeclarationFragment>) node.fragments()) {
			String attributeName = className + '.' + vdf.getName().getIdentifier() + ':' + type;
			
			attributes.add(attributeName);
		}
		
		for (Object modifier : node.modifiers()) {
			if(modifier.toString().equals("static")) {
				staticEntities.addAll(attributes);
				return true;
			}
		}
		
		entitySet.addAll(attributes);
		return true;
	}
	
	@Override
	public boolean visit(MethodDeclaration node) {
		if (node.getBody() == null) {
			return true;
		}
		
		// Construct the method's name.
		List<String> params = new ArrayList<>();
		for (SingleVariableDeclaration var : (List<SingleVariableDeclaration>) node.parameters()) {
			IVariableBinding varBind = var.resolveBinding();
			if (varBind == null) {
				params.add(var.toString().split("\\s+")[0]);
			}else {
				params.add(varBind.getType().getQualifiedName());
			}
		}
		Collections.sort(params, String.CASE_INSENSITIVE_ORDER);
		
		StringBuffer buffer = new StringBuffer();
		buffer.append(node.getName().getIdentifier());
		buffer.append("(");
		buffer.append(String.join(", ", params));
		buffer.append(")");

		String methodName = className + '.' + buffer.toString();
		
		methodSet.add(methodName);
		methodToLOCMap.put(methodName, new Integer(countLines(node.getBody().toString())));
		
		if (node.isConstructor()) {
			return true;
		}
		
		for (Object modifier : node.modifiers()) {
			if(modifier.toString().equals("static")) {
				staticEntities.add(methodName);
				return true;
			}
		}
		
		// Visit the body of the method.
		MethodVisitor visitor = new MethodVisitor();
		node.getBody().accept(visitor);
		
		
		// Check if the method is an accessor
		if (isSetter(visitor) != null && params.size() == 1) {
			accessorToAccessedFieldMap.put(methodName, isSetter(visitor));
			return true;
		}
		
		if (isGetter(visitor) != null && params.size() == 0) {
			accessorToAccessedFieldMap.put(methodName, isGetter(visitor));
			return true;
		}
		
		entitySet.add(methodName);
		methodToEntitySetMap.put(methodName, visitor.getEntitySet());
		methodToTargetClassSetMap.put(methodName, visitor.getTargetClassSet());
		
		return true;
	}
	
	public String isGetter(MethodVisitor visitor) {
		List<ASTNode> abstractStatements = visitor.getAbstractSatements();
		if(abstractStatements.size() == 1) {
    		ASTNode node = abstractStatements.get(0);
    		if(node instanceof ReturnStatement) {
    			ReturnStatement returnStatement = (ReturnStatement) node;
    			if((returnStatement.getExpression() instanceof SimpleName || returnStatement.getExpression() instanceof FieldAccess) && visitor.getFieldInstructions().size() == 1 && visitor.getMethodInvocations().size() == 0 &&
	    				visitor.getLocalVariableDeclarations().size() == 0 && visitor.getLocalVariableInstructions().size() == 0) {
    				return visitor.getFieldInstructions().iterator().next();
    			}
    		}
    	}
		return null;
	}
	
	public String isSetter(MethodVisitor visitor) {
		List<ASTNode> abstractStatements = visitor.getAbstractSatements();
    	if(abstractStatements.size() == 1) {
    		ASTNode node = abstractStatements.get(0);
    		if(node instanceof ExpressionStatement) {
    			ExpressionStatement expressionStatement = (ExpressionStatement)node;
    			if(expressionStatement.getExpression() instanceof Assignment && visitor.getFieldInstructions().size() == 1 && visitor.getMethodInvocations().size() == 0 &&
        				visitor.getLocalVariableDeclarations().size() == 0 && visitor.getLocalVariableInstructions().size() == 1) {
    				Assignment assignment = (Assignment)expressionStatement.getExpression();
    				if((assignment.getLeftHandSide() instanceof SimpleName || assignment.getLeftHandSide() instanceof FieldAccess) && assignment.getRightHandSide() instanceof SimpleName)
    					return visitor.getFieldInstructions().iterator().next();
    			}
    		}
    	}
    	return null;
	}
}