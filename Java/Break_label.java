class Break_label{


    public static void main(String[] args)
    {
        int a = 1;

        a1: {

            a2: {

                a3:{

                    System.out.println("we are in a1");
                    
                    System.out.println("we are in a2");
                    if (a==1)
                    break a1;
                    System.out.println("we are in a3");
                }
            }
        }
    
    int b=2;
        b1: {

            b2: {

                b3:{

                    System.out.println("we are in b1");
                    if (b==2)
                        break b2;
                }

                System.out.println("we are in b2");
            }
        
            System.out.println("we are in b3");
        
        }
    
    
    
    
    
    
    }

}