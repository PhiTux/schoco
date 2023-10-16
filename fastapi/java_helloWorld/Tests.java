import static org.junit.Assert.*;
import org.junit.BeforeClass;
import org.junit.Test;

/**
 * ⭐⭐⭐
 *  This class / file is NOT visible to students.
 *  It is the only file which may contain the JUnit-Tests.
 *  You can NOT rename this file.
 * ⭐⭐⭐
 */
public class Tests {
	/** 🛑 don't touch the following code-block!!
     *  It activates the security-manager which ensures limited rights of student's code during Testing. */
    @BeforeClass
    public static void setUp() {
        System.setSecurityManager(new SecurityManager());
    }
	/* 🛑 end of security code
	 *================================================*/


	// Two examples
	@Test
	public void isGreaterTrue() {
		/*Schoco schoco = new Schoco();
		assertTrue("Num 1 is greater than Num 2", schoco.isGreater(4, 3));
		assertTrue(schoco.isGreater(4, 3));*/
	}
	
	@Test
	public void isGreaterFalse() {
		/*Schoco schoco = new Schoco();
		assertEquals(4, schoco.addition(1, 3));*/
	}	

}
