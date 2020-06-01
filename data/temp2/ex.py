def get_env_creds():
    try:
        os.chdir(os.getcwd())
        dotenv_path = os.path.join(os.getcwd(), '.env')
        load_dotenv(dotenv_path=dotenv_path)
    except:
        raise AUTH_ERROR


def file_from_path(path):
    '''Get file name from path string'''
    head, tail = ntpath.split(path)
    return tail or ntpath.basename(head)


def arg_dict_to_list(dictionary):
    '''
    hello
    world
    '''
    arg_list = []
    for key, value in dictionary.items():
        arg_list.extend(["--{}".format(key), value])
    return arg_dict_to_list
