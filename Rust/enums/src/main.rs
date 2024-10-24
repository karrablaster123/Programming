enum IPAddressKind {
    V4,
    V6,
}

struct IPAddress {
    kind: IPAddressKind,
    address: String,
}

let home = IPAddress {
    kind: IPAddressKind::V4,
    address: String::from("127.0.0.1"),
};

let loopback = IPAddress {
    kind: IPAddressKind::V6,
    address: String::from("::1"),
};

// Simpler Implementation

enum IpAddr {
    V4(String),
    V6(String),
}

let home = IpAddr::V4(String::from("127.0.0.1"));
let loopback = IpAddr::V6(String::from("::1"));

// Alternative

enum IpAddr2 {
    V4(u8, u8, u8, u8),
    V6(String),
}

let home = IpAddr2::V4(127, 0, 0, 1);
let loopback = IpAddr2::V6(String::from("::1"));


fn main() {
    let some_number: Option<i32> = Some(5);
    let some_char: Option<char> = Some('e');

    let absent_number: Option<i32> = None;
    let x: i8 = 5;
    let y: Option<i8> = Some(5);
    // error: expected type `i8`, found `Option<i8>`
    // let sum = x + y;
}
