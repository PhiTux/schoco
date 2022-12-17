import static org.junit.Assert.*;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class HelloWorldTest {

	@Test
	@DisplayName("4 > 3")
	public void isGreaterTrue() {
		HelloWorld helloWorld = new HelloWorld();
		assertTrue("Num 1 is greater than Num 2", helloWorld.isGreater(4, 3));
	}
	
	@Test
	@DisplayName("Not 4 > 5")
	public void isGreaterFalse() {
		HelloWorld helloWorld = new HelloWorld();
		assertFalse("Num 1 is greater than Num 2", helloWorld.isGreater(4, 5));
	}	

}
