import os
import tempfile
import unittest

import verify
from checksumfile import ChecksumFile


class VerifyTest(unittest.TestCase):

    def test_verify_reports_success_when_all_files_match(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            with open(os.path.join(temp_directory, "empty.dat"), "wb"):
                pass
            with open(os.path.join(temp_directory, "data.dat"), "wb") as empty:
                empty.write(bytearray(range(256)))
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify_result = verify.verify_checksums(checksum_file, temp_directory)
            self.assertTrue(verify_result.success)

    def test_verify_reports_failure_when_a_file_does_not_match(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            with open(os.path.join(temp_directory, "empty.dat"), "wb"):
                pass
            with open(os.path.join(temp_directory, "data.dat"), "wb") as empty:
                empty.write(bytearray(range(256)))
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427f"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify_result = verify.verify_checksums(checksum_file, temp_directory)
            self.assertFalse(verify_result.success)
            self.assertEqual(verify_result.mismatches, ["empty.dat"])
            self.assertEqual(verify_result.missing_files, [])
            self.assertEqual(verify_result.additional_files, [])

    def test_verify_reports_failure_when_a_file_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            with open(os.path.join(temp_directory, "empty.dat"), "wb"):
                pass
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify_result = verify.verify_checksums(checksum_file, temp_directory)
            self.assertFalse(verify_result.success)
            self.assertEqual(verify_result.mismatches, [])
            self.assertEqual(verify_result.missing_files, ["data.dat"])
            self.assertEqual(verify_result.additional_files, [])

    def test_verify_reports_failure_when_an_additional_file_is_present(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            with open(os.path.join(temp_directory, "empty.dat"), "wb"):
                pass
            with open(os.path.join(temp_directory, "data.dat"), "wb") as empty:
                empty.write(bytearray(range(256)))
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}})
            verify_result = verify.verify_checksums(checksum_file, temp_directory)
            self.assertFalse(verify_result.success)
            self.assertEqual(verify_result.mismatches, [])
            self.assertEqual(verify_result.missing_files, [])
            self.assertEqual(verify_result.additional_files, ["data.dat"])

    def test_verify_calls_event_handler_for_every_file_it_hashes(self):
        hashed_files = []
        with tempfile.TemporaryDirectory() as temp_directory:
            with open(os.path.join(temp_directory, "empty.dat"), "wb"):
                pass
            with open(os.path.join(temp_directory, "data.dat"), "wb") as empty:
                empty.write(bytearray(range(256)))
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify.verify_checksums(checksum_file, temp_directory, lambda f, h: hashed_files.append(f))
            self.assertCountEqual(hashed_files, ["data.dat", "empty.dat"])

    def test_verify_does_not_call_event_handler_when_a_file_does_not_have_a_hash(self):
        hashed_files = []
        with tempfile.TemporaryDirectory() as temp_directory:
            with open(os.path.join(temp_directory, "empty.dat"), "wb"):
                pass
            with open(os.path.join(temp_directory, "data.dat"), "wb") as empty:
                empty.write(bytearray(range(256)))
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}})
            verify.verify_checksums(checksum_file, temp_directory, lambda f, h: hashed_files.append(f))
            self.assertEqual(hashed_files, ["empty.dat"])

    def test_verify_does_not_call_event_handler_when_a_file_does_not_exist(self):
        hashed_files = []
        with tempfile.TemporaryDirectory() as temp_directory:
            with open(os.path.join(temp_directory, "data.dat"), "wb") as empty:
                empty.write(bytearray(range(256)))
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify.verify_checksums(checksum_file, temp_directory, lambda f, h: hashed_files.append(f))
            self.assertEqual(hashed_files, ["data.dat"])