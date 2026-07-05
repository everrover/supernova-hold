//search
//attack
//lamp
//matches
//walk
//
//POST /action.php HTTP/1.1
//Host: 10.48.189.50
//Content-Length: 11
//Cache-Control: max-age=0
//Accept-Language: en-US,en;q=0.9
//Origin: http://10.48.189.50
//Content-Type: application/x-www-form-urlencoded
//Upgrade-Insecure-Requests: 1
//User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36
//Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
//Referer: http://10.48.189.50/
//Accept-Encoding: gzip, deflate, br
//Connection: keep-alive

import java.util.*;
import java.io.*;
import java.io.IOException;
import java.io.InputStream;
import java.net.ServerSocket;
import java.net.Socket;
import java.net.URL;
import java.net.URLConnection;
import org.apache.commons.io.IOUtils;
import java.util.Scanner;
import java.util.logging.Level;
import java.util.logging.Logger;
public class RPG {
	private static final int port = 3333;
	private static Socket connectionSocket;
	private static InputStream is;
	private static OutputStream os;
	private static Scanner scanner;
	private static PrintWriter serverPrintOut;
	public static void main(String[] args) {
		try (ServerSocket serverSocket = new ServerSocket(port)) {
			while(true) {
				connectionSocket = serverSocket.accept();
				is = connectionSocket.getInputStream();
				os = connectionSocket.getOutputStream();
				scanner = new Scanner(is, "UTF-8");
				serverPrintOut = new PrintWriter(new OutputStreamWriter(os, "UTF-8"), true);
				try {
					serverPrintOut.println("You find yourself in a cave, what do you do?");
					String s = scanner.nextLine();
					URL url = new URL("http://cave.thm/" + s);
					URLConnection con = url.openConnection();
					InputStream in = con.getInputStream();
					String encoding = con.getContentEncoding();
					encoding = encoding == null ? "UTF-8" : encoding;
					String string = IOUtils.toString(in, encoding);
					string = string.replace("\n", "").replace("\r", "").replace(" ", "");
					Action action = (Action) Serialize.fromString(string);
					action.action();
					serverPrintOut.println(action.output);
				} catch (Exception ex) {
					serverPrintOut.println("Nothing happens");
				}
				connectionSocket.close();
			}
		} catch (IOException e) {
			e.printStackTrace();
		}
	}
}
class Action implements Serializable {
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
class Serialize {
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
POST /action.php HTTP/1.1
Host: 10.48.189.50
Content-Length: 11
Cache-Control: max-age=0
Accept-Language: en-US,en;q=0.9
Origin: http://10.48.189.50
Content-Type: application/x-www-form-urlencoded
Upgrade-Insecure-Requests: 1
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7
Referer: http://10.48.189.50/
Accept-Encoding: gzip, deflate, br
Connection: keep-alive

action=walk
