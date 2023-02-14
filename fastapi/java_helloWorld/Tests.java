import static org.junit.Assert.*;

//import org.junit.jupiter.api.DisplayName;
import org.junit.Test;

public class Tests {

	@Test
	// would need JUnit5 for features like @DisplayName()
	//@DisplayName("4 > 3")
	public void isGreaterTrue() {
		Schoco schoco = new Schoco();
		assertTrue("Num 1 is greater than Num 2", schoco.isGreater(4, 3));
	}
	
	@Test
	//@DisplayName("Not 4 > 5")
	public void isGreaterFalse() {
		Schoco schoco = new Schoco();
		assertFalse("Num 1 is greater than Num 2", schoco.isGreater(4, 5));
	}	

}
