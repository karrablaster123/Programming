enum Coin {
    Penny,
    Nickel,
    Dime,
    Quarter,
}

fn value_in_cents(coin: Coin) -> u8 {
    match coin {
        Coin::Penny => {
            println!("Lucky penny!");
            1
        },
        Coin::Nickel => 5,
        Coin::Dime => 10,
        Coin::Quarter => 25,
    }
}

fn plus_one(x: Option<i32>) -> Option<i32> {
    match x {
        None => None,
        Some(i) => Some(i + 1),
    }
}

fn main() {
    let coin = Coin::Penny;
    value_in_cents(coin);

    let coin = Coin::Quarter;
    println!("{}", value_in_cents(coin));

    let coin = Coin::Nickel;
    println!("{}", value_in_cents(coin));

    let coin = Coin::Dime;
    println!("{}", value_in_cents(coin));
    println!("Hello, world!");
    let five = Some(5);
    let six = plus_one(five);
    let none = plus_one(None);
    println!("{:?}", six);
    println!("{:?}", none);
}

fn dice_roll() {
    let dice_roll = 9;
    match dice_roll {
        3 => add_fancy_hat(),
        7 => remove_fancy_hat(),
        _ => move_player(dice_roll), // Generic catch-all
    }

    fn add_fancy_hat() {}

    fn remove_fancy_hat() {}

    fn move_player(num_spaces: u8) {}
}

fn config_max() {
    let config_max = Some(3u8);

    // Single pattern cases
    if let Some(max) = config_max {
        println!("The maximum is configured to be {}", max)
    }
}