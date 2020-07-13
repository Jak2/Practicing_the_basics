import java.util.Scanner;


public class Sum_of_N_numbers {
    public static void main(String []args)
    {
        Scanner s= new Scanner(System.in);
        int sum=0;

        System.out.println("enter the no of values to add");
        int no_of_values_to_add = s.nextInt();
        if (no_of_values_to_add==1)
            {
                System.out.println("are you kidding me or what..! \nyou need more than one number to do addition\ngo to your room and think what you did");   
            }
       else
            {    
                int input[]= new int[no_of_values_to_add];
                System.out.println("enter the values");
                int dummy_value;
                    for(dummy_value=0; dummy_value<no_of_values_to_add; dummy_value++)
                        {
                            input[dummy_value]= s.nextInt();
                            sum = sum + input[dummy_value];
                        }
                System.out.print("sum of ");
                    for(dummy_value=0;dummy_value<no_of_values_to_add-2;dummy_value++)
                        {
                            System.out.print(input[dummy_value]+",");
                            
                        }
                    while(dummy_value<no_of_values_to_add-1)
                        {
                            System.out.print(input[dummy_value]);
                            break;
                        }
                dummy_value=no_of_values_to_add-1;
                System.out.print(" and "+input[dummy_value]);
                System.out.print(" is "+sum+"\n\n\n");
            }
            s.close();
        }   
    
}