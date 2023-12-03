import static org.junit.Assert.*;
import org.junit.BeforeClass;
import org.junit.Test;

// 🚀 Im Wiki gibts eine Anleitung: https://github.com/PhiTux/schoco/wiki/JUnit-Tests-anlegen-%28de%29

/**
 * ⭐⭐⭐
 *  Diese Klasse / Datei ist für die Schüler/innen NICHT sichtbar.
 *  Sie ist die einzige Datei, die JUnit-Tests enthalten darf.
 *  Sie kann NICHT umbenannt werden.
 * ⭐⭐⭐
 */
public class Tests {
	/** 🛑 Ändere nichts an diesem ersten Codeblock!!
	 *  Er aktiviert den Security-Manager, der die Rechte des Schülercodes während der Tests einschränkt. 
	 *  Dadurch können Sicherheitslücken verhindert werden. */
    @BeforeClass
    public static void setUp() {
        System.setSecurityManager(new SecurityManager());
    }
	/* 🛑 Ende des Security-Codes
	 *================================================*/


	// Zwei Beispiele für JUnit-Tests
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
