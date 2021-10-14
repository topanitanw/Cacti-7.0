import os
import logging as log
import argparse
import copy


def clean_line(line):
    # remove the last comma
    return line.strip().strip("\n").strip("\t").strip(",")


def split_line(line):
    return line.split(", ")


def clean_split_line(line):
    return split_line(clean_line(line))


class CactiOutput:
    def __init__(self, filepath):
        assert os.path.exists(filepath), \
            "%s does not exist" % filepath

        self.filepath = filepath
        self.data = {}

        self.readfile(filepath)

    def readfile(self, filepath):
        with open(filepath, "r") as fo:
            raw_header = fo.readline()
            header = clean_split_line(raw_header)
            log.debug("header: %s", header)

            raw_value = fo.readline()
            value = clean_split_line(raw_value)
            log.debug("value: %s", value)

        for i in range(len(header)):
            if value[i] == "N/A":
                log.warning("set %s from %s to %ld", header[i], value[i], -1)
                value[i] = -1

            log.debug("saving: %s: %s", header[i], value[i])
            self.data[header[i]] = float(value[i])

    def get_data(self):
        return copy.deepcopy(self.data)

    def get_capacity(self):
        return self.data["Capacity (bytes)"]

    def get_access_time(self):
        return self.data["Access time (ns)"]

    def get_dynamic_read_energy(self):
        return self.data["Dynamic read energy (nJ)"]

    def get_dynamic_write_energy(self):
        return self.data["Dynamic write energy (nJ)"]

    def get_standby_leakage_energy(self):
        return self.data["Standby leakage per bank(mW)"] \
            * self.data["Number of banks"]

    def get_area(self):
        return self.data["Area (mm2)"]


def build_arg_parser():
    args = argparse.ArgumentParser(
        description="generate the experiment script")

    args.add_argument("-i",
                      "--input_out_path",
                      action="store",
                      help="a path to the Cacti output .out file",
                      type=str,
                      default="cache.cfg.out",
                      dest="input_out_path",
                      required=False)

    args.add_argument(
        "-d",
        action="store_true",
        help="debugging this script and print out all debugging messages",
        dest="debug",
        default=False,
    )
    return args


def main():
    arg_parser = build_arg_parser()
    args = arg_parser.parse_args()

    if args.debug:
        log_level = log.DEBUG
    else:
        log_level = log.ERROR

    log.basicConfig(
        format=
        "[%(levelname)s m:%(module)s f:%(funcName)s l:%(lineno)s]: %(message)s",
        level=log_level)

    assert os.path.exists(args.input_out_path), \
        "%s does not exist" % args.input_out_path

    CactiOutput(args.input_out_path)


if __name__ == '__main__':
    main()
