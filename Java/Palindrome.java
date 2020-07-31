import java.util.Scanner;

public class Palindrome {
    public static void main(String[]args)
    {
        Scanner sc=new Scanner(System.in);
        System.out.println("enter a number");
        int entered_number= sc.nextInt();
        int rev=0,count= 0;
        int a=entered_number;
        while(a!=0)
        {
            int rem=a%10;
            if(rem!=0)
                {count++;}  
            rev=rev*10+rem;
            a=a/10;
        }
        System.out.println("length of entered number is "+count);
        if(rev==entered_number)
        {
            System.out.println(entered_number+"is an armstrong number");
        }
        else
        {
            System.out.println("entered number is not an armstrong number");
        }
        
        sc.close();
    }
    
}