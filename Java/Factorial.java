import java.util.Scanner;

public class Factorial {
    public static void main(String []args)
    {
        Scanner sc = new Scanner(System.in); 
        int number,i;
        int fact=1;

        System.out.println("enter a number");
        number= sc.nextInt();

        for(i=1;i<=number;i++)
        {
            fact=fact*i;
        }
        System.out.println("factorial of "+number+" is "+fact);

    

        sc.close();
    }
}