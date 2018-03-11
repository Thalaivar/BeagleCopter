#include "dobby.h"

int Dobby::pre_flight_checks(){

  // check current state
  if(this->state == READY_TO_FLY){
    cerr << "DOBBY IS READY!";
    return 0;
  }

  // check IMU
  if(!imu.is_initialized){
    cerr << "IMU not initialized!\n";
    return -1;
  }

  // check Receiver
  if(!radio.is_initialized){
    cerr << "Receiver not initialized!\n";
    return -1;
  }

  // check if flight mode is set
  if(mode.current_mode == NOT_SET){
    cerr << "Flight mode not set, cant take off!\n";
    return -1;
  }

  // any checks for controller?

  // check Motors
  if(!motors.is_initialized){
    std::cerr << "Motors are not initialized" << '\n';
    return -1;
  }

  // check if IMU is calibrated
  if(!imu.is_calibrated){
    std::cerr << "IMU not calibrated!" << '\n';
    return -1;
  }

  // check if radio calibrated
  if(!radio.is_calibrated){
    std::cerr << "Receiver not calibrated!" << '\n';
    return -1;
  }

  // if everything checks out, ready to fly!
  cerr << "DOBBY IS READY!";
  this->status = READY_TO_FLY;
  return 0;
}

int Dobby::setup(){

  // initialize the radio
  if(radio.init_radio() < 0){
    std::cerr << "Radio failed to initialize!" << '\n';
    return -1;
  }

  // initialize the Motors
  if(motors.initialize_pru() < 0){
    std::cerr << "Motors failed to initialize!" << '\n';
    return -1;
  }

  //initialize the IMU
  if(imu.init_imu() < 0){
    std::cerr << "IMU failed to initialize" << '\n';
    return -1;
  }

  return 0;
}

void Dobby::control_loop(){

  // get latest radio signals
  radio.update();

  // get latest desired things
  mode.flight_mode_update();

  // run smc controller
  control.run_smc_controller();

  // update motors
  motors.update();
  
}