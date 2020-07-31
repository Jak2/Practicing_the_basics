
import java.util.Scanner;

abstract class BankAccount{
	protected String accountName, accountId,  address, loanId, loanType;
	
	BankAccount(String accountId, String accountName, String address, String loanId, String loanType, double loanAmount,double balance){
		this.accountId = accountId;
       		this.accountName = accountName;
		this.address=address;
		this.loanId=loanId;
		this.loanType=loanType;
		//this.loanAmount=loanAmount;
		this.balance=balance;
	}
	double balance;
	final void deposit(double amount){
		balance+=amount;

	}
	
	abstract double withdraw(double amount);
	final double balCheck(){
		return balance;
	}
}
final class SavingsBankAccount extends BankAccount{
	SavingsBankAccount(String accountId,String accountName,String address,String loanId, String loanType, double loanAmount,double balance){
		super(accountId,accountName,address,loanId,loanType,loanAmount,balance);
		System.out.println("\naccountId :"+accountId+"\taccountName :"+accountName+"\taddress :"+address+"\n\nloanId :"+loanId+"\tloanType :"+loanType+"\tloanAmount :"+loanAmount+"\n\nbalance :"+balance);
	}

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
	double payloan(double loan){
			System.out.println(accountId+" :\t"+balance);
			if((balance-loan)>=0){
				balance=balance-loan;
			return loan;
		}
		else{
			return 0.0;
		}
		
	}
}

public class Bank_program {

    public static void main(String[] args) {
		Scanner scan=new Scanner(System.in);
		
        String[] Account = {"1234567-ABCD", "Raj", "India","121448221","House Loan"};
		

        BankAccount sbacc=new SavingsBankAccount(Account[0], Account[1], Account[2],Account[3], Account[4], 100000.0, 5000.0);
		
		

		System.out.println("\nplease select what you would like to do");
		System.out.print("\n\npress 1 to know your bank details\ttype 2 to deposit\n\ntype 3 to withdraw\t\t\ttype 4 to pay loan\n>");
		int num=scan.nextInt();
		if(num==1){
			new SavingsBankAccount(Account[0], Account[1], Account[2],Account[3], Account[4], 100000.0, 5000.0);
		}

		if(num==2){
			System.out.println("enter the amount to deposit");
			double deposit_amt = scan.nextDouble();
			sbacc.deposit(deposit_amt);
			System.out.println("amount has been successfully deposited");
        	System.out.println("After Deposite(2000) Balance:"+sbacc.balCheck());
		}        

		if(num==3){

		
        System.out.println("Updated Balance:"+sbacc.balCheck());
        System.out.println("Current Balance:"+sbacc.balCheck());
		
		System.out.println("enter the amount to withdraw");
		double withdraw_amt=scan.nextDouble();
		if(sbacc.withdraw(withdraw_amt)==0)
                System.out.println("Transaction Failed!\nCurrent Balance in your account:"+sbacc.balCheck());
        else
                System.out.println("Transaction Completed!\nAfter Withdrawl"+withdraw_amt+"remaining balance is "+sbacc.balCheck());
		}

		if(num==4){
        System.out.println("Updated Balance:"+sbacc.balCheck());
        System.out.println("Current Balance:"+sbacc.balCheck());
		
		System.out.println("enter the amount to payloan");
		double pay_loan_amt=scan.nextDouble();
		SavingsBankAccount s = new SavingsBankAccount(Account[0], Account[1], Account[2],Account[3], Account[4], 100000.0, 5000.0);
		
		if(s.payloan(pay_loan_amt)<0)
                System.out.println("Transaction Failed!\nplease enter amount greater than 0");
        else
                System.out.println("Transaction Completed!\n loan paid = "+pay_loan_amt+"remaining loan is "+(100000.0-pay_loan_amt));
		}



		scan.close();
    }
    
}

