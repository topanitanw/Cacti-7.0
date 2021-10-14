import os
import argparse
import git
import logging as log
import sys
import pandas as pd

# def get_proj_root(path):
#     git_repo = git.Repo(path, search_parent_directories=True)
#     git_root = git_repo.git.rev_parse("--show-toplevel")
#     return git_root
#
#
# sys.path.insert(0, get_proj_root("."))

import file_manager as fmg
import cacti_config
import cacti_output
import experiments as rrex

ASSOC = 4
NCORE = 1

headers = (
    "component",
    "level",
    "slice",
    "Tech node (nm)",
    "Capacity (bytes)",
    "Number of banks",
    "Associativity",
    "Output width (bits)",
    "Access time (ns)",
    "Random cycle time (ns)",
    "Dynamic search energy (nJ)",
    "Dynamic read energy (nJ)",
    "Dynamic write energy (nJ)",
    "Standby leakage per bank(mW)",
    "Area (mm2)",
    "Ndwl",
    "Ndbl",
    "Nspd",
    "Ndcm",
    "Ndsam_level_1",
    "Ndsam_level_2",
    "Data arrary area efficiency %",
    "Ntwl",
    "Ntbl",
    "Ntspd",
    "Ntcm",
    "Ntsam_level_1",
    "Ntsam_level_2",
    "Tag arrary area efficiency %",
)


class Component:
    def __init__(self, comp, level, slice_size, size_byte, assoc):
        self.comp = comp
        self.level = level
        self.slice_size = slice_size
        self.size_byte = size_byte
        self.assoc = assoc

    def get_part_header(self):
        return {
            "component": self.comp,
            "level": self.level,
            "slice": self.slice_size
        }


def display_data(power_df):
    print(power_df[[
        "component",
        "level",
        "slice",
        "Capacity (bytes)",
        "Associativity",
        "Output width (bits)",
        "Access time (ns)",
        "Dynamic search energy (nJ)",
        "Dynamic read energy (nJ)",
        "Dynamic write energy (nJ)",
        "Standby leakage per bank(mW)",
        "Area (mm2)",
    ]])


def get_config_filename(comp, level, slicesize):
    return f"{comp}_l{level}_s{slicesize}.cfg"


def create_config_and_run(power_df, comp, core_counts):
    comp_cacti_config = cacti_config.CactiConfig(
        comp.comp,
        comp.level,
        comp.size_byte,
        comp.assoc,
        core_counts,
    )

    comp_config_filename = get_config_filename(comp.comp, comp.level, comp.slice_size)
    comp_config_path = os.path.join("configs", comp_config_filename)
    comp_cacti_config.write_config(comp_config_path)
    comp_cacti_config.run(comp_config)

    comp_cacti_output_filename = comp_config + ".out"
    log.info("reading: %s", comp_cacti_output_filename)
    comp_cacti_output = cacti_output.CactiOutput(comp_cacti_output_filename)

    new_row = comp.get_part_header()
    new_row.update(comp_cacti_output.get_data())

    comp_row = power_df.loc[(power_df["component"] == comp.comp)
                            & (power_df["level"] == comp.level) &
                            (power_df["slice"] == comp.slice_size)]

    if comp_row.empty:
        power_df = power_df.append(new_row, ignore_index=True)
        log.info("\n%s", power_df)
    return power_df


def build_arg_parser():
    args = argparse.ArgumentParser(
        description="generate the experiment script")

    args.add_argument(
        "-c",
        "--config",
        action="store",
        help="a path to the yaml config file",
        type=str,
        default="configs/canneal.yaml",
        dest="config_path",
        required=False,
    )

    args.add_argument(
        "-d",
        action="store_true",
        help="debugging this script and print out all debugging messages",
        dest="debug",
        default=False,
    )

    args.add_argument(
        "-r",
        action="store_true",
        help=
        "Regenerate the McPAT output file even though it was already done.",
        dest="rerun",
        default=False,
    )
    return args


def main():
    arg_parser = build_arg_parser()
    args = arg_parser.parse_args()

    if args.debug:
        log_level = log.DEBUG
    else:
        log_level = log.INFO

    log.basicConfig(
        format=
        "[%(levelname)s m:%(module)s f:%(funcName)s l:%(lineno)s]: %(message)s",
        level=log_level)

    log.info("config path: %s", args.config_path)
    subex_lst = rrex.generate_subexperiments()
    power_df = pd.DataFrame(columns=headers)

    power_filepath = os.path.join("power_info.csv")
    if os.path.exists(power_filepath) and not args.rerun:
        log.info("%s already exists, so skip rerunning cacti", power_filepath)
        power_df = pd.read_csv(power_filepath)
        display_data(power_df)
        exit(0)

    for subex in subex_lst:
        subex_suffix = subex.get_string_suffix()
        log.info("subex %s", subex_suffix)

        if subex.get_l2tlb_slice() > 0:
            comp_l2tlb = Component(
                "tlb",
                2,
                subex.get_l2tlb_slice(),
                subex.get_tlb_size_byte(),
                ASSOC,
            )

            power_df = create_config_and_run(power_df, comp_l2tlb, NCORE)
        else:
            log.info("l2tlb is ignored since its slice is zero")

        if subex.get_l2cache_slice() > 0:
            comp_l2cache = Component(
                "cache",
                2,
                subex.get_l2cache_slice(),
                subex.get_l2cache_size_byte(),
                ASSOC,
            )

            power_df = create_config_and_run(power_df, comp_l2cache, NCORE)
        else:
            log.info("l2cache is ignored since its slice is zero")

        if subex.get_l3cache_slice() > 0:
            comp_l3cache = Component(
                "cache",
                3,
                subex.get_l3cache_slice(),
                subex.get_l3cache_size_byte(),
                ASSOC,
            )

            power_df = create_config_and_run(power_df, comp_l3cache, NCORE)
        else:
            log.info("l3cache is ignored since its slice is zero")
        print("-" * 5)

    power_df = power_df.sort_values(by=["component", "level", "slice"])
    power_df = power_df.reset_index()
    power_df.to_csv(power_filepath, index=False)
    display_data(power_df)
    print("-" * 70)


if __name__ == '__main__':
    # log = logging.getLogger(__file__)
    main()
