import hashlib
import io

def create_hash(file_name):
    md5_hash = hashlib.new("md5")
    buffer = bytearray(4096)
    with open(file_name, "rb") as file:
        while True:
            read_bytes = file.readinto(buffer)
            if read_bytes == 0:
                break
            md5_hash.update(buffer[:read_bytes])
    return {'md5': md5_hash.hexdigest()}
