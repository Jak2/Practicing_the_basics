import java.util.Scanner;

public class PoundsToKilograms {
    public static void main(String []args)
    {
        //* int size is 4bytes
        //* float size is 4 bytes
        //* double size is 8bytes so mostly use double 


        Scanner scan= new Scanner(System.in);

        System.out.println("enter a number");
        double a = scan.nextDouble();
        if(a>0)
        {
          double  kilograms = 0.45359237*a;
          System.out.println(a+" pounds in kilograms = "+kilograms);
        }
        else
        {
            System.out.println("enter a number greater than zero");
        }
        scan.close();
    }
}