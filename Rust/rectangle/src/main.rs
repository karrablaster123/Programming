#[derive(Debug)] // Implements Debug trait for this struct
struct Rectangle {
    width: u32,
    height: u32,
}

// Implementing a method on a struct
impl Rectangle {
    fn area(&self) -> u32 {
        self.width * self.height
    }

    fn can_hold(&self, other: &Rectangle) -> bool {
        self.width > other.width && self.height > other.height
    }
}
// Multiple impl blocks are allowed
impl Rectangle {
    // Constructor type associated function
    fn square(size: u32) -> Rectangle {
        Rectangle {
            width: size,
            height: size,
        }
    }
}

fn main() {
    let rect1 = Rectangle {
        width: 30,
        height: 50,
    };
    // Rectangle doesn't implement std::fmt::Display
    // println!("rect1 is {}", rect1);

    // Rectangle uses Debug trait (Only if )
    println!("rect1 is {:#?}", rect1);

    let scale = 2;
    // Using the dbg! macro
    let rect2 = Rectangle {
        width: dbg!(30 * scale),
        height: 50,
    };
    dbg!(&rect2);   // dbg! is a macro that prints the value of the expression,
                    // the line of code where it was called,
                    // and returns the result. You need to provide it a reference
                    // or else it will take ownership of the result. 
    // dbg! prints to stderr not to stdout.
    dbg!(area(&rect2));
    dbg!(rect2.area());

    let rect3 = Rectangle {
        width: 10,
        height: 40,
    };
    let rect4 = Rectangle {
        width: 60,
        height: 45,
    };

    println!("Can rect1 hold rect2? {}", rect1.can_hold(&rect2));
    println!("Can rect1 hold rect3? {}", rect1.can_hold(&rect3));
    println!("Can rect1 hold rect4? {}", rect1.can_hold(&rect4));
    
    let sq = Rectangle::square(3);
    dbg!(&sq);
    dbg!(rect1.can_hold(&sq));
}

fn area(rectangle: &Rectangle) -> u32 {
    rectangle.width * rectangle.height
}

