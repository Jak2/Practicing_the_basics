import java.util.Scanner;

public class Prime_number{
    public static void main(String []args){
    Scanner sc= new Scanner(System.in);

    int i,list_prime, no_of_prime, prime = 0;
    
    System.out.println("enter a number");
    int number= sc.nextInt();

    if(number%2!=0)
    {
        System.out.println("entered number is a prime number");
    
        System.out.println("shall i show the list of prime numbers till "+number);
        list_prime=sc.nextInt();
        if(list_prime==1)
        System.out.println("printing the values");
        {
                for(i=1;i<=number;i++)
                {
                    if(i%2!=0)
                    System.out.println(i);
                    
                }
        }
        System.out.println("so do you wanna know how many numbers are there till "+number);
        no_of_prime= sc.nextInt();
        if(no_of_prime==1)
        
        {

            for(i=1;i<=number;i++)
            {
                if(i%2!=0)
                prime++;
            }
            System.out.println("no of prime numbers till "+number+" are "+prime);
        }
       
    }
}
}