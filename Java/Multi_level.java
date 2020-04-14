// * 10. Write a program to demonstrate the usage of super keyword, 
// *       constructor overloading with 3 classes following multi-level inheritance

class A
{
     A(){
        System.out.println("class A");
    }
    void display(){
        System.out.println("super class A");
    }
}

class B extends A{
    B(){
        System.out.println("class B");
    }
}

class C extends B{
    C(){
        System.out.println("class C");
    }
    void show(){
        super.display();
    }
}

public class Multi_level {
    public static void main(String []args)
    {
        C object = new C();
        object.show();
    }
}