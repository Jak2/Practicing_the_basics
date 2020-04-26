import java.util.Scanner;

public class Even_number {
    public static void main(String []args){
    
    int i, series,list_even;
    int even = 0;
    Scanner sc= new Scanner(System.in);
    
    System.out.println("enter the a number");
    int number= sc.nextInt();

    if(number%2 ==0)
    {
        System.out.println("entered numer is a even number");
        
        System.out.println("do you want to see the series of even numbers from 0 to"+number+"\n yes or no");
        System.out.println("enter 1 for yes and 0 for no");
        series = sc.nextInt();
        
        if(series == 1)
        {            
            System.out.println("even numbers from 0 to "+number+" are");
        
            for(i=2;i<=number;i++){

                if(i%2 ==0)
                System.out.println(i);      
                
             }
        }
        
        System.out.println("shall i show you the no of even numbers till "+number);
        System.out.println("type 1 for yes and 0 for no");
        list_even = sc.nextInt();
        
        if(list_even == 1)
        {
            for(i=2;i<=number;i++){
                if(i%2==0)
                even++;
            }
         System.out.println("total no of even numbers till "+number+" are: "+even);
        }
}

}}