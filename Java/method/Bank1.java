package method;
import java.util.Scanner;
import java.lang.Object;

public class Bank1 {

 


    final class SavingsBankAccount extends Bank1{
        SavingsBankAccount(String accountId,String accountName,String address,String loanId, String loanType, double loanAmount,double balance){
            super(accountId,accountName,address,loanId,loanType,loanAmount,balance);
        }
            @Override
        double withdraw(double amount){
            System.out.println(accountId+" :\t"+balance);
            if((balance-amount)>=0){
                balance=balance-amount;
                return amount;
            }
            else{
                return 0.0;
            }
            
        }
    }
    
    public static void  main(String[]args){
    
    double acc_num, loan_amt;
    Scanner scan =new Scanner(System.in);
  
    
    System.out.println("welcome to the bank");

    String[] Account = {"1234567-ABCD", "Raj", "India","121448221","House Loan"};

    BankAccount sbacc=new SavingsBankAccount(Account[0], Account[1], Account[2],Account[3], Account[4], 100000.00, 5000.0);

    System.out.println("please select what you would like to do");
    System.out.println("press 1 to know your bank details\tpress 2 to deposit\npress 3 to withdraw\t 4 to pay loan");
    int input=scan.nextInt();
   
    }
}