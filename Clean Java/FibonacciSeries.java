import java.util.Scanner;


public class FibonacciSeries
{
    public static void main(String args[])
        {
            Scanner scan = new Scanner (System.in);   
            int first_num=0, second_num=1,sum=0;
            
            System.out.println("enter the size of the fibonacci series");
            int n=scan.nextInt();

            System.out.println(first_num+"\n"+second_num);
            for(int i=0;i<n-2;i++)
            {
                sum=first_num+second_num;
                System.out.println(sum);
                first_num=second_num;
                second_num=sum;
            }
            

        
            scan.close();
        }
}