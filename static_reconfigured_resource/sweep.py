import re
import glob
import itertools
import os

scaling_factors = (8, 4, 2, 1, 1 / 2, 1 / 4, 1 / 8)
default_factors = (1, 1, 1, 1, 1, 1, 1)


def get_file_number(filepath):
    filename = os.path.basename(filepath)
    search_obj = re.search(r'stats_t(\d+).txt', filename)
    fileno = search_obj.group(1)
    return int(fileno)


def get_stat_file(dirpath):
    file_pattern = os.path.join(dirpath, "stats_t*.txt")
    stat_files = glob.glob(file_pattern)
    stat_files.sort(key=get_file_number)
    return stat_files


def get_factor_string(level, factor):
    factor_str = "l" + str(level)
    if factor >= 1:
        factor_str += "m" + str(int(factor))
    else:
        factor_str += "d" + str(int(1 / factor))

    return factor_str


def get_string_scaling_factor(scaling_factors):
    suffix_string = []
    for index, scaling in enumerate(scaling_factors):
        tlb_level = index + 1
        suffix = get_factor_string(tlb_level, scaling)
        suffix_string.append(suffix)
    return "_".join(suffix_string)


def get_cartesian_product_factor(tlb_levels):
    l1_factors = default_factors
    l2_factors = default_factors
    if 1 in tlb_levels and 2 in tlb_levels:
        l1_factors = scaling_factors
        l2_factors = scaling_factors
    elif 1 in tlb_levels:
        l1_factors = scaling_factors
    elif 2 in tlb_levels:
        l2_factors = scaling_factors
    else:
        raise ValueError("it should not fail into this case")

    cartesian_product = itertools.product(l1_factors, l2_factors)
    cartesian_product_set = list(set(cartesian_product))
    cartesian_product_set.sort(key=lambda x: x[0] * x[1])
    return cartesian_product_set


# [(0.125, 1), (0.25, 1), (0.5, 1), (1, 1), (2, 1), (4, 1), (8, 1)]
def generate_folder_name(prefix, scaling_tlb_levels):
    tlb_level_set = get_cartesian_product_factor(scaling_tlb_levels)
    folder_name_lst = []
    for aset in tlb_level_set:
        suffix_string = []

        for index, scaling in enumerate(aset):
            tlb_level = index + 1
            suffix = get_factor_string(tlb_level, scaling)
            suffix_string.append(suffix)

        folder_suffix = "_".join(suffix_string)
        folder_name = "_".join([prefix, folder_suffix])
        folder_name_lst.append(folder_name)
    return folder_name_lst


def get_end_file_number(bm_prefix, sub_experiment_paths):
    total_file_num = []
    for apath in sub_experiment_paths:
        stat_files = get_stat_file(apath)
        total_file_num.append(len(stat_files))
    return min(total_file_num)
