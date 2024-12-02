import os

import hash


def verify_checksums(checksum_file, directory):
    all_match = True
    existing_files = collect_files(directory)
    files_with_checksum = checksum_file.file_checksums.keys()
    if not all(file in existing_files for file in files_with_checksum):
        all_match = False
    if not all(file in files_with_checksum for file in existing_files):
        all_match = False
    for existing_file in filter(lambda f: f in files_with_checksum, existing_files):
        filename = os.path.join(directory, existing_file)
        file_hash = hash.create_hash(filename)
        existing_hashes = checksum_file.file_checksums[existing_file]
        for (hash_to_check) in existing_hashes:
            if file_hash[hash_to_check] != existing_hashes[hash_to_check]:
                all_match = False
    return VerifyResult(all_match)


def collect_files(directory):
    file_list = []
    for path, dirs, files in os.walk(directory):
        relative_path = path.removeprefix(directory).removesuffix("/")
        for file in files:
            file_list.append((relative_path + "/" + file).removeprefix("/"))
    return file_list


class VerifyResult:
    def __init__(self, success: bool):
        self.success = success
