#include <iostream>
#include <iomanip>
#include <string>
int main() {
    std::string msg = "Hello, world!";
    std::cout << std::setw(20) << std::left << msg << std::endl;
    return 0;
}