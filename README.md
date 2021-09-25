DHLLDV
======

Python implementation of the DHLLDV slurry transport framework

Note that the equations are from the 3<sup>rd</sup> edition of the book '[Slurry Transport Fundamentals, A Historical Overview &  The Delft Head Loss &  Limit Deposit Velocity Framework](https://www.researchgate.net/publication/330753872_The_Delft_Head_Loss_Limit_Deposit_Velocity_Framework_2nd_Edition)', By Sape A. Miedema, Edited by Robert Ramsdell

Each model has a test suite, based on 'hand' calculations contained in the included excel spreadsheet [tests/tests.xls](https://github.com/rcriii42/DHLLDV/blob/master/tests/tests.xls)

In addition, [DHLLDV Framework.xlsm](https://github.com/rcriii42/DHLLDV/blob/master/DHLLDV%20Framework.xlsm), a spreadsheet developed by Sape Miedema, implements the framework, a simple pump and slurry system model, historical models and more.

## Licensing
Unless noted in a particular sub-directory, this project is licenced under the [GNU Public License (GPL) 3.0](https://github.com/rcriii42/DHLLDV/blob/master/LICENSE). The current exceptions are as follows:

* The file [DHLLDV Framework.xlsm](https://github.com/rcriii42/DHLLDV/blob/master/DHLLDV%20Framework.xlsm) is copyright Prof. Dr. ir. Sape A. Miedema. To my knowledge Professor Miedema makes the spreadsheet available free of charge with no restrictions.
* The files in the [Scripts](https://github.com/rcriii42/DHLLDV/tree/master/Scripts) directory are licensed under the [MIT license](https://github.com/rcriii42/DHLLDV/blob/master/Scripts/LICENSE). This allows the creation of proprietary modifications and extensions to the viewer code. If you distribute derivative works, you must preserve the copyright notice and provide access to the source code of the underlying DHLLDV library (a link to this repository is sufficient).

## Usage
Once you have the code, navigate to the code directory and create a virtual environment (optional but recommended), install the requirements:

`(env) $ pip install -r requirements.tx`

Run the tests:

```
(env) PS C:\Users\you\PycharmProjects\DHLLDV> pytest
================================================= test session starts =================================================
platform win32 -- Python 3.8.5, pytest-6.2.2, py-1.10.0, pluggy-0.13.1
rootdir: C:\Users\rcrii\PycharmProjects\DHLLDV
plugins: cov-2.11.1
collected 66 items

tests\test_DHLLDV_framework.py .....                                                                             [  7%]
tests\test_DHLLDV_framework_graded.py ............                                                               [ 25%]
tests\test_Framework_LDV.py .......                                                                              [ 36%]
tests\test_Wilson_V50.py .....                                                                                   [ 43%]
tests\test_Wilson_stratified.py ...s..                                                                           [ 53%]
tests\test_heterogeneous.py .....                                                                                [ 60%]
tests\test_homogeneous.py .............                                                                          [ 80%]
tests\test_stratified.py ........                                                                                [ 92%]
tests\test_utils.py .....                                                                                        [100%]

============================================ 65 passed, 1 skipped in 0.49s ============================================
```

## Interactive Viewer
There is an interactive viewer that runs in a bokeh server, the following command will open a tab in your browser:

`(env) PS C:\Users\you\PycharmProjects\DHLLDV> bokeh serve --show .\Scripts\bokeh_viewer.py`

![image](https://user-images.githubusercontent.com/9353408/131259001-3ce1bc1b-8a22-4ac8-9351-26d4481c97d8.png)

The viewer allows you to adjust certain properties of the system:

* **Pipe**: Allows input of pipe diameter in mm. The up and down arrows adjust the pipe diameter by 25mm each way
* **Fluid**: Allows selection of fresh or salt water at 20&deg;C (68&deg;F)
* **Grain Size Distribution** (GSD): Allows adjusting the grain size distribution by adjusting the D85, D50, D15 and fines fraction (defined as passing the #200 sieve, 0.075mm). The up and down arrows vary the D50 by 0.1mm each way, adjusting D85, and D15 proportionally, but not adjusting the fines fraction. The resulting GSD curve is shown with an added point representing the particle diameter that forms part of the carrier liquid.
* **Concentrations**: Allows adjusting the concentration of the slurry by adjusting either the Cv or the rhom. The up and down arrows adjust the Cv by 0.005 each way.
* **Stop**: The Stop button stops the server. The browser tab will still stay open, but the widgets to adjust the slurry no longer will work.


