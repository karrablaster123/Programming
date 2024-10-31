use winput::{Vk, Input, Action};


fn main() {
    let inputs = [
        Input::from_vk(Vk::Alt, Action::Press),
        Input::from_vk(Vk::Oem3, Action::Press),
        Input::from_vk(Vk::Alt, Action::Release),
        Input::from_vk(Vk::Oem3, Action::Release),
    ];

    winput::send_inputs(&inputs);
}
