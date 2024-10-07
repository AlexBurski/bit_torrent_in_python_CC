import json
import sys
import hashlib

import bencodepy

# import requests - available if you need it!


def decode_bencode(bencoded_value):
    bc = bencodepy.Bencode(encoding=None)
    decoded_value = bc.decode(bencoded_value)
    return decoded_value


def parse_element(data, index):
    if data[index : index + 1] == b"d":
        index += 1
        while data[index : index + 1] != b"e":
            index = parse_element(data, index)
            index = parse_element(data, index)
        index += 1
        return index
    elif data[index : index + 1] == b"l":
        index += 1
        while data[index : index + 1] != b"e":
            index = parse_element(data, index)
        index += 1
        return index
    elif data[index : index + 1] == b"i":
        index += 1
        end_index = data.index(b"e", index)
        index = end_index + 1
        return index
    elif data[index : index + 1].isdigit():
        colon_index = data.index(b":", index)
        length = int(data[index:colon_index])
        index = colon_index + 1 + length
        return index
    else:
        raise ValueError(f"Invalid bencode at position {index}")


def bytes_to_str(data):
    if isinstance(data, bytes):
        try:
            return data.decode("utf-8")
        except UnicodeDecodeError:
            return repr(data)

    elif isinstance(data, dict):
        return {bytes_to_str(k): bytes_to_str(v) for k, v in data.items()}

    elif isinstance(data, list):
        return [bytes_to_str(v) for v in data]

    else:
        return data


def main():
    command = sys.argv[1]
    if command == "decode":
        bencoded_value = sys.argv[2].encode()
        decoded_value = decode_bencode(bencoded_value)
        decoded_str = bytes_to_str(decoded_value)
        print(json.dumps(decoded_str))
        # json.dumps() can't handle bytes, but bencoded "strings" need to be
        # bytestrings since they might contain non utf-8 characters.
        #
        # Let's convert them to strings for printing to the console.

        # Uncomment this block to pass the first stage
        # print(json.dumps(decode_bencode(bencoded_value), default=bytes_to_str))

    elif command == "info":
        file_to_read = sys.argv[2]
        with open(file_to_read, "rb") as f:
            bencoded_value = f.read()
            # print(bencoded_value)
            decoded_dict = decode_bencode(bencoded_value)

            # Uncomment this block to pass the first stage

            tracker_url = decoded_dict.get(b"announce").decode("utf-8")
            file_length = decoded_dict.get(b"info", {}).get(b"length")

            info_key = b"4:info"
            info_key_pos = bencoded_value.index(info_key)
            info_start = info_key_pos + len(info_key)
            info_end = parse_element(bencoded_value, info_start)
            bencoded_info = bencoded_value[info_start:info_end]

            info_hash = hashlib.sha1(bencoded_info).hexdigest()

            print(f"Tracker URL: {tracker_url}")
            print(f"Length: {file_length}")
            print(f"Info Hash: {info_hash}")

    else:
        raise NotImplementedError(f"Unknown command {command}")


if __name__ == "__main__":
    main()
