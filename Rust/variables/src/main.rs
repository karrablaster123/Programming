fn main() {
    let mut x = 5;
    println!("x = {x}");
    x = 6;
    println!("x = {x}");
    // Constants
    const THREE_HOURS_IN_SECONDS: u32 = 60 * 60 * 3;

    // Shadowing
    shadowing();
}

fn shadowing() {
    let x = 5;

    let x = x + 1;

    {
        let x = x * 2;
        println!("The value of x in the inner scope is: {x}");
    }

    println!("The value of x is: {x}");
}

fn shadowing_2() {
    // Benefits of Shadowing
    let spaces = "   ";
    let spaces = spaces.len();
}
