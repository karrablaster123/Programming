fn main() {
    println!("Hello, world!");
    another_function();
    param_function(5);
    print_labeled_measurement(5, 'h');
    print_labelled_measurement(7, 'm');
    let y: i32 = {
        let x: i32 = 3;
        x + 1
    };

    println!("The value of y is: {y}");
    println!("The value of five() is: {}", five());

}

fn another_function() {
    println!("Another function.");
}
fn param_function(x: i32) {
    println!("The value of x is: {}", x);
}
fn print_labeled_measurement(value: i32, unit_label: char) {
    println!("The measurement is: {}{}", value, unit_label);
}
fn print_labelled_measurement(value: i32, unit_label: char) {
    println!("The measurement is: {value}{unit_label}");
}
fn five() -> i32 {
    5 // Will not work with a semicolon as it will make it a statement and not a return value.
}