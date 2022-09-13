DHLLDV
======

Python implementation of the DHLLDV slurry transport framework

Note that the equations are from the 3<sup>rd</sup> edition of the book '[Slurry Transport Fundamentals, A Historical Overview &  The Delft Head Loss &  Limit Deposit Velocity Framework](https://www.researchgate.net/publication/330753872_The_Delft_Head_Loss_Limit_Deposit_Velocity_Framework_2nd_Edition)', By Sape A. Miedema, Edited by Robert Ramsdell

Each model has a test suite, based on 'hand' calculations contained in the included excel spreadsheet [tests/tests.xls](https://github.com/rcriii42/DHLLDV/blob/master/tests/tests.xls)

In addition, [DHLLDV Framework.xlsm](https://github.com/rcriii42/DHLLDV/blob/master/DHLLDV%20Framework.xlsm), a spreadsheet developed by Sape Miedema, implements the framework, a simple pump and slurry system model, historical models and more.

## Licensing
Unless noted in a particular sub-directory, this project is licenced under the [GNU Public License (GPL) 3.0](https://github.com/rcriii42/DHLLDV/blob/master/LICENSE). The current exceptions are as follows:

* The file [DHLLDV Framework.xlsm](https://github.com/rcriii42/DHLLDV/blob/master/DHLLDV%20Framework.xlsm) is copyright Prof. Dr. ir. Sape A. Miedema. Professor Miedema makes the spreadsheet available free of charge with no restrictions, except for the request that you cite it in any publications as "Miedema, S.A., "Slurry Transport: Fundamentals, A Historical Overview & The Delft Head Loss & Limit Deposit Velocity Framework" Supplementary Excel Workbook. Delft University of Technology, Delft, the Netherlands, March 2017."
* The files in the [Scripts](https://github.com/rcriii42/DHLLDV/tree/master/Scripts) directory are licensed under the [MIT license](https://github.com/rcriii42/DHLLDV/blob/master/Scripts/LICENSE). This allows the creation of proprietary modifications and extensions to the viewer code. If you distribute derivative works, you must preserve the copyright notice and provide access to the source code of the underlying DHLLDV library (a link to this repository is sufficient).

## Usage
Download the source code:

`PS C:\Users\you\PycharmProjects\DHLLDV>git clone https://github.com/rcriii42/DHLLDV.git DHLLDV`

Change to the DHLLDV directory and create a virtual environment (not required but recommended):

`PS C:\Users\you\PycharmProjects\DHLLDV>python -m venv .\env`

Activate the virtual environment:

* In Bash (Linux, Unix, etc): `source env/bin/activate`
* In Windows Powershell: `env\scripts\activate.ps1`
* Commands for other command-line environments [here](https://docs.python.org/3/library/venv.html#creating-virtual-environments) (scroll down to the table)

After activating the virtual environment, the command prompt will be preceded by `(env) `.

Install the requirements:
`(env) PS C:\Users\you\PycharmProjects\DHLLDV>pip install -r requirements.txt`

Run the tests:

```
(venv) PS C:\Users\rcrii\PycharmProjects\DHLLDV> pytest --cov-report term-missing --cov=DHLLDV
======================================================= test session starts ========================================================
platform win32 -- Python 3.10.2, pytest-6.2.5, py-1.11.0, pluggy-1.0.0
rootdir: C:\Users\rcrii\PycharmProjects\DHLLDV
plugins: cov-3.0.0
collected 110 items

tests\test_DHLLDV_framework.py ......                                                                                         [  5%]
tests\test_DHLLDV_framework_graded.py ...............                                                                         [ 19%]
tests\test_Framework_LDV.py .......                                                                                           [ 25%]
tests\test_Pipe.py ...............                                                                                            [ 39%]
tests\test_PumpObj.py ........                                                                                                [ 46%]
tests\test_SlurryObj.py ..............                                                                                        [ 59%]
tests\test_Wilson_V50.py .....                                                                                                [ 63%]
tests\test_Wilson_stratified.py ...s..                                                                                        [ 69%]
tests\test_heterogeneous.py .....                                                                                             [ 73%]
tests\test_homogeneous.py ..............                                                                                      [ 86%]
tests\test_stratified.py ........                                                                                             [ 93%]
tests\test_utils.py .......                                                                                                   [100%]

---------- coverage: platform win32, python 3.10.2-final-0 -----------
Name                             Stmts   Miss  Cover   Missing
--------------------------------------------------------------
src\DHLLDV\DHLLDV_Utils.py          37      0   100%
src\DHLLDV\DHLLDV_constants.py      12      0   100%
src\DHLLDV\DHLLDV_framework.py     272     17    94%   138, 199, 233, 286-289, 309-310, 350-358, 470
src\DHLLDV\PipeObj.py              149     23    85%   49, 85, 189-190, 200-201, 209-225
src\DHLLDV\PumpObj.py              140     42    70%   62, 75, 93, 113, 128-164, 192, 202
src\DHLLDV\SlurryObj.py            170      2    99%   161, 278
src\DHLLDV\__init__.py               0      0   100%
src\DHLLDV\heterogeneous.py         55      1    98%   146
src\DHLLDV\homogeneous.py           57      0   100%
src\DHLLDV\stratified.py            80      2    98%   171, 220
--------------------------------------------------------------
TOTAL                              972     87    91%


================================================== 109 passed, 1 skipped in 5.39s =================================================
```

# Interactive Viewer
There is an interactive viewer that runs in a bokeh server, the following command will open a tab in your browser:

`(env) PS C:\Users\you\PycharmProjects\DHLLDV> bokeh serve --show .\Scripts\bokeh_viewer.py`

The viewer has a top bar, and two tabs; a Slurry Tab and Pipeline Tab

## Top Bar

<img alt="DHLLDV Viewer top bar" src="https://user-images.githubusercontent.com/9353408/189939922-cea8b7e3-a691-407a-8de4-3a2245b1ac56.png" width="200%">

* Two tabs, to show info about the **Slurry** or the **Pipeline**
* A **Pipeline Picker** to choose among already-defined pipeline setups
* A **Unit Picker**, that chooses between output in SI (m, m3/sec, kW) or US (Ft, GPM, HP, Psi) units, currently only updates the Pipeline tab
* A **Stop** button that stops the server. The browser tab will still stay open, but the widgets to adjust the slurry no longer will work.

## Slurry Tab

<img src="https://user-images.githubusercontent.com/9353408/184931303-00ec8b59-1909-4a34-a0c1-813dab834d29.png" width="125%" alt="Slurry Tab">

The viewer allows you to adjust certain properties of the system:

* **Pipe**: Allows input of pipe diameter in mm. The up and down arrows adjust the pipe diameter by 25mm each way. The roughness is the absolute roughness of new steel pipe in m (per Cameron Hydraulic Data). This does _not_ update the pipeline, but does change the pipe diameter for the velocity graphs.
* **Fluid**: Allows selection of fresh or salt water at 20&deg;C (68&deg;F). This adjusts the density and viscosity of the carrier fluid.
* **Grain Size Distribution** (GSD): Allows adjusting the grain size distribution by adjusting the D85, D50, D15 and fines fraction (defined as passing the #200 sieve, 0.075mm).
  * The up and down arrows vary the D50 by 0.1mm each way, adjusting D85, and D15 proportionally, but not adjusting the fines fraction.
  * The fines fraction can be set blank, in which case it is ignored when generating the GSD
  * The resulting GSD curve is calculated and shown on the "Grain Size Distribution" graph. The distribution starts at the low end with the 'pseudoliquid diameter', the diameter of particle below which particles are essentially part of the fluid (this is pipe-size, fluid, and particle density dependent). It then calculates the fractions of particles between the given D15, D50, and D85, targeting a 10-point distribution, then adds one above the largest particle diameter.
* **Concentrations**: Allows adjusting the concentration of the slurry by adjusting either the Cv or the rhom. The up and down arrows adjust the Cv by 0.005 each way.


## Pipeline Tab

Shows a particular pipeline, including a CSD dredge with two pumps. 

### Left Panel
* The total length, K, and delta-z for the pipeline
* The dig depth and final discharge elevation
* The number of pumps, maximum total head, maximum available power
* A sequential list of the pipe sections and pumps in the pipeline
  * Pipe sections display the name, diameter, length, K, and elevation change
  * Pumps are two rows. The first gives details about the pump, including the driver (motor or engine) power. The second gives the pump speed and power demand at the operating point.

### Right Panel
* An interactive head-flow-velocity plot of the system (head required) and pump (head available) curves.
* The system minimum friction point - flow, velocity (in the same pipe diamater as in the plot above), and slurry head requirement.
* The **Operating Point**, the right-hand intersection of the system and pump curves for slurry - flow, velocity, head requrement, and delivered production.
* A plot of the pressure gradeline - shows the pressure change and elevations along the pipe

<img src="https://user-images.githubusercontent.com/9353408/189940930-af14bd12-5aaf-4790-8b1b-928a3b239789.png" width="125%" alt="Pipeline Tab">
