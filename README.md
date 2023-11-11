# Assistive_Tremor_Algorithms
This project is the result of my final undergraduate semester. It experiments with multiple algorithms for smoothing the mouse movements of people with essential tremor.

Here is a trailer to the final video presentation for this project:
https://youtu.be/gO67bq34zDg


Real-World Mouse Movement Dataset used: https://github.com/leahkf/mouseandtouchinput

The first algorithm (B-Spline plus Breakpoints) is based on the following papers:

BANIHASHEM S. Y., ZIN N. A. M., YATIM N. F. M., IBRAHIM N. M.: Real Time Break Point Detection Technique (RBPD) in Computer Mouse Trajectory. Telkomnika: Indonesian Journal of Electrical Engineering (4 2013). doi:10.11591/telkomnika. v11i5.2507.

BANIHASHEM S. Y., ZIN N. A. M., YATIM N. F. M., IBRAHIM N. M.: Improving Mouse Controlling and Movement for People with Parkinson’s Disease and Involuntary Tremor Using Adaptive Path Smoothing Technique via B-Spline. Assistive Technology 26, 2 (5 2014), 96–104. doi:10.1080/10400435.2013.845271.

The third algorithm (Double-Exponential Smoothing) was inspired by the following paper:

CHUNG M. Y., KIM S.-K.: Efficient jitter compensation using double exponential smoothing. Information Sciences 227 (3 2013), 83– 89. doi:10.1016/j.ins.2012.12.008.


