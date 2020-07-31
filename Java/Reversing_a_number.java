import java.util.Scanner;

public class Reversing_a_number {
    public static void main(String[]args)
    {
        Scanner sc = new Scanner(System.in);
        System.out.println("enter the value to reverse");
        int a = sc.nextInt();

        int rev=0;
        while(a!=0){

        int rem=a%10;
      //  System.out.println("removing "+rem);
        a=a/10;
        
        rev = rev*10+rem;
      //  System.out.println("reversing value ="+rev);
        
        }//for(int i=0;i<n)
        
        System.out.println(rev);
        sc.close();
    }
}