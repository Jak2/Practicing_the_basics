import java.util.Scanner;

public class FibonacciSeriesRecursion {

    static  int first=0, second=1, fib=0; 
    public static int fib(int n)
    {
        if(n==0)
            {
                return 0;
            }
        if(n==1)
            {
                return 1;
            }
        if(n==2)
            {
                return 2;
            }
        return fib = fib(n-1)+fib(n-2);      
    }
    
    public static void main(String []args)
    {
        Scanner scan = new Scanner(System.in);
        
        System.out.println("enter the length of fibonacci series");
        int n= scan.nextInt();

        for(int i=0;i<n;i++)
        System.out.println(fib(i));
        
        scan.close();
    }

}