# Steering-control-with-simple-Lane Detetion
Creating lane detection based on linear equations.
Calculate the steering control angle based on trigonometric equations.
The steering angle control data is sent to the Arduino module via the serial port (USB).
The Arduino module drives the servo motor according to the received control angle.

**The steering control system configuration.**

<img src="https://github.com/masiwan2000/Steering-control-with-simple-LD/blob/22052480638b6679915739e50e68a0802f758d44/system%20design.jpg" alt="Alt Text" width="300" height="200">


**To introduce the Lane Detection Program, try running the following code:**

*LD_KST.py with Field_Dataset/KST_Area.*

<img src="https://github.com/masiwan2000/Steering-control-with-simple-LD/blob/86854119f82be19bd96055acfe35fc931a9cc2ed/output-LD_KST.jpg" alt="Alt Text" width="300" height="200">

*Try changing the ROI and filter threshold (white and yellow) to use with Field_Dataset/Highway.*

<img src="https://github.com/masiwan2000/Steering-control-with-simple-LD/blob/d8996af87d6adaa707e9d20204c543742a36c6dd/final%20result%20LD.jpg" alt="Alt Text" width="300" height="200">

*Run LD-Steering1.py with Indoor_Dataset.*

<img src="https://github.com/masiwan2000/Steering-control-with-simple-LD/blob/5f5fd4c658694c82595d449e82e5d3d1b39d93c8/Output%20Final.png" alt="Alt Text" width="300" height="200">

*This is a simulation video of the result of the project.*

<img src="https://github.com/masiwan2000/Steering-control-with-simple-LD/blob/8b0c21494eadd41c3cc1fc86afbce660a560241e/Fig_run_simulation.jpg" alt="Alt Text" width="300" height="200">

[Click Here](https://drive.google.com/file/d/15p_wf_BUDU-3fGUtM39hI2DAot_YjYVa/view?usp=sharing)
