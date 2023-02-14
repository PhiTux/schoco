public class Schoco {

	public Schoco() {
		System.out.println("Hello World");
	}

	public static void main(String[] args) {
		Schoco testObjekt = new Schoco(); 
	}

	/**
	 * 
	 * @param num1
	 * @param num2
	 * @return returns true, if num1 is greater than num2
	 */
	public boolean isGreater(int num1, int num2) {
		return num1 > num2;
	}
}
