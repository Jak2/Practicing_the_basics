package print;

public class Print_fun {
    public static String hello(String a)
    {
        return a;
    }

    public static void main(String []args)
    {
        String a = "hello there";
        System.out.println(hello(a));

        int c= 10,b=20;
        System.out.println(c+b);
        System.out.println(c+""+b);
    }

}