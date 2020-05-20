import java.util.Scanner;

public class Fibonacci 
{
    public static void main(String []args)
    {
            Scanner sc= new Scanner(System.in);
        int i,a=0,b=1;
        int fib=0;
        System.out.println("enter the a number");
        int n = sc.nextInt();
        
        System.out.println("fibonacci series =");
        System.out.println(a+"\n"+b);
        
        for(i=1;i<n-1;i++)// *managing the list 
        {
            fib = fib+1;
            System.out.println(fib);
        }
        sc.close();

    }
}