package method;

public class Account {
private int ANumber;
private static double balance;

public Account(double initialBalance, int accno) {
    balance = initialBalance;
    ANumber = accno;
}

public void deposit (double u_amm){
    balance += u_amm;
}

public static double withdraw(double amount) {
    balance -= amount;
    return amount;
}

public static double getBalance() {
    return balance;
}
public int getAccount(){
    return ANumber;
}
}


