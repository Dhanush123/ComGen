import ntpath


def get_filename_from_path(path):
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def get_filename_noext(filename):
    return get_filename_from_path(
        filename).rsplit(".", maxsplit=1)[0]
