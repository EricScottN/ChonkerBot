import argparse
from config.all_global_variables import ActiveChannels, Arguments


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("-jum", "--jumble", type=int, help='Set seconds until next jumble')
    parser.add_argument("-t", "--testing", default=False)
    args = parser.parse_args()
    if args.testing:
        ActiveChannels.set_all_channels_to_test()
    if args.jumble is not None:
        Arguments.jumble_countdown = args.jumble

