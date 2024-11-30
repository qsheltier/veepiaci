import unittest
import os
import tempfile
import hash

class TestHashMethods(unittest.TestCase):

    def test_hash_for_an_empty_file_can_be_created(self):
        with tempfile.TemporaryDirectory() as t:
            f = os.path.join(t, "empty_file")
            with open(f, "w"):
                pass
            created_hash = hash.create_hash(f)
            self.assertIsNotNone(created_hash)

    def test_md5_hash_for_an_empty_file_is_correct(self):
        with tempfile.TemporaryDirectory() as t:
            f = os.path.join(t, "empty_file")
            with open(f, "w"):
                pass
            created_hash = hash.create_hash(f)
            self.assertEqual(created_hash["md5"], "d41d8cd98f00b204e9800998ecf8427e")

    def test_md5_hash_for_a_file_with_content_is_correct(self):
        with tempfile.TemporaryDirectory() as t:
            f = os.path.join(t, "empty_file")
            with open(f, "wb") as temp_file:
                temp_file.write(bytearray(range(256)))
            created_hash = hash.create_hash(f)
            self.assertEqual(created_hash["md5"], "e2c865db4162bed963bfaa9ef6ac18f0")

if __name__ == '__main__':
    unittest.main()
