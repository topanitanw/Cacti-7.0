import sys
import os
import argparse
import logging as log


def build_arg_parser():
    args = argparse.ArgumentParser(
       description="generate the experiment script"
    )

    args.add_argument(
        "-f",
        "--output_file_path",
        action="store",
        help="the path of the output file",
        type=str,
        default=".",
        dest="output_file_path",
        required=False
    )

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

    # warning 30, info 20, debug 10
    log_level = log.INFO
    if args.debug:
        log_level = log.DEBUG

    # never print a logging message before calling basicConfig
    # if you accidentally print a message before calling basicConfig,
    # the logging message will be unable to be printed out.
    mesg_prefix = "[%(levelname)s m:%(module)s f:%(funcName)s l:%(lineno)s]:"
    mesg_body = " %(message)s"
    mesg_format = mesg_prefix + mesg_body
    log.basicConfig(
        format=mesg_format,
        level=log_level,
    )

    if not os.path.exists(args.output_file_path):
        log.error("the output file path does not exist")
        sys.exit(1)


    content_lines = []
    with open(args.output_file_path) as fopen:
        content_lines = fopen.readlines()

    header_lst = content_lines[0].strip().split(",")
    log.info("header_lst: %s", header_lst)

    value_lst = content_lines[1].strip().split(",")
    log.info("value_lst: %s", value_lst)

    for i in range(len(header_lst)):
        log.info("%s header: %s, value: %s", i, header_lst[i], value_lst[i])

    access_time_ns = float(value_lst[5])
    access_time_cycles = access_time_ns * 1e-9 * 4e9
    log.info("access time cycles: %s", access_time_cycles)
    sys.exit(0)


if __name__ == '__main__':
    main()
