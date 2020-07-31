
import java.util.Scanner;

public class Main {
    public static void main(String[] args) 
    {
        Scanner scan = new Scanner(System.in);
        System.out.println("enter the size of the array");
        int i, n = scan.nextInt(), ids[] = new int[n];
        System.out.println("enter the elements of array");
        for (i = 0; i < n; i++) 
        {
            ids[i] = scan.nextInt();
        }
        System.out.println("length" + ids.length);
        System.out.println(n - 1);
        // if array is full
        if (ids.length == n) 
        {
            System.out.println("enter the no of elements to delete");
            int m = scan.nextInt();
            int number = 0;
            while (number > m - 1 && number < n)
            {
                System.out.println(ids[number]);
                number++;
            }
        }
    }

}
