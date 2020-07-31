public class Solution 
{
public static void main(String[] args) throws IOException
{
 BufferedReader bufferedReader = new BufferedReader (new InputStreamReader (System.in));


BufferedWriter bufferedWriter = new BufferedWriter (new FileWriter(System.getenv

("OUTPUT_PATH")));


String s = bufferedReader.readLine();

int result = Result.getAnagram(s);

bufferedWriter.write(String.valueOf(result));

bufferedWriter.newLine():

bufferedReader.close();

bufferedWrIter.close();
}
}
