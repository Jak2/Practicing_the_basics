package method;

public class Smallest_of_two {

    static int small(int a, int b)
    {
        /* //*dont need to declare again
        int a;
        int b;
        */
        int min; 
        if (a<b)
        min = a;
        else
        min = b;
        return min;
    }
    public static void main(String[] args)
    {
        int a= 10;
        int b= 20;
        int c;

        c= small(a,b);//* static reference so the method should be static
                    //* this means the method should be written static
        System.out.println(c);
        System.out.println(small(a,b));
        System.out.println(small(50,60));  
    }
}