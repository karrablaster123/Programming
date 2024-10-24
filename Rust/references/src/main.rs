fn main() {
    let s1 = String::from("hello");

    let len = calculate_length(&s1); // pass in a reference. s1 does not go out of scope

    println!("The length of '{s1}' is {len}.");

    let mut s = String::from("hello");

    change(&mut s); // Each variable can only have one mutable reference in a scope.

    println!("{s}");
}

fn calculate_length(s: &String) -> usize {
    s.len()
}

fn change(some_string: &mut String) { // Only by using mut, you can change the value
    some_string.push_str(", world");
}

