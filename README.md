# Computer Tomography Simulation 
[Computer tomography](https://en.wikipedia.org/wiki/CT_scan) simulation using [radon transform](https://en.wikipedia.org/wiki/Radon_transform).

## How to run
1. Download needed packages:
 - Numpy   (pip install numpy)
 - PySide2 (pip install PySide2)
 - pydicom (pip install pydicom)
 - skimage (pip install scikit-image)
 
2. Run via python3 interpreter.

## GUI Interface
![1](https://user-images.githubusercontent.com/32361814/77952539-1f2a9280-72cc-11ea-8c82-b90463022f11.png)

## Issues
Non-fast mode preprocess images iteration frames from greyscale through rgb to the PySide2 QPixmap. It impacts on CT process and extends time for ending.
