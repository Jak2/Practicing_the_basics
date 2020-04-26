
import java.util.Scanner;

public class Palindrome {
    public static void main(String []args){
        Scanner sc= new Scanner(System.in);
        System.out.println("enter any number");
        String number = sc.nextLine();
        
        int palindrome =0, 
            mod, 
            num = Integer.parseInt(number),
            // String num = (int)number
            x=num;

        while(num>0)
        {
            mod = num%10;
            palindrome = palindrome*10 + mod;
            num = num/10;
        }
        if(palindrome==x){
            System.out.println("entered number is a palindrome");
        }
        else
            System.out.println("entered number is not a palindrome");
    }
    
}