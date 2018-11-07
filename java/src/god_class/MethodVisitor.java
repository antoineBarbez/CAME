package god_class;

import java.util.ArrayList;
import java.util.HashSet;
import java.util.List;
import java.util.Set;

import org.eclipse.jdt.core.dom.ASTNode;
import org.eclipse.jdt.core.dom.ASTVisitor;
import org.eclipse.jdt.core.dom.BreakStatement;
import org.eclipse.jdt.core.dom.CatchClause;
import org.eclipse.jdt.core.dom.ConditionalExpression;
import org.eclipse.jdt.core.dom.ContinueStatement;
import org.eclipse.jdt.core.dom.DoStatement;
import org.eclipse.jdt.core.dom.EnhancedForStatement;
import org.eclipse.jdt.core.dom.ExpressionStatement;
import org.eclipse.jdt.core.dom.FieldAccess;
import org.eclipse.jdt.core.dom.ForStatement;
import org.eclipse.jdt.core.dom.IBinding;
import org.eclipse.jdt.core.dom.IMethodBinding;
import org.eclipse.jdt.core.dom.ITypeBinding;
import org.eclipse.jdt.core.dom.IVariableBinding;
import org.eclipse.jdt.core.dom.IfStatement;
import org.eclipse.jdt.core.dom.MethodInvocation;
import org.eclipse.jdt.core.dom.ReturnStatement;
import org.eclipse.jdt.core.dom.SimpleName;
import org.eclipse.jdt.core.dom.SwitchCase;
import org.eclipse.jdt.core.dom.SwitchStatement;
import org.eclipse.jdt.core.dom.VariableDeclarationStatement;
import org.eclipse.jdt.core.dom.WhileStatement;

public class MethodVisitor extends ASTVisitor {
	private Set<String> accessedAttributes = new HashSet<String>();
	private Set<String> invokedMethods = new HashSet<String>();
	private Set<String> accessedClasses = new HashSet<String>();
	
	public Set<String> getAccessedAttributes() {
		return this.accessedAttributes;
	}
	
	public Set<String> getInvokedMethods() {
		return this.invokedMethods;
	}
	
	public Set<String> getAccessedClasses() {
		return this.accessedClasses;
	}
	
	private List<ASTNode> abstractStatements = new ArrayList<ASTNode>();
	private List<ASTNode> methodInvocations = new ArrayList<ASTNode>();
	private List<ASTNode> localVariableDeclarations = new ArrayList<ASTNode>();
	private List<String> localVariableInstructions = new ArrayList<String>();
	
	public List<ASTNode> getAbstractSatements() {
		return this.abstractStatements;
	}
	
	public List<ASTNode> getMethodInvocations() {
		return this.methodInvocations;
	}
	
	public List<String> getLocalVariableInstructions() {
		return this.localVariableInstructions;
	}
	
	public List<ASTNode> getLocalVariableDeclarations() {
		return this.localVariableDeclarations;
	}
	
	
	@Override
	public boolean visit(BreakStatement node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(ContinueStatement node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(ReturnStatement node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(DoStatement node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(EnhancedForStatement node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(ForStatement node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(IfStatement node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(WhileStatement node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(SwitchStatement node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(SwitchCase node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(CatchClause node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(ConditionalExpression node) {
		abstractStatements.add(node);
		return true;
	}

	@Override
	public boolean visit(ExpressionStatement node) {
		abstractStatements.add(node);
		return true;
	}
	
	@Override
	public boolean visit(MethodInvocation node) {
		methodInvocations.add(node);
		return true;
	}
	
	@Override 
	public boolean visit(FieldAccess node) {
		IVariableBinding varBind = node.resolveFieldBinding();
		
		if (varBind == null) {
			return true;
		}
		
		ITypeBinding decClassBind = varBind.getDeclaringClass();
		
		if (decClassBind == null) {
			return true;
		}
		
		String attributeName = varBind.getName();
		String declaringClass;
		if (decClassBind.isNested()) {
			declaringClass = decClassBind.getDeclaringClass().getQualifiedName();
		}else {
			declaringClass = decClassBind.getQualifiedName();
		}
		
		
		accessedAttributes.add(declaringClass + "." + attributeName);
		return true;
	}
	
	@Override
	public boolean visit(VariableDeclarationStatement node) {
		localVariableDeclarations.add(node);
		return true;
	}
	
	@Override
	public boolean visit(SimpleName node) {
		IBinding bind = node.resolveBinding();
		if (bind == null) {
			return true;
		}
	
		boolean isAttributeAccess = false;
		boolean isMethodInvocation = false;
		String entity = null;
		ITypeBinding decClassBind = null;
		if (bind.getKind() == IBinding.VARIABLE) {
			IVariableBinding varBind = (IVariableBinding) bind;
			
			entity = varBind.getName();
			
			if (varBind.isField()) {
				
				decClassBind = varBind.getDeclaringClass();
				isAttributeAccess = true;
			}else{
				localVariableInstructions.add(entity);
			}
		}else if (bind.getKind() == IBinding.METHOD) {
			isMethodInvocation = true;
			IMethodBinding mBind = (IMethodBinding) bind;

			List<String> params = new ArrayList<>();
			for (ITypeBinding paramType : mBind.getParameterTypes()) {
				params.add(paramType.getQualifiedName());
			}
			
			StringBuffer buffer = new StringBuffer();
			buffer.append(mBind.getName());
			buffer.append("(");
			buffer.append(String.join(", ", params));
			buffer.append(")");
			
			String methodName = buffer.toString();
			
			entity = methodName;
			decClassBind = mBind.getDeclaringClass();
		}
		
		if (decClassBind == null) {
			return true;
		}
		
		String declaringClass;
		if (decClassBind.isNested()) {
			declaringClass = decClassBind.getDeclaringClass().getQualifiedName();
		}else {
			declaringClass = decClassBind.getQualifiedName();
		}
		
		if (isAttributeAccess) {
			accessedAttributes.add(declaringClass + "." + entity);
		}
		
		if (isMethodInvocation) {
			invokedMethods.add(declaringClass + "." + entity);
		}
		
		accessedClasses.add(declaringClass);
		
		return true;
	}
}