import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.net.InetSocketAddress;
import java.util.HashMap;
import java.util.Scanner;

public class Java_api {
	public static void main(String[] args) throws IOException {
		Java_api server = new Java_api();
	}
	
	public Java_api() throws IOException {
		HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
		server.createContext("/compile", new HttpHandler() {

			@Override
			public void handle(HttpExchange exchange) throws IOException {
				if ("POST".equals(exchange.getRequestMethod())) {

					HashMap<String, String> postData = getRequestData(exchange.getRequestBody());
					
					int exitCode = 0;
					Scanner s;
					try {
						String[] command = { "sh", "-c", "bash /app/cookies.sh 'javac -cp /app/tmp /app/tmp/Main.java' " + postData.get("timeout_cpu") + " " + postData.get("timeout_session") + "; exit" };
						Process process = Runtime.getRuntime().exec(command);
						s = new Scanner(process.getInputStream()).useDelimiter("\\A");
						exitCode = process.waitFor();
					} catch (InterruptedException e) {
						e.printStackTrace();
						exchange.sendResponseHeaders(500, -1);// Internal Server Error
						OutputStream os = exchange.getResponseBody();
						os.write("InterruptedException occured".getBytes());
						os.close();
						return;
					} catch (Exception e) {
						e.printStackTrace();
						exchange.sendResponseHeaders(501, -1);
						OutputStream os = exchange.getResponseBody();
						os.write("Exception occured".getBytes());
						os.close();
						return;
					}
					
					String output = s.hasNext() ? s.next() : "";

					String responseText = "{\"exitCode\":\"" + exitCode + "\",\"output\":\"" + output + "\"}";
					exchange.sendResponseHeaders(200, responseText.getBytes().length);
					OutputStream os = exchange.getResponseBody();
					os.write(responseText.getBytes());
					os.close();
				} else {
					exchange.sendResponseHeaders(405, -1);// 405 Method Not Allowed
				}
				exchange.close();
			}
		});

		server.createContext("/execute", new HttpHandler() {

			@Override
			public void handle(HttpExchange exchange) throws IOException {
				if ("POST".equals(exchange.getRequestMethod())) {

					HashMap<String, String> postData = getRequestData(exchange.getRequestBody());
					
					int exitCode = 0;
					Scanner s;
					try {
						String[] command = { "sh", "-c", "bash /app/cookies.sh 'java -cp /app/tmp Main' " + postData.get("timeout_cpu") + " " + postData.get("timeout_session") + "; exit" };
						Process process = Runtime.getRuntime().exec(command);
						s = new Scanner(process.getInputStream()).useDelimiter("\\A");
						exitCode = process.waitFor();
					} catch (InterruptedException e) {
						e.printStackTrace();
						exchange.sendResponseHeaders(500, -1);// Internal Server Error
						OutputStream os = exchange.getResponseBody();
						os.write("InterruptedException occured".getBytes());
						os.close();
						return;
					} catch (Exception e) {
						e.printStackTrace();
						exchange.sendResponseHeaders(501, -1);
						OutputStream os = exchange.getResponseBody();
						os.write("Exception occured".getBytes());
						os.close();
						return;
					}
					
					String output = s.hasNext() ? s.next() : "";

					//TODO: Don't return output on following line! (Could be endless...)
					String responseText = "{\"exitCode\":\"" + exitCode + "\",\"output\":\"" + output + "\"}";
					exchange.sendResponseHeaders(200, responseText.getBytes().length);
					OutputStream os = exchange.getResponseBody();
					os.write(responseText.getBytes());
					os.close();
				} else {
					exchange.sendResponseHeaders(405, -1);// 405 Method Not Allowed
				}
				exchange.close();
			}
		});

		server.setExecutor(null); // creates a default executor
		server.start();
	}
	
	
	
	private HashMap<String, String> getRequestData(InputStream is) throws IOException {
		HashMap<String, String> request = new HashMap<>();
		
		StringBuilder sb = new StringBuilder();
		int i;
		while ((i = is.read()) != -1) {
			sb.append((char) i);
		}
		String rs = sb.toString();
		if (rs.startsWith("'{") || rs.startsWith("\"{"))
			rs = rs.substring(2, rs.length()-2);
		else if (rs.startsWith("{"))
			rs = rs.substring(1, rs.length()-1);
		for (String kv : rs.split(",")) {
			kv = kv.trim();
			String key = kv.split(":")[0];
			if (key.startsWith("\"") || key.startsWith("\'"))
				key = key.substring(1, key.length()-1);
			String value = kv.split(":")[1];
			if (value.startsWith("\"") || value.startsWith("\'"))
				value = value.substring(1, value.length()-1);
			request.put(key, value);
		}
		return request;
	}
}