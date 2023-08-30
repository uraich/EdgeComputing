# Changes I made to be able to compile the newest version.
### Generalities:
I use esp-idf-v5.1, which seems to be the latest stable version.
I also use the Mauro's latest micropython-camera-driver where I had to remove the MODULE_CAMERA_ENABLED parameter in the last
line of src/modcamera.c
### microlite
In the microlite module I had to modify micropython.cmake:
in target_compile_options I added  -Wno-error=stringop-overflow to avoid a warning being seen as error and stopping compilation
and I removed -fno-rtti, which produced plenty of warnings that this flag is only valid for the C++ but not for the C compiler.

### tflm_esp_kernels
Modifications to components/tflite-lib/tensorflow/lite/micro/kernels/esp_nn/conv.cc and depthwise_conv.cc to avoid compilation errors.
### boards folder
I also uploaded ESP32_CAM_S3, the boards files I used to build the system.
I first just compiled micropython, then added u-lab, then the camera driver and finally microlite
I hope I did not forget anything