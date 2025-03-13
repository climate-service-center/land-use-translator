# High-Resolution Land Use and Land Cover (LULC) Dataset Calculator for Regional Climate Modeling

This Python program generates high-resolution land use and land cover (LULC) datasets for regional climate modeling across both historical and future periods. The original project was developed in Fortran by Peter Hoffmann (see: [ESSD, 2023](https://essd.copernicus.org/articles/15/3819/2023/)). By integrating this LULC data, climate models can more accurately simulate the impacts of land use changes on regional climate dynamics.

## Installation Guide

1. **Change to the project directory:**
   
   ```bash
   cd project_name
   ```
   
2. **Install the required libraries:**
   
   ```bash
   conda env create -f environment.yml
   ```

3. **Activate your environment:**
   
   ```bash
   conda activate land_use_translator_env
   ```

## Quick Start (Example: Historical Scenario 1950-2015 for Germany)

1. **Change to the project's data directory:**
   
   ```bash
   cd land_use_and_land_cover_change/data/
   ```
   
2. **Download required data files using `wget`:**
   
   ```bash
   wget --continue --progress=bar --no-check-certificate \
    "https://luh.umd.edu/LUH2/LUH2_v2h/transitions.nc" \
    "https://luh.umd.edu/LUH2/LUH2_v2h/states.nc" \
    "https://luh.umd.edu/LUH2/LUH2_v2h/management.nc" \
    "https://zenodo.org/records/14981619/files/CROB_reg01_Global.nc?download=1" \
    "https://zenodo.org/records/14981619/files/FORB_reg01_Global.nc?download=1" \
    "https://zenodo.org/records/14981619/files/GRAB_reg01_Global.nc?download=1" \
    "https://zenodo.org/records/14981619/files/SHRB_reg01_Global.nc?download=1" \
    "https://zenodo.org/records/14981619/files/URBB_reg01_Global.nc?download=1" \
    "https://zenodo.org/records/14981619/files/PFTS_reg01.nc?download=1"
   ```
   
   These files will be downloaded and saved in the `data` directory.

3. **Run the program from the project directory:**
   
   ```bash
   python3 main.py
   ```
   
4. **Output File:**
   - The generated output file will be located in the `data/LUCAS_LUC/` directory.
   - It contains the Plant Functional Type (PFT) fraction for the 16 NPFTs across the selected region, scenario, and timeline.

## Dataset Requirements

### **Required Datasets:**

- **Land Use (LU) Transitions:**
  - Downloadable from the [LUH Data Portal](https://luh.umd.edu/data.shtml).
  - Files needed:
    - `transitions.nc`: Annual land-use transitions.
    - `states.nc`: Land-use states (fractions of each grid cell).
    - `management.nc`: Irrigation data (only required if `irri = True`).
    - `add_tree_cover.nc`: Tree cover data (only required if `addtree = True`).

- **Landmate PFT Maps:**
  - Provides vegetation characterization with 16 Plant Functional Types (PFTs).
  - Available from [WDC Climate](https://www.wdc-climate.de/ui/entry?acronym=LM_PFT_EUR_v1.1_afts).
  - Rename the downloaded file as `PFTS_reg01.nc` and move it to `land_use_and_land_cover_change/data/`.

### **Optional Datasets:**

- **McGrath Data:**
  - Used for historical forest type distribution.
  - Contact the project maintainers for access.

- **Sea-Land Mask:**
  - Default: Calculated from Landmate PFT maps.
  - Custom masks can be specified using `path_file_lsm` in the configuration file.

- **Background Data:**
  - Used when vegetation types are missing but required by LUH2 rules.
  - Default global dataset provided, but custom datasets can be specified.

## Configuration

The main configuration file is located at `config/main.yaml`. Modify these parameters to customize the program:

### **LUT Configuration**

- `region`: Pre-configured regions: "Germany", "Europe", "WestAfrica", "NorthAmerica", "Australasia". Custom regions can be added.
- `forward`: **True** for future simulation, **False** for historical.
- `backgrd`: **True/False** (Include background data).
- `mcgrath`: **True/False** (Use McGrath data in LUT).
- `addtree`: **True/False** (Include additional tree cover data).
- `irri`: **True/False** (Enable irrigation data if available).
- `syear` / `eyear`: Specify the time range.
- `npfts`: Number of NPFTs in the LUT.
- `xsize` / `ysize`: Define region dimensions.

### **LUH2 Data Preparation**

- `prepare_luh2_data`: **True/False** (Extract required LUH2 data).
- `prepare_mcgrath`: **True/False** (Prepare McGrath data, if available).
- `remap`: Choose remapping method (**bilinear** or **con2**).
- `scenario`: Options: "historical", "historical_high", "historical_low", "rcp19", "rcp26", "rcp34", "rcp45", "rcp60", "rcp70", "rcp85".
- `grid`: Select resolution (degrees).
- `coords`: Custom coordinates (optional).

### **Sea-Land Mask Configuration**

- `path_file_lsm`: Path to a custom sea-land mask file (if applicable).
- `rcm_lsm_var`: Variable name in the RCM LSM file.

### **Background Data Configuration**

- `path_file_back*`: Path to a custom background dataset.

### **Optional File Paths**

- `path_file_*`: Specify custom paths for input files. If not set, default locations will be used.
