from cerberus import Validator, errors
import yaml
import os
import xarray as xr
from src.config import datadir, scenario_dict, mcg

schema = {
    "region": {"type": "string", "allowed": ["Germany", "Europe", "WestAfrica", "NorthAmerica", "Australasia"]},
    "forward" : {"type": "boolean"},
    "addtree": {"type": "boolean"},
    "backgrd" : {"type": "boolean"},
    "mcgrath" : {"type": "boolean"},
    "irri" : {"type": "boolean"},
    "prepare_luh2_data": {"type": "boolean"},
    "prepare_mcgrath": {"type": "boolean"},
    "syear" : {"type": "integer"},
    "eyear" : {"type": "integer"},
    "npfts" : {"type": "integer"},
    "mcgrath_eyear" : {"type": "integer", "nullable": True},
    "xsize" : {"type": "integer"},
    "ysize" : {"type": "integer"},
    "gradef" : {"type": "integer"},
    "crodef" : {"type": "integer"},
    "shrdef" : {"type": "integer"},
    "remap" : {"type": "string", "allowed": ["bilinear", "con2"]},
    "scenario" : {"type": "string", "allowed": ["historical", "historical_high", "historical_low", "rcp19", "rcp26", "rcp34", "rcp45", "rcp60", "rcp70", "rcp85"]},
    "grid": {"type": "float"},
    "rcm_lsm_var": {"type": "string"},
    "path_file_states" : {"type": "string", "nullable": True},
    "path_file_trans" : {"type": "string", "nullable": True},
    "path_file_manag" : {"type": "string", "nullable": True},
    "path_file_addtree" : {"type": "string", "nullable": True},
    "path_file_rcm_lsm_in" : {"type": "string", "nullable": True},
    "path_file_lc_in" : {"type": "string", "nullable": True},
    "path_file_backgra_global" : {"type": "string", "nullable": True},
    "path_file_backshr_global" : {"type": "string", "nullable": True},
    "path_file_backfor_global" : {"type": "string", "nullable": True},
    "path_file_backurb_global" : {"type": "string", "nullable": True},
    "path_file_backcro_global" : {"type": "string", "nullable": True},
    "path_file_backgra" : {"type": "string", "nullable": True},
    "path_file_backshr" : {"type": "string", "nullable": True},
    "path_file_backfor" : {"type": "string", "nullable": True},
    "path_file_backurb" : {"type": "string", "nullable": True},
    "path_file_backcro" : {"type": "string", "nullable": True},
    "path_file_lsm" : {"type": "string", "nullable": True},
    "vers": {"type": "integer"},
    "coords": {"type": "string", "nullable": True},
}


class CustomValidator(Validator):
    def _validate_allowed(self, allowed, field, value):
        """{'type': 'list'}"""
        if value not in allowed:
            self._error(field, f"unallowed value {value} --> Select one of the following values: {allowed}")

def validate_config(config):
    v = CustomValidator(schema)
    v.validate(config)
    if v.errors:
        raise ValueError(v.errors)
    if config.syear >= config.eyear:
        raise ValueError("Starting year (syear) must be smaller than ending year (eyear)")
    if config.mcgrath_eyear and config.mcgrath:
        if config.mcgrath_eyear > config.eyear:
            raise ValueError("Mcgrath year (mcgrath_eyear) must be equal or smaller than ending year (eyear)")
        if config.mcgrath_eyear < config.syear:
            raise ValueError("Mcgrath year (mcgrath_eyear) must be equal or bigger than starting year (syear)")
    if config.coords:
        if len(config.coords.split(",")) != 4:
            raise ValueError("Coordinates must given as 4 values (lonmin,lonmax,latmin,latmax) separated by commas")
        try:
            [float(config.coords.split(",")[i]) for i in range(4)]
        except ValueError:
            raise ValueError("Coordinates must be given as float values")

def validate_path(file, datadir=None, add_message=""):
    if datadir:
        if not os.path.isfile(os.path.join(datadir, file)):
            path = os.path.join(datadir, file)
            raise ValueError(f"File {path} does not exist. "+add_message)
    else:
        if not os.path.isfile(file):
            raise ValueError(f"File {file} does not exist. "+add_message)

def validate_main_files(namelist, config):
    # IT MIGHT BE SIMPLIFIED AND INCLUDED JUST IN THE INIT FUNCTION OF LUT
    for key, value in namelist.items():
        # checking if files exist
        if key == "F_GRID":
            validate_path(value)
        if key in ("F_LC_IN"):
            validate_path(value)
            validate_dimensions(value, config)
        if key.startswith("F_GLOBAL_BACK") and config.backgrd:
            validate_path(value)
            validate_dimensions(value, config, type=2)
        if config.path_file_lsm:
            validate_path(config.path_file_lsm)
            validate_dimensions(config.path_file_lsm, config)
            ds = xr.open_dataset(config.path_file_lsm, decode_times=False)
            try:
                ds[config.rcm_lsm_var]
            except KeyError:
                raise ValueError(f"Variable {config.rcm_lsm_var} not found in file {config.path_file_lsm}")
    if config.scenario in ["historical", "historical_high", "historical_low"]:
        sfile="states.nc" if not config.path_file_states else config.path_file_states
        tfile="transitions.nc" if not config.path_file_trans else config.path_file_trans
        mfile="management.nc" if not config.path_file_manag else config.path_file_manag
    elif config.scenario in scenario_dict.keys():
        afile=f"added_tree_cover_input4MIPs_landState_ScenarioMIP_UofMD-{scenario_dict[config.scenario]}-2-1-f_gn_2015-2100.nc" if not config.path_file_addtree else config.path_file_addtree
        sfile=f"multiple-states_input4MIPs_landState_ScenarioMIP_UofMD-{scenario_dict[config.scenario]}-2-1-f_gn_2015-2100.nc" if not config.path_file_states else config.path_file_states
        tfile=f"multiple-transitions_input4MIPs_landState_ScenarioMIP_UofMD-{scenario_dict[config.scenario]}-2-1-f_gn_2015-2100.nc" if not config.path_file_trans else config.path_file_trans
        mfile=f"multiple-management_input4MIPs_landState_ScenarioMIP_UofMD-{scenario_dict[config.scenario]}-2-1-f_gn_2015-2100.nc" if not config.path_file_manag else config.path_file_manag
    if (config.prepare_mcgrath):
        ifile=f"{mcg}_{config.syear}_{config.mcgrath_eyear}.nc"
        validate_path(ifile, datadir, add_message="Consider adding the missing file or unable option 'prepare_mcgrath'.")
    if config.prepare_luh2_data:
        validate_path(tfile, datadir)
        validate_path(sfile, datadir)
    if config.irri:
        if config.scenario not in ["historical", "historical_low", "historical_high"]:
            validate_path(sfile, datadir)
        validate_path(mfile, datadir)
    if config.addtree:
        validate_path(afile, datadir)

def validate_mcgrath_prepared_files(namelist, config):
    for key, value in namelist.items():
        if (key=="F_MCGRATH"):
            validate_path(value, add_message="Consider enabling the option 'prepare_mcgrath' to prepare the missing file or unable 'mcgrath'.")
            validate_dimensions(value, config)

def validate_prepared_files(namelist, config):
    for key, value in namelist.items():
        # checking if files exist
        if key == "F_GRID":
            validate_path(value)
        elif key not in ["F_IRRI_IN", "F_ADDTREE", "F_MCGRATH", "F_LC_OUT"] and not key.startswith("F_BACK") and not key.startswith("F_GLOBAL"):
            validate_path(value, add_message="Consider enabling the option 'prepare_luh2_data' to prepare the missing file.")
        # checking file sizes
        
        if key not in ["F_IRRI_IN", "F_ADDTREE", "F_MCGRATH", "F_GRID", "F_LC_OUT"] and not key.startswith("F_BACK") and not key.startswith("F_GLOBAL"):
            validate_dimensions(value, config)

        if config.backgrd and key.startswith("F_BACK"):
            validate_dimensions(value, config)

        if (config.addtree and key=="F_ADDTREE"):
            validate_path(value)
            validate_dimensions(value, config)

        if (config.irri and key=="F_IRRI_IN"):
            validate_path(value, add_message="Consider enabling the option 'prepare_luh2_data' to prepare the missing file.")
            validate_dimensions(value, config)

def validate_dimensions(value, config, type=1):
    ds = xr.open_dataset(value, decode_times=False)
    if not (ds.dims.get("x") or ds.dims.get("lon") or ds.dims.get("rlon")) and not (ds.dims.get("y") or ds.dims.get("lat") or ds.dims.get("rlat")):
        raise ValueError(f"File {value} has wrong dimensions. Expected 2D but got {ds.dims}")
    else:
        x_dim = "x" if ds.dims.get("x") else "lon" if ds.dims.get("lon") else "rlon"
        y_dim = "y" if ds.dims.get("y") else "lat" if ds.dims.get("lat") else "rlat"
    if type == 2:
        if ds.dims.get(x_dim) < config.xsize or ds.dims.get(y_dim) < config.ysize:
            raise ValueError(f"File {value} has wrong dimensions. Expected {config.xsize}x{config.ysize} but got {ds.dims.get(x_dim)}x{ds.dims.get(y_dim)}")
    else:
        if ds.dims.get(x_dim) != config.xsize or ds.dims.get(y_dim) != config.ysize:
            raise ValueError(f"File {value} has wrong dimensions. Expected {config.xsize}x{config.ysize} but got {ds.dims.get(x_dim)}x{ds.dims.get(y_dim)}")
