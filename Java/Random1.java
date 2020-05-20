
import java.util.Random;

public class Random1 {

   public static void main( String args[] ) {
      Random num = new Random();
      int res;
      for ( int i = 1; i <= 15; i++ ) {
         res = 1 + num.nextInt(10000);
         System.out.printf( "%d  ", res );      
      }
   }
}
    
}