#include <iostream>
using namespace std;

int i = 0;

while (i < 2) {
    cout << i;
    i++;
}

for (int j = 0; j < 2; j++) {
    cout << j;
}

int k = 0;

do {
    cout << k;
    k++;
} while (k < 2);

return 0;