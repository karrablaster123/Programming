fn main() {
    let mut s = String::from("hello world");

    let word = first_word(&s);
    println!("the first word is: {} ", word);
    s.clear(); // error!
    // This line will cause a compile-time error
    // println!("the first word is: {word}");
}

fn first_word(s: &String) -> &str { // &str = string slice
    let bytes = s.as_bytes();

    for (i, &item) in bytes.iter().enumerate() {
        if item == b' ' {
            return &s[0..i];
        }
    }

    &s[..]
}