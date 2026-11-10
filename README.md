# Program2
## Introduction 
Here is our submission to the Hardware Synthesis Programming assignment. At the high level, this program takes in a series of equations per line and creates a SSA form of it. From there, it creates a DAG and the user can specify what schedule they would like to implement. The program writes a datapath and control unit verilog file using functional unit blocks for the respective operations. The program then creates a wrapper that instantiates these units. The program then can be written onto an FPGA board which has a clocking feature that allows users to see intermediate calculations. 
## Board Launch
Once programmed, the FPGA board provided in the lab uses the first 8 switches as bits for a specific input. The index of the input is selected with the next seven switches. For example, if B was the second input, flipping switch 8 would index B and then you could select the appropriate value you would like to assign to B. The index of your input is shown with the last two digits of the digital display on the FPGA. The first two would show your input value, in hexidecimal. Once the user is satisfied with the value they would like to assign an input, they can then press the left button on the FPGA board (in the section of buttons that form a cross) to assign that value to hardware. Once all inputs are assigned, the user can step through to the next cycle by clicking the middle button. To view intermediate inputs, the last switch must be flipped and then the index of that variable must be flipped as well. The LEDs on the board represent what cycle the user is on, in binary. As a note, the values are modulo 256, if any variable values do exceed 256 in hexidecimal. 
## Structure
The func.py file has our parsing function, the DAG.py file has our directed acyclic graph class, the dag_view file is for gui visualization of the DAG and schedules, the gui file is our script for the gui, the gen_top and Generator files are for generating the verilog code, and the schedules file is for our scheduling functions. 
## Dependencies
To install all of the necessary dependencies, while also creating an environment to run the code, put this in your terminal 

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Demo 
The first five minutes will be spent explaining our code structure, the next five to ten minutes will be spent going through our examples in the gui, and the last portion will be spent demonstrating the board deployment.

## AI Statement 
Claude was used to assist us in creating the DAG file (creating pseudocode), the constrained schedule functions (again pseudocode), and gave general guidance on creating the Generator file. Claude created the gen_top file as well so the constraint file.  
