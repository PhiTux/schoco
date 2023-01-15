import static org.junit.Assert.*;

import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

class MainTest {

	@Test
	// would need JUnit5 for features like @DisplayName()
	//@DisplayName("4 > 3")
	public void isGreaterTrue() {
		Main helloWorld = new Main();
		assertTrue("Num 1 is greater than Num 2", main.isGreater(4, 3));
	}
	
	@Test
	//@DisplayName("Not 4 > 5")
	public void isGreaterFalse() {
		Main helloWorld = new Main();
		assertFalse("Num 1 is greater than Num 2", main.isGreater(4, 5));
	}	

}
