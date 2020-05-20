import java.util.Scanner;
import java.lang.Math;

public class Armstrong {
    public static void main(String args[])
    {
        Scanner sc= new Scanner(System.in);
        System.out.println("enter a number");
        String str= sc.nextLine();              //* taking string as input 

        double len= str.length();               //* calculating string length
        
        double number=Double.parseDouble(str);  //* converting string variable to double
        double armstrong=0;                     //* everything is taken as double cause
                                                //* exponential computation gives floatiing values
        System.out.println("entered number is "+number);
        System.out.println("length of entered number is "+len);//* prints length of the entered number

        System.out.println("type of entered value is "+str.getClass());     //* prints variable type but only works for strings
        
        double dummy_number= number;
        int mul_len;
        while(number!=0.0)
        {
            for(mul_len=1;mul_len<=len;mul_len++)
            {
                double mod=dummy_number%10;
                //System.out.println("value after each %10"+mod);
                dummy_number=dummy_number/10;
                //System.out.println("after num/10 the value of num is "+number);
                armstrong = armstrong+ Math.pow(mod,len);  
            }            
            
            if(armstrong==number)
            {
                System.out.println("the number "+number+" is an armstrong number");
            }
          
        }

    }

}

                