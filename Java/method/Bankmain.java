package method;
import java.util.Scanner;
// main class
public class Bankmain {
public static void main(String[] args) {
   Scanner scan = new Scanner(System.in);
   // Menu starts from here
   Scanner input = new Scanner(System.in);
   System.out.println("Enter the option for the operation you need:");
   System.out.println("****************************************************");
   System.out.println("[ Options: ne - New Account de - Delete Account ]");
   System.out.println("[       dp - Deposit    wi - Withdraw      ]");
   System.out.println("[           se - Select Account ex - Quit      ]");
   
   System.out.println("press 1 to know your bank details\tpress 2 to deposit\npress 3 to withdraw\t 4 to pay loan");
    
   System.out.println("****************************************************");
   System.out.print("> ");  //indicator for user input
   String choice = input.next();
   //Options

   while(true){
   if(choice == "ne"){
   int nacc;
   int bal;
   
   System.out.print("Insert account number: ");
   nacc =input.nextInt(); //-- Input nr for array insertion
   System.out.print("Enter initial balance: ");
   bal=input.nextInt(); //-- Input nr for array insertion
   System.out.println("Current account: " + nacc + " " +  "Balance " + bal);
   int [][]array = new int[nacc][bal];   // Array for account and balance
   break;
 }
 // account selection      
 if(choice.equals("se")){
   System.out.println("Enter number of account to be selected: ");
   //user input for account nr from array
   System.out.println("Account closed.");
 }     
 //close account
 if(choice.equals("de")){
   //array selected for closing
   System.out.println("Account closed.");
 }


 // deposit
 if(choice.equals("dp")){
   System.out.print("Enter amount to deposit:  ");
   double amount = scan.nextDouble();
   if(amount <= 0){
       System.out.println("You must deposit an amount greater than 0.");
   } else {
       System.out.println("You have deposited " + (amount + Account.getBalance()));
   }
 }
 // withdrawal     
 if(choice.equals("wi")){
   System.out.print("Enter amount to be withdrawn: ");
   double amount = scan.nextDouble();
   
       if (amount > Account.getBalance()){ 
           System.out.println("You can't withdraw that amount!");
  } else if (amount <= Account.getBalance()) {
   Account.withdraw(amount);
   System.out.println("NewBalance = " + Account.getBalance());
  }
  }
//quit 
if(choice == "ex"){
   System.exit(0);
       } 
   }   // end of menu loop
scan.close();
}// end of main
} // end of class


