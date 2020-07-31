import java.util.Scanner;
import java.lang.Math;
public class Armstrong{

    public static double counter(double rem,double num)
    {
        double count=0;
        while(num>0)
        {
            rem=num%10;
            if(rem!=0)
            {
                count++;
            }
        }
        return count;
    }

    public static void main(String[]args){
        Scanner sc=new Scanner(System.in);
        System.out.println("enter the number");
        double armstrong=0,rem,arm, a=sc.nextDouble();
       // double b=a;
        while(a>0)
        {
            
            rem=a%10;
            arm=Math.pow(rem,counter(rem,a));
            armstrong = armstrong*10+arm;
        }
        if(a==armstrong)
        {
            System.out.println("armstrong number of"+a+" is "+armstrong);
        }
        else
        {
            System.out.println(a+" is not an armstrong number");
        }
    sc.close();
    }

} 
