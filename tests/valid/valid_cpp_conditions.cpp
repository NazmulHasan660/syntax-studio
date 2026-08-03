#include <iostream>
using namespace std;

int x = 10;
int y = 3;
int sum = x + y;
bool ready = sum > 10;

if (ready) {
    cout << sum;
} else {
    cout << y;
}

return 0;