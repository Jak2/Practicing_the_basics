import java.util.ArrayList;
import java.util.HashSet;
import java.util.Iterator;
import java.util.List;
import java.util.Scanner;
import java.util.Set;

public class Main {

    public static int deleteItems(List<Integer> list, int m) {
        for (int i = 0; i < m; i++) {
            list.remove(i);
        }
        Set<Integer> set = new HashSet<>();
        Iterator<Integer> i = list.iterator();

        while (i.hasNext()) {
            set.add(i.next());
        }

        return set.size();
    }

    public static void main(String[] args) {
        Scanner scan = new Scanner(System.in);
        ArrayList<Integer> list = new ArrayList<Integer>();
        for (int i = 0; i < 6; i++) {
            list.add(scan.nextInt());
        }

        System.out.println("\n" + deleteItems(list, 2));
    }

    
}