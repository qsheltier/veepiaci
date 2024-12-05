import os
import tempfile
import unicodedata
import unittest

import verify
from checksumfile import ChecksumFile


def create_empty_file(temp_directory, filename="empty.dat"):
    with open(os.path.join(temp_directory, filename), "wb"):
        pass


def create_file_with_data(temp_directory, filename="data.dat"):
    with open(os.path.join(temp_directory, filename), "wb") as empty:
        empty.write(bytearray(range(256)))


class VerifyTest(unittest.TestCase):

    def test_verify_reports_success_when_all_files_match(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            create_file_with_data(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify_result = verify.verify_checksums(checksum_file, temp_directory)
            self.assertTrue(verify_result.success)

    def test_verify_reports_failure_when_a_file_does_not_match(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            create_file_with_data(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427f"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify_result = verify.verify_checksums(checksum_file, temp_directory)
            self.assertFalse(verify_result.success)
            self.assertEqual(verify_result.mismatches, ["empty.dat"])
            self.assertEqual(verify_result.missing_files, [])
            self.assertEqual(verify_result.additional_files, [])

    def test_verify_reports_failure_when_a_file_is_missing(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify_result = verify.verify_checksums(checksum_file, temp_directory)
            self.assertFalse(verify_result.success)
            self.assertEqual(verify_result.mismatches, [])
            self.assertEqual(verify_result.missing_files, ["data.dat"])
            self.assertEqual(verify_result.additional_files, [])

    def test_verify_reports_failure_when_an_additional_file_is_present(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            create_file_with_data(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}})
            verify_result = verify.verify_checksums(checksum_file, temp_directory)
            self.assertFalse(verify_result.success)
            self.assertEqual(verify_result.mismatches, [])
            self.assertEqual(verify_result.missing_files, [])
            self.assertEqual(verify_result.additional_files, ["data.dat"])

    def test_verify_calls_event_handler_for_every_file_it_hashes(self):
        hashed_files = []
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            create_file_with_data(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify.verify_checksums(checksum_file, temp_directory, on_file_hashed=lambda f, h, c: hashed_files.append(f))
            self.assertCountEqual(hashed_files, ["data.dat", "empty.dat"])

    def test_verify_calls_event_handler_for_every_file_it_hashes_with_result_of_hash_check(self):
        hashed_files = []
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            create_file_with_data(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427f"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify.verify_checksums(checksum_file, temp_directory, on_file_hashed=lambda f, h, c: hashed_files.append(f + " " + str(c)))
            self.assertCountEqual(hashed_files, ["data.dat True", "empty.dat False"])

    def test_verify_does_not_call_event_handler_when_a_file_does_not_have_a_hash(self):
        hashed_files = []
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            create_file_with_data(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}})
            verify.verify_checksums(checksum_file, temp_directory, on_file_hashed=lambda f, h, c: hashed_files.append(f))
            self.assertEqual(hashed_files, ["empty.dat"])

    def test_verify_does_not_call_event_handler_when_a_file_does_not_exist(self):
        hashed_files = []
        with tempfile.TemporaryDirectory() as temp_directory:
            create_file_with_data(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify.verify_checksums(checksum_file, temp_directory, on_file_hashed=lambda f, h, c: hashed_files.append(f))
            self.assertEqual(hashed_files, ["data.dat"])

    def test_verify_calls_finish_handler_after_files(self):
        events = []
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            create_file_with_data(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify.verify_checksums(checksum_file, temp_directory, on_file_hashed=lambda f, h, c: events.append(f), on_finished=lambda _: events.append("finish"))
            self.assertCountEqual(events, ["empty.dat", "data.dat", "finish"])
            self.assertEqual(events[-1], "finish")

    def test_verify_calls_finish_handler_with_verification_result(self):
        result_from_event = []
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            create_file_with_data(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "data.dat": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            result = verify.verify_checksums(checksum_file, temp_directory, on_finished=lambda r: result_from_event.append(r))
            self.assertEqual(result_from_event[0], result)

    def test_verify_matches_files_with_umlauts_correctly(self):
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            create_file_with_data(temp_directory, unicodedata.normalize("NFD", "ümläut.txt"))
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}, "ümläut.txt": {"md5": "e2c865db4162bed963bfaa9ef6ac18f0"}})
            verify_result = verify.verify_checksums(checksum_file, temp_directory)
            self.assertTrue(verify_result.success)

    def test_verify_sends_start_of_verification_event_before_first_file(self):
        events = []
        with tempfile.TemporaryDirectory() as temp_directory:
            create_empty_file(temp_directory)
            checksum_file = ChecksumFile("test", {"empty.dat": {"md5": "d41d8cd98f00b204e9800998ecf8427e"}})
            verify.verify_checksums(checksum_file, temp_directory, on_started=lambda d: events.append(d), on_file_hashed=lambda f, h, c: events.append(f))
        self.assertEqual(events, [temp_directory, "empty.dat"])
