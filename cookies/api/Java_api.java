import com.sun.net.httpserver.HttpServer;
import java.io.IOException;
import java.io.OutputStream;
import java.net.InetSocketAddress;

public class Java_api {
    public static void main(String[] args) throws IOException {

        HttpServer server = HttpServer.create(new InetSocketAddress(8080), 0);
        server.createContext("/compile", (exchange -> {

            if ("GET".equals(exchange.getRequestMethod())) {
                
                int exitCode = 0;
                try {
                    String[] command = {"sh","-c", "bash /app/cookies.sh 'javac tmp/Main.java' 10 10; exit"};
			        Process process = Runtime.getRuntime().exec(command);
                    exitCode = process.waitFor();
                } catch (InterruptedException e) {
                    e.printStackTrace();
                }
                
                String responseText = "Exited with error code : " + exitCode;
                exchange.sendResponseHeaders(exitCode, responseText.getBytes().length);
                OutputStream output = exchange.getResponseBody();
                output.write(responseText.getBytes());
                output.flush();
            } else {
                exchange.sendResponseHeaders(405, -1);// 405 Method Not Allowed
            }
            exchange.close();
        }));


        server.setExecutor(null); // creates a default executor
        server.start();

    }
}