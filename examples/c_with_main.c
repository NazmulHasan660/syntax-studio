#include <stdio.h>

int main(int argc, char** argv) {
    int x = 10;
    int y = 20;
    int sum = x + y;

    if (sum > 20) {
        printf(sum);
    } else {
        printf(x);
    }

    return 0;
}
