package variables;

public class Local_variables {
    public static void main(String []args)
    {

         //* int size is 4bytes
        //* float size is 4 bytes
        //* double size is 8bytes so mostly use double 
        //*char size is 2bytes

        int a = 10;
        float b=a;
        System.out.println(b);

        //! float c= 20.9 error= Exception in thread "main" java.lang.Error: Unresolved compilation problem: 
        // !     Type mismatch: cannot convert from double to float
        double c=20.9;
        int d=(int)c;
        System.out.println(d);

        int e = 29;
        byte f = (byte)e;
        System.out.println(f);

        byte g = 10;
        byte h  = 20;
      //! byte i= g+h; Exception in thread "main" java.lang.Error: Unresolved compilation problem: 
  //!      Type mismatch: cannot convert from int to byte 
        byte i = (byte)(g+h);
        System.out.println(i);


    }

}