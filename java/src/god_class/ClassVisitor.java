package god_class;

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
import org.eclipse.jdt.core.dom.IVariableBinding;
import org.eclipse.jdt.core.dom.MethodDeclaration;
import org.eclipse.jdt.core.dom.ReturnStatement;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.SingleVariableDeclaration;
import org.eclipse.jdt.core.dom.VariableDeclarationFragment;


public class ClassVisitor extends ASTVisitor {
	private Set<String> instanceAttributes = new HashSet<String>();
	private Set<String> accessorMethods = new HashSet<String>();
	private Set<String> accessedAttributes = new HashSet<String>();
	private Set<String> invokedMethods = new HashSet<String>();
	private Set<String> accessedClasses = new HashSet<String>();
	private Map<String, Set<String>> methodToAccessedAttributesMap = new HashMap<String, Set<String>>(); 
	
	private int loc = 0;
	private String className;
	
	public ClassVisitor(String className) {
		this.className = className;
	}
	
	public int getLoc() {
		return this.loc;
	}
	
	public Set<String> getAccessorMethods() {
		return this.accessorMethods;
	}
	
	public Set<String> getAccessedAttributes() {
		return this.accessedAttributes;
	}
	
	public Set<String> getInvokedMethods() {
		return this.invokedMethods;
	}
	
	public Set<String> getAccessedClasses() {
		return this.accessedClasses;
	}
	
	public Map<String, Set<String>> getMethodToAccessedAttributesMap() {
		return this.methodToAccessedAttributesMap;
	}
	
	// Methods to compute class metrics
	
	public double computeLCOM5() {
		if (methodToAccessedAttributesMap.size() < 2 || instanceAttributes.size() == 0) {
			return 0;
		}
		
		Map<String, Set<String>> attributeToAccessingMethods = new HashMap<String, Set<String>>();
		for (String attribute : instanceAttributes) {
			attributeToAccessingMethods.put(attribute, new HashSet<String>());
		}
		
		for (Map.Entry<String, Set<String>> entry: methodToAccessedAttributesMap.entrySet()) {
			String method = entry.getKey();
			Set<String> accessedAttributesMap = entry.getValue();
			for (String attribute : instanceAttributes) {
				if (accessedAttributesMap.contains(attribute)) {
					attributeToAccessingMethods.get(attribute).add(method);
				}
			}
		}
		
		int nbMethods = methodToAccessedAttributesMap.size();
		int nbAttributes = instanceAttributes.size();
		
		int sum = 0;
		for (Map.Entry<String, Set<String>> entry: attributeToAccessingMethods.entrySet()) {
			sum += entry.getValue().size();
		}
		
		double num = nbMethods - (1f/(float)nbAttributes)*sum;
		double den = nbMethods - 1;
		
		double lcom5Value = num / den;
		
		return lcom5Value;
	}
	
	private static int countLines(String str){
	   String[] lines = str.split("\r\n|\r|\n+");
	   return  lines.length;
	}
	
	@Override
	public boolean visit(FieldDeclaration node) {
		// Ignore class attributes
		for (Object modifier : node.modifiers()) {
			if(modifier.toString().equals("static")) {
				return true;
			}
		}
		
		for (VariableDeclarationFragment vdf : (List<VariableDeclarationFragment>) node.fragments()) {
			instanceAttributes.add(className + "." + vdf.getName().getIdentifier());
		}
		
		return true;
	}
	
	@Override
	public boolean visit(MethodDeclaration node) {
		if (node.getBody() == null) {
			return true;
		}
		
		// Increment loc;
		String methodBody = node.getBody().toString();
		loc += countLines(methodBody);
		
		if (node.isConstructor()) {
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

		String methodName = buffer.toString();
				
		
		// Visit the body of the method.
		MethodVisitor visitor = new MethodVisitor();
		node.getBody().accept(visitor);
		
		accessedClasses.addAll(visitor.getAccessedClasses());
		accessedAttributes.addAll(visitor.getAccessedAttributes());
		invokedMethods.addAll(visitor.getInvokedMethods());
		methodToAccessedAttributesMap.put(methodName, visitor.getAccessedAttributes());
		
		// Check if the method is an accessor
		if (isSetter(visitor) != null && params.size() == 1) {
			accessorMethods.add(methodName);
			return true;
		}
		
		if (isGetter(visitor) != null && params.size() == 0) {
			accessorMethods.add(methodName);
			return true;
		}
		
		return true;
	}
	
	public String isGetter(MethodVisitor visitor) {
		List<ASTNode> abstractStatements = visitor.getAbstractSatements();
		if(abstractStatements.size() == 1) {
    		ASTNode node = abstractStatements.get(0);
    		if(node instanceof ReturnStatement) {
    			ReturnStatement returnStatement = (ReturnStatement) node;
    			if((returnStatement.getExpression() instanceof SimpleName || returnStatement.getExpression() instanceof FieldAccess) && visitor.getAccessedAttributes().size() == 1 && visitor.getMethodInvocations().size() == 0 &&
	    				visitor.getLocalVariableDeclarations().size() == 0 && visitor.getLocalVariableInstructions().size() == 0) {
    				return visitor.getAccessedAttributes().iterator().next();
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
    			if(expressionStatement.getExpression() instanceof Assignment && visitor.getAccessedAttributes().size() == 1 && visitor.getMethodInvocations().size() == 0 &&
        				visitor.getLocalVariableDeclarations().size() == 0 && visitor.getLocalVariableInstructions().size() == 1) {
    				Assignment assignment = (Assignment)expressionStatement.getExpression();
    				if((assignment.getLeftHandSide() instanceof SimpleName || assignment.getLeftHandSide() instanceof FieldAccess) && assignment.getRightHandSide() instanceof SimpleName)
    					return visitor.getAccessedAttributes().iterator().next();
    			}
    		}
    	}
    	return null;
	}
}