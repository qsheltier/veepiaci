import os

import hash


def verify_checksums(checksum_file, directory, on_file_hashed=None, on_finished=None):
    existing_files = collect_files(directory)
    files_with_checksum = checksum_file.file_checksums.keys()
    missing_files = [file for file in filter(lambda f: f not in existing_files, files_with_checksum)]
    additional_files = [file for file in filter(lambda f: f not in files_with_checksum, existing_files)]
    mismatches = []
    for existing_file in filter(lambda f: f in files_with_checksum, existing_files):
        filename = os.path.join(directory, existing_file)
        file_hash = hash.create_hash(filename)
        existing_hashes = checksum_file.file_checksums[existing_file]
        hash_checks_out = True
        for (hash_to_check) in existing_hashes:
            if file_hash[hash_to_check] != existing_hashes[hash_to_check]:
                mismatches.append(existing_file)
                hash_checks_out = False
        if on_file_hashed:
            on_file_hashed(existing_file, file_hash, hash_checks_out)
    verification_result = VerificationResult(mismatches, missing_files, additional_files)
    if on_finished is not None:
        on_finished(verification_result)
    return verification_result


def collect_files(directory):
    file_list = []
    for path, dirs, files in os.walk(directory):
        relative_path = path.removeprefix(directory).removesuffix("/")
        for file in files:
            file_list.append((relative_path + "/" + file).removeprefix("/"))
    return file_list


class VerificationResult:
    def __init__(self, mismatches: list, missing_files: list, additional_files: list):
        self.mismatches = mismatches
        self.missing_files = missing_files
        self.additional_files = additional_files
        self.success = not mismatches and not missing_files and not additional_files
