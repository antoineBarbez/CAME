package fe;

import java.util.Arrays;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

public class Utils {
	public static String getEnclosingClass(String method) {
		Pattern p = Pattern.compile("(.*\\.[A-Z]\\w*)\\.\\w+\\(");
		Matcher m = p.matcher(method);
		if(m.find()) {
			return m.group(1);
		}else {
			String[] names = method.split("\\(")[0].split("\\.");
			return String.join(".", Arrays.copyOf(names, names.length - 1));
		}
	}
	
	public static double getDistance(Set<String> set1, Set<String> set2) {
        if(set1.isEmpty() && set2.isEmpty())
            return 1.0;
        return 1.0 - (double)intersection(set1,set2).size()/(double)union(set1,set2).size();
    }

    private static Set<String> union(Set<String> set1, Set<String> set2) {
        Set<String> set = new HashSet<String>();
        set.addAll(set1);
        set.addAll(set2);
        return set;
    }

    private static Set<String> intersection(Set<String> set1, Set<String> set2) {
        Set<String> set = new HashSet<String>();
        set.addAll(set1);
        set.retainAll(set2);
        return set;
    }
}