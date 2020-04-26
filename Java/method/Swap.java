package method;
public class Swap {
    //* public static void wap(int  , int )
    //* we cannot write like this in java
    public static int swap(int a , int b)
    {
    /* //* int a= 10; 
        //*int b =20;
        //* we cannot write like this in the method in java
        //* we need to write these in class*/
       
    System.out.println("before swapping"+a+""+b);
    int c=a;
    a=b;
    b=c;
    System.out.println("after swapping"+a+""+b);
    
    return 0;
}
    public static void main(String[]args)
    {
        int a =10;
        int b =20;
        
       /* //* System.out.println("printing values of a and b before swapping \n" "a="+a+"b="+b);
        //* we cannot write like this "" after "" in the above line 
      */
     System.out.println("printing values of a and b before swapping \n a=" + a + "\tb=" + b);
        
        //* int c = swap(a, b);
        //! The value of the local variable c is not usedJava(536870973)
        System.out.println(swap(a,b));//* swap is static reference here so the method should be static


    }


}