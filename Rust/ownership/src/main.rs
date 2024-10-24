fn main() {
    // Since x and y are both assigned to the stack, they are
    // stored in separate locations in memory.
    let x = 5;
    let _y = x;

    // In this case, since the string is stored on the heap,
    // s1 is moved to s2 and the s1 pointer is no longer valid.
    let s1 = String::from("hello");
    let s2 = s1;

    // To fix this, we can use the clone keyword to create a
    // new string that is equal to s1.
    let s3 = String::from("hello");
    let s4 = s3.clone();
    
    // This will not work because s1 is no longer valid.
    // println!("s1 = {}, s2 = {}, s3 = {}, s4 = {}", s1, s2, s3, s4);

    println!("s2 = {}, s3 = {}, s4 = {}", s2, s3, s4);

    //Here are some of the types that implement Copy:

    // All the integer types, such as u32.
    // The Boolean type, bool, with values true and false.
    // All the floating-point types, such as f64.
    // The character type, char.
    // Tuples, if they only contain types that also implement Copy. For example, (i32, i32) implements Copy, but (i32, String) does not.

    let s = String::from("hello");  // s comes into scope

    takes_ownership(s);             // s's value moves into the function...
                                    // ... and so is no longer valid here

    let x = 5;                      // x comes into scope

    makes_copy(x);                  // x would move into the function,
                                    // but i32 is Copy, so it's okay to still
                                    // use x afterward

} 
// Here, x goes out of scope, then s. But because s's value was moved, nothing
// special happens.

fn takes_ownership(some_string: String) { // some_string comes into scope
    println!("{some_string}");
}
// Here, some_string goes out of scope and `drop` is called. The backing
// memory is freed.
fn makes_copy(some_integer: i32) { // some_integer comes into scope
    println!("{some_integer}");
}
// Here, some_integer goes out of scope. Nothing special happens.