import com.sun.net.httpserver.HttpServer;
import com.sun.net.httpserver.HttpExchange;
import com.sun.net.httpserver.HttpHandler;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.InetSocketAddress;
import java.util.HashMap;
import java.util.stream.Collectors;

public class Java_api {
	public static void main(String[] args) throws IOException, InterruptedException {
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
					String stdout = "";

					try {
						String[] command = { "sh", "-c", "bash /app/cookies.sh 'javac -cp /app/tmp/:/usr/share/java/junit.jar /app/tmp/*.java' " 
						+ postData.get("timeout_cpu") 
						+ " " 
						+ postData.get("timeout_session") 
						+ (postData.get("save_output").trim().equals("true") ? " ; echo '\nschoco compilation finished SBsodjpFo43E5Y7d'" : "") 
						+ "; exit" }; // random string to indicate end of execution

						Process p;
						
						if (postData.get("save_output").trim().equals("true")) {
							p = new ProcessBuilder().redirectErrorStream(true).command(command).start();

							BufferedReader reader = 
											new BufferedReader(new InputStreamReader(p.getInputStream()));
							StringBuilder builder = new StringBuilder();
							String line = null;
						
							while ((line = reader.readLine()) != null) {
								if (line.equals("schoco compilation finished SBsodjpFo43E5Y7d")) break;
								builder.append(line);
								builder.append(System.getProperty("line.separator"));
							}
						
							stdout = builder.toString();
						} else {
							p = new ProcessBuilder().inheritIO().command(command).start();
						}

						exitCode = p.waitFor();
						System.out.flush();

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
					
					String responseText = "{\"exitCode\":\"" + exitCode + (postData.get("save_output").trim().equals("true") ? ("\", \"stdout\":\"" + stdout.replaceAll("\"","\\\\\"")) : "") + "\"}";
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
					String stdout = "";

					try {
						String[] command = { "sh", "-c", "bash /app/cookies.sh 'java -Djava.security.manager=default -cp /app/tmp Schoco' " 
						+ postData.get("timeout_cpu") 
						+ " " 
						+ postData.get("timeout_session") 
						+ (postData.get("save_output").trim().equals("true") ? " ; echo '\nschoco execution finished JVXjUq5wpdxDTki5'" : "")
						+ "; exit" };

						Process p; 
						
						if (postData.get("save_output").trim().equals("true")) {
							p = new ProcessBuilder().redirectErrorStream(true).command(command).start();

							BufferedReader reader = 
											new BufferedReader(new InputStreamReader(p.getInputStream()));
							StringBuilder builder = new StringBuilder();
							String line = null;
						
							while ((line = reader.readLine()) != null) {
								if (line.equals("schoco execution finished JVXjUq5wpdxDTki5")) break;
								builder.append(line);
								builder.append(System.getProperty("line.separator"));
							}
						
							stdout = builder.toString();
						} else {
							p = new ProcessBuilder().inheritIO().command(command).start();
						}
						
						exitCode = p.waitFor();
						System.out.flush();

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

					String responseText = "{\"exitCode\":\"" + exitCode + (postData.get("save_output").trim().equals("true") ? ("\", \"stdout\":\"" + stdout.replaceAll("\"","\\\\\"")) : "") + "\"}";
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

		server.createContext("/test", new HttpHandler() {

			@Override
			public void handle(HttpExchange exchange) throws IOException {
				if ("POST".equals(exchange.getRequestMethod())) {

					HashMap<String, String> postData = getRequestData(exchange.getRequestBody());
					
					int exitCode = 0;
					String stdout;

					try {
						String[] command = { "sh", "-c", "bash /app/cookies.sh 'java -cp /app/tmp:/usr/share/java/junit.jar:/app/hamcrest.jar org.junit.runner.JUnitCore Tests' " + postData.get("timeout_cpu") + " " + postData.get("timeout_session") + " ; echo '\nschoco JUnit finished'; exit" };
						Process p = new ProcessBuilder().redirectErrorStream(true).command(command).start();

						BufferedReader reader = 
										new BufferedReader(new InputStreamReader(p.getInputStream()));
						StringBuilder builder = new StringBuilder();
						String line = null;
						
						while ((line = reader.readLine()) != null) {
							if (line.equals("schoco JUnit finished")) break;
							//System.out.println(line);
							//System.out.flush();
							builder.append(line);
							builder.append(System.getProperty("line.separator"));
						}

						stdout = builder.toString();

						exitCode = p.waitFor();
						System.out.flush();

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

					String responseText = "{\"exitCode\":\"" + exitCode + "\", \"stdout\":\"" + stdout + "\"}";
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