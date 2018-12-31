#include <stdlib.h>
#include <unistd.h>
#include <stdio.h>

int convert(int n, char c){
    if(c == 'h')
        n *= 3600;
    else if(c == 'm')
        n *= 60;
    return n;
}

int main(int argc, char **argv){
    int num1 = convert(atoi(argv[1]), *argv[2]);
    int num2;
    if(argc > 3){
        num2 = convert(atoi(argv[3]), *argv[4]);
        sleep(num1 + num2);
        system("mpg123 /home/pi/Anton/Responses/TimerFinish.mp3");
    }
    else{
        sleep(num1);
        system("mpg123 /home/pi/Anton/Responses/TimerFinish.mp3");
    }
}
