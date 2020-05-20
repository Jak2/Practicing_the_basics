import java.lang.Math;
class He{
    public static void main(String args[]){
        double a=10;
        double b=2;

        System.out.println("a pow b "+Math.pow(a,b));
    }
}



import java.util.Scanner;

public class Typecasting {

    public static void main(String []args)
    {
        Scanner sc = new Scanner(System.in);
        System.out.println("type casting = changing one type of data to another type\n\n you should keep compatibility in mind, java automatically converts one type of data another type, if the data type is not compatible then you have to convert them using explicit cnversion ");
        System.out.println("1. widening casting\n2. narrowing casting ");
        System.out.println("would you like to know more y or n");
        char a = sc.next().charAt(0);

       
        char a1='y', b1='n';
        
        //* the user will enter y and the value of a1 is y
        if(a1==a)
        {
            System.out.println("Widening casting also called implicit type casting\n"+
            "it is converting small variable type to large variable types\n"+
            "byte->short->char->int->long->float->double\n"+
            "and don't forget the compatibility\n"+
            "numeric is not compatiable with char,boolean\n boolean and char are not compatiable with each other"+
            
            "would you like know about narrow typecasting y or n"
            ); 

            char narrowtypecating = sc.next().charAt(0);
            //* the user will enter y and the value of a1 is y
            if(narrowtypecating == a1)
            {      
                System.out.println("narrow typecasting also called explicit typecasting\n"+
                "used to convert large variable to small variable\n"+
                "double->float->long->int->char->short->byte\n"+
                "used to convert non compatiable variables"
                );
            }
  
        }
        
       
       
       
        System.out.println("would you like to see them in action y or n");
        char implementation = sc.next().charAt(0);
        //* the user will enter y and the value of a1 is y
        
        int int_value;
        String string_value;
        char char_value;
        double double_value;
        float float_value;        
        String i,f,c,s;
        
        if(implementation==a1)
        {
            char variable_type;
            System.out.println("enter the variable type");
            System.out.println("type any one of these proposed names\n"+
            "i for integer\n\t"+
            "f for float\n\t"+ 
            "s for String\n\t"+
            "c for character");

            variable_type = sc.next().charAt(0);        
            System.out.println("");
          
            int zy=0;
            

            swtich(variable_type){

                case i:
                    System.out.println("widening_typecasting or implicit type casting");
                    System.out.println("enter a value");
                    int_value = sc.nextInt()
                    float_value = int_value;
                    System.out.println("converted integer "+int_value+" to float"+float_value);
                    break;

                case f:
                System.out.println("narrow typecasting");
                System.out.println("enter a value");
                double_value = sc.nextDouble();
                double_value= (int)float_value;
                System.out.println("entered float value ="+int_value+" is converted to integer ="+int_value);
                break;

                case s:
                System.out.println("widening_typecasting or implicit type casting");
                System.out.println("enter a value");
                string_value = sc.nextLine();
                int_value = Integer.parseInt(string_value);
               //*int_value = Integer.valueOf(string_value); we can also use this to convert 
                System.out.println("there is no widening_typecasting b/n string and int\n"+
                "hence we are using parse\n integer value= "+int_value);
                //string to char
                char_value = string_value.charAt(0);
                System.out.println("char value"+char_value);
                break;

                case c:
                System.out.println("widening typecasting\n enter a number");
                System.out.println("enter a value");
                char_value = sc.next().charAt(0);
                float_value= char_value;

                default: 
                System.out.println("entered value cannot be processed");
            }
        
        }
    
    }
}


