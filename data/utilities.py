import ntpath


def get_filename_from_path(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)
