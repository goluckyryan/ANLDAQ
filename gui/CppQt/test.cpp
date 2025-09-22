
#include <iostream>
#include <string>
#include <chrono>

#include "class_PV.h"

int main() {

  auto start = std::chrono::high_resolution_clock::now();

  ca_context_create(ca_enable_preemptive_callback);

  PV pvList;

  for( int i=0; i<20; i++ ) {

    int ch = i % 10;

    pvList.setName("VME99:MDIG1:raw_data_length" + std::to_string(ch));

    pvList.put(i);

    std::cout << "PV: " << pvList.getName() << ", Value: " << pvList.getValue() << std::endl;

  }

  auto end = std::chrono::high_resolution_clock::now();
  std::chrono::duration<double> elapsed = end - start;
  std::cout << "Elapsed time: " << elapsed.count() << " seconds" << std::endl;


  return 0;
}