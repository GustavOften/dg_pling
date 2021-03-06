#include "mbed.h"
 
Serial pc(USBTX, USBRX); 
InterruptIn button(p21);
DigitalOut led(LED1);

void pling(){
  bool plingEvent = true;
  wait(0.01);
  for(int i=0; i<10; i++){
    if(button.read() == 0){
      wait(0.001);
    }
    else{      
      plingEvent = false;
      break;
    }// if
  }// for loop  
  if(plingEvent){
    led = 1;
    pc.printf("PLING\n");
    wait(5);
    led = 0;
  }// if   
}// pling()

int main() {
    button.mode(PullUp);
    button.fall(&pling);
    while(1) { 
        sleep();
    }
}