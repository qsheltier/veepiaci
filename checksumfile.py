class ChecksumFile:
    """Contains all checksums that have been created for a number of files."""

    def __init__(self, type, file_checksums):
        """Create a new ChecksumFile of the given type, containing the given checksums."""
        self.type = type
        """The type of the checksum file (i.e. “UltraISO” for files created by UltraISO)."""
        self.file_checksums = file_checksums
        """A dictionary of files and their checksums."""


def read_checksum_file(filename):
    """Read the given file and parse it into a `ChecksumFile` object."""
    file_checksums = {}
    with open(filename, "r", encoding="latin-1") as file:
        first_line = file.readline()
    if "UltraISO" in first_line:
        encoding = "windows-1252"
    else:
        encoding = "utf-8"
    with open(filename, "r", encoding=encoding) as file:
        file.readline()
        file.readline()
        file.readline()
        for line in file:
            line_parts = line.split(" ", 1)
            checksum = line_parts[0]
            checked_file = line_parts[1].strip().removeprefix("*")
            file_checksums[checked_file] = {"md5": checksum}
    return ChecksumFile("UltraISO", file_checksums)
