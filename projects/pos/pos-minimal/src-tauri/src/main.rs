// @tested pos-solo pos-full pos-minimal - pos_ko_lib::run → pos_lib::run, compiles OK
// Prevents additional console window on Windows in release, DO NOT REMOVE!!
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

fn main() {
    pos_lib::run()
}
