import os
import logging as log
import enum
import math

# slice is the partitioned area allocated to other components.
slice_options = (0, 1, 2, 4, 8, 16)
max_slice = 16
# Total byte per core is calculated by summing
# total bytes/bits used to implement a components such as l2 cache, l3 cache,
# and l2 tlb.
# l2 cache 256KB
# l3 cache 2MB, 8 MB 16 assoc for 4 cores, 2 MB 4 asoc per core.
# l2 tlb: 1536 entries, 8 bytes per entry
# 1536 * 8 + 256KB + 2MB = total_byte_per_core
total_byte_per_core = 2371584
total_byte_per_core_per_size_slice = total_byte_per_core / max_slice

BYTE_PER_TLB_ENTRY = 8
BYTE_PER_CACHE_LINE = 64
# variables to be replaced
# stlb_entry
# l2cache_size
# l3cache_size
RSIM_CONFIG_TEMPLATE = """\
; this is a configuration file based on the skylake processor.

[general]
ncore = 1
coreType = guest

;======================================================================
[dtlb]
entry = 64
nway = 4
; can be either true_lru or random
evictedPolicy = true_lru

[stlb]
entry = {stlb_entry}
nway = 4
evictedPolicy = true_lru

[ntlb]
entry = 16
nway = 16
evictedPolicy = true_lru
;======================================================================
[l1dcache]
sizeKiloByte = 32
nway = 8
lineSizeByte = 64
storeType = store_allocate
cachingPolicy = caching_top

[l2cache]
sizeKiloByte = {l2cache_size}
nway = 4
lineSizeByte = 64
storeType = store_allocate
cachingPolicy = caching_top

[l3cache]
sizeKiloByte = {l3cache_size}
nway = 4
lineSizeByte = 64
storeType = store_allocate
cachingPolicy = caching_inclusive

;======================================================================
[pscl4]
nentry = 2

[pscl3]
nentry = 4

[pscl2]
nentry = 32

;======================================================================
[dtlb_prefetch]
enable = false
nentry = 16

[stlb_prefetch]
enable = false
nentry = 16
"""


def mkdir(dirpath):
    if not os.path.exists(dirpath):
        os.mkdir(dirpath)


def write_file(filepath, file_content):
    log.info("writing %s", filepath)
    with open(filepath, "w") as fopen:
        fopen.write(file_content)


def log2(x, base):
    return int(math.log(x) / math.log(base))


# Compute power of two greater than or equal to `n`
def find_nearest_lower_power_of_2(n):
    '''
    decrement `n` (to handle the case when `n` itself
    is a power of 2)
    '''
    n = n

    # calculate the position of the last set bit of `n`
    lg = log2(n, 2)
    # next power of two will have a bit set at position `lg + 1`.
    return 1 << lg


def generate_subexperiments():
    subex_lst = []
    count = 0
    for l3c_slice in slice_options:
        for l2c_slice in slice_options:
            l2tlb_slice = max_slice - l2c_slice - l3c_slice
            if l2tlb_slice < 0:
                continue

            log.info(
                "%-3u l2tlb_slice %-3u l2c_slice %-3u l3c_slice %-3u",
                count,
                l2tlb_slice,
                l2c_slice,
                l3c_slice,
            )

            if l3c_slice > 0 and l2c_slice > l3c_slice:
                continue
            calculate_structure(Component.Tlb, "l2tlb", l2tlb_slice)
            calculate_structure(Component.Cache, "l2cache", l2c_slice)
            calculate_structure(Component.Cache, "l3cache", l3c_slice)

            subex = Subexperiment(l2tlb_slice, l2c_slice, l3c_slice)
            subex_lst.append(subex)
            count += 1
    log.info("count %u", count)

    return subex_lst


class Component(enum.Enum):
    Cache = 1
    Tlb = 2


def get_num_set(size_byte, byte_per_set):
    return int(math.ceil(size_byte / byte_per_set))


def get_cache_set(size_byte):
    # each cache line has 64 bytes, and a set has 4 ways
    byte_per_set = BYTE_PER_CACHE_LINE * 4
    return get_num_set(size_byte, byte_per_set)


def get_tlb_set(size_byte):
    # each entry has 8 bytes, and a set has 4 ways.
    byte_per_set = BYTE_PER_TLB_ENTRY * 4
    return get_num_set(size_byte, byte_per_set)


def calculate_structure(component, dev_name, slice_portion):
    space = " " * 4
    if component == Component.Cache:
        nset = get_cache_set(slice_portion *
                             total_byte_per_core_per_size_slice)
        log.debug(
            "%s %s cache size byte %.03e nset %u",
            space,
            dev_name,
            float(slice_portion * total_byte_per_core_per_size_slice),
            nset,
        )

    elif component == Component.Tlb:
        nset = get_tlb_set(slice_portion * total_byte_per_core_per_size_slice)
        log.debug(
            "%s %s tlb byte %.03e nset %u",
            space,
            dev_name,
            float(slice_portion * total_byte_per_core_per_size_slice),
            nset,
        )
    else:
        raise ValueError("value error")

    return nset


class Subexperiment:
    TLB_NWAY = 4
    CACHE_NWAY = 4
    KILO_BYTE = 2**10

    def __init__(self, l2tlb_slice, l2c_slice, l3c_slice):
        self.l2tlb_slice = l2tlb_slice
        self.l2c_slice = l2c_slice
        self.l3c_slice = l3c_slice

    def get_l2tlb_slice(self):
        return self.l2tlb_slice

    def get_l2cache_slice(self):
        return self.l2c_slice

    def get_l3cache_slice(self):
        return self.l3c_slice

    def get_l2cache_size_byte(self):
        return self.get_cache_size_byte(self.l2c_slice) * self.KILO_BYTE

    def get_l3cache_size_byte(self):
        return self.get_cache_size_byte(self.l3c_slice) * self.KILO_BYTE

    def get_string_suffix(self):
        return "l2tlbs{l2tlbs:02d}_l2cs{l2cs:02d}_l3cs{l3cs:02d}".format(
            l2tlbs=self.l2tlb_slice, l2cs=self.l2c_slice, l3cs=self.l3c_slice)

    def get_config_filepath(self, output_dir):
        filename = "skylake_{suffix}.ini".format(
            suffix=self.get_string_suffix())
        filepath = os.path.join(output_dir, filename)
        return filepath

    def get_tlb_entry(self):
        tlb_size_byte = self.l2tlb_slice * total_byte_per_core_per_size_slice
        tlb_nentry = math.ceil(tlb_size_byte) / BYTE_PER_TLB_ENTRY
        if tlb_nentry == 0:
            return tlb_nentry

        tlb_nset = tlb_nentry / self.TLB_NWAY

        # make sure that the number of tlb sets must be one of the power of 2.
        tlb_nset_power_of_2 = find_nearest_lower_power_of_2(tlb_nset)
        tlb_nentry_power_of_2 = tlb_nset_power_of_2 * self.TLB_NWAY
        return int(tlb_nentry_power_of_2)

    def get_tlb_size_byte(self):
        return self.get_tlb_entry() * BYTE_PER_TLB_ENTRY

    def get_cache_size_byte(self, cache_slice):
        '''
        return the cache in kilo bytes
        '''
        cache_size_byte = cache_slice * total_byte_per_core_per_size_slice
        if cache_size_byte == 0:
            return cache_size_byte

        cache_nset = cache_size_byte / (self.CACHE_NWAY * BYTE_PER_CACHE_LINE)
        cache_nset_power_of_2 = find_nearest_lower_power_of_2(cache_nset)
        cache_size_byte = cache_nset_power_of_2 * self.CACHE_NWAY * BYTE_PER_CACHE_LINE
        return int(math.ceil(cache_size_byte / self.KILO_BYTE))

    def write_configs(self, output_dir):
        content = RSIM_CONFIG_TEMPLATE.format(
            stlb_entry=self.get_tlb_entry(),
            l2cache_size=self.get_cache_size_byte(self.l2c_slice),
            l3cache_size=self.get_cache_size_byte(self.l3c_slice))

        filepath = self.get_config_filepath(output_dir)
        write_file(filepath, content)


if __name__ == '__main__':
    log.basicConfig(
        format=
        "[%(levelname)s m:%(module)s f:%(funcName)s l:%(lineno)s]: %(message)s",
        level=log.DEBUG)
    generate_subexperiments()
