#!/usr/bin/python3
import sys, argparse
from halo8thruster.driver.listener import Listener

PORT_RAW   = 4000
PORT_HSI   = 4001
PORT_TRACE = 4002

def main():
    parser = argparse.ArgumentParser(description='Listens for exoserial data on the local network (udp).')
    parser.add_argument('--trace',  action='store_true', help='Enables Trace Mode.')
    parser.add_argument('--hsi',    action='store_true', help='Enables HSI Mode.')
    parser.add_argument('--gui',    action='store_true', help='Enables Gui.')
    parser.add_argument('--socket', type=str, default="127.0.0.1", help='The Network host to bind to.')
    parser.add_argument('--port',   type=int, default=None, help='The port to listen on.')
    args = parser.parse_args()

    if args.trace:
        mode, port = "trace", args.port or PORT_TRACE
        print(f"Listening for trace msgs {args.socket}:{port}.")
        print("Enabled Trace Mode.")
    elif args.hsi:
        mode, port = "hsi", args.port or PORT_HSI
        print(f"Listening for hsi and trace msgs {args.socket}:{port}.")
        print("Enabled HSI Mode.")
    elif args.gui:
        mode, port = "gui", args.port or PORT_HSI
        print("Enabled HSI-GUI Mode.")
    else:
        mode, port = "raw", args.port or PORT_RAW
        print("Enabled Raw Mode.")
        print(f"Listening for exoserial msgs on {args.socket}:{port}.")

    try:
        Listener(mode, args.socket, port).run()
    except OSError as e:
        print(e)
        sys.exit(1)

if __name__ == "__main__":
    main()
