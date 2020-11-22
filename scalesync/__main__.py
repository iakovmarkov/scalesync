import argparse
import toml
import logging
import time
from bluepy import btle
from processor import ScanProcessor

logLevels = [
    "DEBUG",
    "INFO",
    "WARNING",
    "ERROR",
    "CRITICAL",
]

logFormats = {
    "LONG": "%(asctime)s - %(message)s",
    "SHORT": "%(message)s",
}


def main():
    config = toml.load('config.toml')
    config['users'].sort(key=lambda user: user['weight_threshold'], reverse=True)

    parser = argparse.ArgumentParser(description='Sync your Xiaomi smart scale with weight tracking apps.')
    parser.add_argument('--hci', default='hci0', help='Which HCI device to use')
    parser.add_argument('--interval', default=5, help='How often the scan should trigger')
    parser.add_argument(
        "--logFormat",
        help="Log format. Can be SHORT or LONG",
        default="LONG",
    )
    parser.add_argument(
        "--logLevel",
        help=f'Log verbosity. Can be {", ".join(logLevels)}',
        default="INFO",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=args.logLevel,
        format=logFormats[args.logFormat],
        datefmt="%d-%b-%y %H:%M:%S",
    )
    logging.root.setLevel(args.logLevel)
    print(f"Log level is {args.logLevel}")
    
    processor = ScanProcessor(config)

    while True:
        try:
            scanner = btle.Scanner(args.hci[-1]).withDelegate(processor)
            scanner.scan(5, passive=True) # Adding passive=True to try and fix issues on RPi devices
        except btle.BTLEDisconnectError as error:
            logging.error(f"BTLE disconnected: {error}\n")
            pass
        except btle.BTLEManagementError as error:
            logging.error(f"Bluetooth connection error: {error}\n")
            pass
        
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
