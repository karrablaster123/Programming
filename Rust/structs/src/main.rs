struct User {
    active: bool,
    username: String,
    email: String,
    sign_in_count: u64,
}
// Tuple struct
struct Color(i32, i32, i32);
struct Point(i32, i32, i32);
fn main() {
    let mut user1    = User {
        email: String::from("a@b.com"),
        username: String::from("someusername123"),
        active: true,
        sign_in_count: 1,
    };
    user1.email = String::from("c@d.com");
    // Struct update syntax
    let user2 = User {
        email: String::from("e@f.com"),
        ..user1
    };
    // This won't work since the String type is moved from user1 to user2
    // println!("user1.email: {}, user1.username: {}", user1.email, user1.username);
    println!("user2.email: {}, user2.username: {}", user2.email, user2.username);

    let black = Color(0, 0, 0);
    let origin = Point(0, 0, 0);
    // a function that takes a parameter 
    // of type Color cannot take a Point as an argument, 
    // even though both types are made up of three i32 values
}

fn build_user(email: String, username: String) -> User {
    User {
        email,
        username,
        active: true,
        sign_in_count: 1,
    }
}