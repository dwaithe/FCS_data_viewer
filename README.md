# FoCuS-point

<H4>Python TCSPC (Time Correlated Single Photon Counting) FCS (Fluorescence Correlation Spectroscopy)  data visualiser. </H4>

<p>This is source code repository for FoCuS-point software. For full details please refer to the project website: <a href="http://dwaithe.github.io/FCS_point_correlator/">FoCuS-point project page.</a><p>

<p> The latest and historical releases of the software and manual for Windows, Linux and OSX are available through the following link and allows immediate access to FoCuS-point technique: <a href ="https://github.com/dwaithe/FCS_point_correlator/releases/">Click for Releases</a></p>
<p> Futhermore, the software can be directly installed using pip.

## Installation
### Windows/ Ubuntu 20.04/ MacOS
To match modern python standard, we recommend the use of [miniforge](https://github.com/conda-forge/miniforge?tab=readme-ov-file#miniforge3) over Anaconda with better environment control efficiency.
1. Install Anaconda/miniforage with proper bash initialization.
2. Create virtual environment
    ```bash
    mamba create -n focus python=3.10 -y
    ```
3. Activate the virtual environment
    ```bash
    mamba activate focus
    pip install numpy
    ```
4. Install the package from Github directly
    ```bash
    pip install git+https://github.com/jackyko1991/FCS_point_correlator/ --upgrade
    ```
### Local Installation (For Development Only)
1. Install Anaconda/miniforage with proper bash initialization.
2. Create virtual environment
    ```bash
    mamba create -n focus python=3.10 -y
    ```
3. Activate the virtual environment
    ```bash
    mamba activate focus
    pip install numpy
    ```
4. Clone the repository to local
    ```bash
    git clone git@github.com:jackyko1991/FCS_point_correlator.git
    cd FCS_point_correlator
    ```
4. Install the package from Github directly
    ```bash
    pip install -e .
    ```

### Ubuntu 14.04 (Deprecated)
```bash
sudo apt-get install python-setuptools python-dev build-essential git-all (to install pip, might not need).
sudo easy_install pip (to install pip, might not need).
sudo pip install —upgrade virtualenv numpy
sudo apt-get install libpng-dev libfreetype6-dev (Matplotlib dependencies)
sudo -H pip install git+https://github.com/dwaithe/FCS_point_correlator/ -upgrade (should work for all OS as long as the dependencies are met).
```

### Verify Installation
```bash
python -m focuspoint.FCS_point_correlator
```

## FAQ
1. What datafiles does FoCuS-point support? 
    
    Presently FoCuS-point supports `.pt3` and `.ptu` uncorrelated files and under the fitting tab the FoCuS-point software supports `.SIN` and `.fcs` correlated files and `.csv` files correlated in FoCuS-point's own format.
2. I have data files which are not `.pt3` or any of the current formats, what can I do?  
    You can create an issue using github and I will make the software support your file format if possible. [Issues](https://github.com/dwaithe/FCS_point_correlator/issues)