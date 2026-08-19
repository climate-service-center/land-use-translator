# cspell:ignore dotdict, mcgrath, pfts

import os
import time

import yaml
from config.validation import (
    validate_config,
    validate_main_files,
    validate_mcgrath_prepared_files,
    validate_pfts_file,
    validate_prepared_files,
)
from lut import LUT
from utils import dotdict, print_section_heading


def load_configuration(data: str) -> dotdict | None:
    """load configuration from yaml file"""
    config_path = os.path.join(
        os.path.expandvars("${REPOS_DIR}"), f"land-use-translator/land_use_and_land_cover_change/config/{data}"
    )
    with open(config_path) as stream:
        try:
            config: dict = yaml.safe_load(stream)
            # Expand environment variables in all path attributes
            for key, value in config.items():
                if isinstance(value, str) and (
                    ("dir" in key.lower()) or ("path" in key.lower()) or ("file" in key.lower())
                ):
                    config[key] = os.path.expandvars(value)

            return dotdict(config)
        except yaml.YAMLError as exc:
            print(exc)


def main():
    """
    Main function to run the LUT
    """

    print("Starting LUCAS LUT calculation...\n")
    print("LUCAS LUT version:", "v2.0.7")
    print("Start time:", time.strftime("%Y-%m-%d %H:%M:%S"))
    t_start = time.time()

    # Load configuration from /config/
    print("Loading configuration...")
    config: Any = load_configuration("main.yaml")
    # config: Any = load_configuration("LANDMATE_testdata-backward.yaml")
    # config: Any = load_configuration("LANDMATE_testdata-forward-rcp70.yaml")

    # LANDMATE, global, 10km, historical and future scenarios CMIP6: AIM-ssp370, IMAGE-ssp126, MAGPIE-ssp585, MESSAGE-ssp245.
    # config: Any = load_configuration("LANDMATE_PFT_v1.2_global_0.1deg_2015-hist.yaml")  # historical
    # config: Any = load_configuration("LANDMATE_PFT_v1.2_global_0.1deg_2015-rcp70.yaml")  # AIM-ssp370
    # config: Any = load_configuration("LANDMATE_PFT_v1.2_global_0.1deg_2015-rcp26.yaml")  # IMAGE-ssp126
    # config: Any = load_configuration("LANDMATE_PFT_v1.2_global_0.1deg_2015-rcp85.yaml")  # MAGPIE-ssp585
    # config: Any = load_configuration("LANDMATE_PFT_v1.2_global_0.1deg_2015-rcp45.yaml") # MESSAGE-ssp245

    # LANDMATE, Europe, 2km, historical and future scenarios CMIP6: AIM-ssp370, IMAGE-ssp126, MAGPIE-ssp585, MESSAGE-ssp245.
    # config: Any = load_configuration("LANDMATE_PFT_v1.1_Europe_0.018deg_2015.yaml") # historical
    # config: Any = load_configuration("LANDMATE_PFT_v1.1_Europe_0.018deg_2015-rcp70.yaml") # AIM-ssp370
    # config: Any = load_configuration("LANDMATE_PFT_v1.1_Europe_0.018deg_2015-rcp26.yaml") # IMAGE-ssp126
    # config: Any = load_configuration("LANDMATE_PFT_v1.1_Europe_0.018deg_2015-rcp85.yaml") # MAGPIE-ssp585
    # config: Any = load_configuration("LANDMATE_PFT_v1.1_Europe_0.018deg_2015-rcp45.yaml") # MESSAGE-ssp245
    print("Configuration loaded.\n")

    # Validate configuration
    print("Validating configuration...")
    validate_config(config)
    print("Configuration successfully validated.\n")

    # Initialize LUT class
    print("Initializing LUT...")
    lut = LUT(config)

    # Generate namelist
    namelist = lut.generate_namelist()

    # Validate main files
    validate_main_files(namelist, config)

    # Preparing the data for the lut calculation
    print_section_heading("Preparing PFTS data")
    lut.func_prepare_pfts_tmp_file()
    validate_pfts_file(namelist, config)
    lut.func_prepare_pfts_file()
    if config.backgrd:
        print_section_heading("Preparing BACKGRD data")
        _t0 = time.time()
        lut.func_prepare_backgr_files()
        print(f"Preparing BACKGRD data - execution time: {time.time() - _t0:.2f}s")
    if config.prepare_mcgrath and not config.forward:
        print_section_heading("Preparing MCGRATH data")
        _t0 = time.time()
        lut.func_prepare_mcgrath()
        print(f"Preparing MCGRATH data - execution time: {time.time() - _t0:.2f}s")
    if config.mcgrath:
        validate_mcgrath_prepared_files(namelist, config)
    if config.prepare_luh2_data:
        print_section_heading("Preparing LUH2 data")
        _t0 = time.time()
        lut.func_prepare_luh2_data()
        print(f"Preparing LUH2 data - execution time: {time.time() - _t0:.2f}s")

    # validating the prepared files
    validate_prepared_files(namelist, config)

    # Running the LUT calculation
    print_section_heading("Calculating land use changes")
    if config.forward:
        print("FORWARD IN TIME")
        _t0 = time.time()
        lut.lucas_lut_forward()
        print(f"Applying LUT forward in time - execution time: {time.time() - _t0:.2f}s")
    else:
        print("BACKWARD IN TIME")
        _t0 = time.time()
        lut.lucas_lut_backward()
        print(f"Applying LUT backward in time - execution time: {time.time() - _t0:.2f}s")

    # Writing out the data
    print_section_heading("Writing out data")
    _t0 = time.time()
    lut.lucas_lut_output()
    print(f"Writing out data - execution time: {time.time() - _t0:.2f}s")
    print("LUCAS LUT SUCCESSFULLY FINISHED")
    print("End time:", time.strftime("%Y-%m-%d %H:%M:%S"))
    print(f"Total LUT execution time: {time.time() - t_start:.2f}s")


if __name__ == "__main__":
    main()
