import java.util.Scanner;

public class Swap{
    public static void main(String []args)
    {
        Scanner sc= new Scanner(System.in);
        System.out.println("enter the values to swap");
        int a = sc.nextInt();
        int b = sc.nextInt();
        System.out.println("entered values of a and b are"+a+""+b);
        int c = a;
        a=b;
        b=c;
        System.out.println("after swapping \nnew value of a = "+a+" b= "+b);
        sc.close();
    }
}