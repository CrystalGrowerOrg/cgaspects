# CrystalAspects

CrystalAspects is a CrystalGrower data analysis tool equipped with a PySide6 GUI. 

## Features

- **Data Analysis and Visualization**: It is designed for the analysis and visualization of crystal growth data, including aspect ratios, surface area to volume ratios, growth rates and more.
- **PySide6 GUI**: A user-friendly graphical user interface for interaction with the application.

## Installation

Ensure you have Python >=3.10 installed on your system. 
You can install CrystalAspects via pip:

```
pip install crystalaspects
```

## Usage

After installation, you can run CrystalAspects using the command:

```
crystalaspects
```

## Building and Packaging for macOS

CrystalAspects can be packaged as a standalone application for macOS using PyInstaller. Follow these steps to build and package the application:

1. Install pyinstaller if not already present in your python environment:
    ```
    pip install pyinstaller
    ```
2. Navigate to your project directory and run the PyInstaller command:

    ```
    ./scripts/mac_os_bundle.sh
    ```

3. After the build completes, the script will run an ad hoc code signing to sign the application. This will create a `.app` package in the `dist` directory, which can be distributed and run on macOS systems.

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

CrystalAspects is currently in Alpha stage. It is intended for science and research use, particularly in the field of computational chemistry.

## Authors

    Alvin Jenner Walisinghe - jennerwalisinghe@gmail.com
    Nathan de Bruyn - jennerwalisinghe@gmail.com
    Peter R. Spackman - peterspackman@fastmail.com

## License

CrystalAspects is distributed under the MIT License. 
See the accompanying LICENSE.txt file for more details.

## Contributions

Contributions are welcome! Please read the contribution guidelines before submitting a pull request.
Links

    Homepage
    Repository

Contact

For support or inquiries, please email the authors or create an issue in the project's issue tracker.
