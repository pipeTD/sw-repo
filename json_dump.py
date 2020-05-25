#
# Exec. save_json(data, '/Users/mharris/bin/scratch_dump.json', overwrite=True)
#

import os
import json
import errno


def save_json(data, file_path, overwrite=False):
    """
    Saves the given data into the file path given
    :param data: Dict
    :param file_path: String - Path to file
    :param overwrite: Boolean - If true then overwrite the file
    :return: String - Resulting file path
    """

    directory = os.path.dirname(file_path)

    try:
        os.makedirs(directory)
    except OSError, e:
        if e.errno != errno.EEXIST:
            raise

    with open(file_path, 'w') as write_file:
        json.dump(data, write_file, indent=4, default=str)

    return file_path
