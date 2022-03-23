# tflite-esp32-cam
This repository contains some tinyML test programs for the esp32-cam module. We supply micropython firmware which integrates ulab, tflite and the camera driver for the ov2640 camera on board the esp32-cam.
**This is highly experimental and no guaranty is given that any part of it actually works!**
The firmware is based on Michael O'Cleirigh work: [https://github.com/mocleiri/tensorflow-micropython-examples](https://github.com/mocleiri/tensorflow-micropython-examples) with a modifed version of Mauro Riva's [interface to the esp32-camera driver](https://github.com/lemariva/micropython-camera-driver). In addition to the setter functions getter functions are provided. The source could of this driver interface can be found on the repository.
I simple python program to read out a 96x96 gray scalee image from the camera and to save the pixel values onto a file is also provided.
