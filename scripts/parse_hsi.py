#!/usr/bin/python3
import struct, argparse, csv, sys, datetime
from src.hsi_defines import HSIDefines

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Binary HSI Parser, converts the the hsi binary data into a csv file.')
    parser.add_argument('input_filename', action='store', type=str,
                        help='the binary hsi file to parse')
    parser.add_argument('output_filename', action='store', type=str,
                        help='the name of the csv file',
                        default='out.csv')
    args = parser.parse_args()

    hsi_def = HSIDefines()
    names = [i.get("name") for i in hsi_def.block_hsi]
    names.insert(0,"timestamp")
    csv_file = open(args.output_filename, "w+")
    csv_w = csv.DictWriter(csv_file, fieldnames=names)
    csv_w.writeheader()
    header_found = False
    with open(args.input_filename, "rb") as f:
        #look for the header
        header = struct.unpack("<I", f.read(4))[0]
        print(header)
        if header == 0xEE01:
            print("Found Header! version 1 ")
            parse_str = "<IIIIIHHHHHHHIHHHHHHHHHHHHHHHHHHHHHHiIHHHHHHHHHHHHHHIII"
            parse_str_len = 130
            header_found = True
        else:
            #assume version 0
            print("No header found parsing version 0")
            f.seek(0)
            parse_str = "<IIIHHHHHHHIHHHHHHHHHHHHHHHHHHHHHHiIHHHHHHHHHHHHHHIII"
            parse_str_len = 122

        data = f.read(parse_str_len)
        while data:
            #extract ts
            data = f.read(parse_str_len)
            if len(data) != parse_str_len:
                continue
            raw_vals = struct.unpack_from(parse_str, data)
            if header_found:
                date_t = raw_vals[0]
                date_ms = raw_vals[1]
                print(date_t, date_ms)
                raw_vals = raw_vals[2:]
            csv_row = {}
            try:
                for i, value in enumerate(hsi_def.block_hsi):
                    name = value.get("name")
                    hex_en = value.get("hex")
                    parsed_val = raw_vals[i]
                    if hex_en:
                        parsed_val = hex(parsed_val)
                    el = hsi_def.hsi.get(name)
                    if el is not None:
                        r = el.get("row")
                        c = el.get("col")
                        if r is not None and c is not None:
                            csv_row[name] = parsed_val
                            # print(name, parsed_val)
                #append the timestamp to the row
                if header_found:
                    date_float = float(str(date_t)+"."+str(date_ms))
                    print(f"datefloat: {date_float}")
                    csv_row["timestamp"] = datetime.datetime.fromtimestamp(date_float)
                csv_w.writerow(csv_row)
            except Exception as e:
                print(f"Query Failed: {e}")

csv_file.flush()
csv_file.close()