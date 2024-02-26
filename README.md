# CGAspects

CGAspects is a CrystalGrower data analysis tool equipped with a PySide6 GUI. 

## Features

- **Data Analysis and Visualization**: It is designed for the analysis and visualization of crystal growth data, including aspect ratios (Zingg analysis), surface area to volume ratios, growth rates and more.
- **PySide6 GUI**: A user-friendly graphical user interface for interaction with the application.

## Installation

To use CGAspects with python, clone the repository and then install the package. 
Ensure you have Python >=3.10 installed on your system.

1. Clone the CGAspects repository (shallow clone with depth 1):

    ```bash
    git clone --depth=1 https://github.com/CrystalGrowerOrg/cgaspects.git
    cd cgaspects
    ```

2. Install CGAspects via pip:

    ```bash
    pip install .
    ```

## Usage

After installation, you can run CGAspects using the command:

```bash
cgaspects
```

## Building and Packaging for macOS

CGAspects can be packaged as a standalone application for macOS using PyInstaller. 

To build and package the application:

1. Install pyinstaller in your python environment:
   
    ```bash
    pip install pyinstaller
    ```
2. Navigate to the project directory and run the provided script:

    ```bash
    ./scripts/mac_os_bundle.sh
    ```

3. After the build completes, the script will run an ad hoc code signing to sign the application.
   This will create a `.app` package in the `dist` directory, which can be distributed and run on macOS systems.

## Dependencies

    PySide6>=6.6.0
    PyOpenGL
    NumPy>=1.12
    Pandas>=1.4
    SciPy>=1.8.1
    Trimesh>=3.12.9
    Matplotlib>=3.5.2
    Natsort>=8.2

## Development Status

CGAspects is currently in Alpha stage.

## Authors

- **Alvin Jenner Walisinghe** - [jennerwalisinghe@gmail.com](mailto:jennerwalisinghe@gmail.com)
- **Nathan de Bruyn** - [nathan.debruyn@manchester.ac.uk](mailto:nathan.debruyn@manchester.ac.uk)
- **Peter R. Spackman** - [peterspackman@fastmail.com](mailto:peterspackman@fastmail.com)

## Contributions

Contributions are welcome! Please read the [contribution guidelines](https://github.com/CrystalGrowerOrg/cgaspects/blob/main/CONTRIBUTING.md) before submitting a pull request.

## Links

- [Homepage](https://github.com/CrystalGrowerOrg/cgaspects)
- [Repository](https://github.com/CrystalGrowerOrg/cgaspects)
- [Submit Issues](https://github.com/CrystalGrowerOrg/cgaspects/issues)

## Contact

For support or inquiries, please email the authors or create an issue in the project's issue tracker.
