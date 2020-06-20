import os

import ray

from comgen.logic.data.process import create_relevant_dirs, process_file, combine_data, filtered_dir, ast_dir

if __name__ == '__main__':
    ray.init()
    create_relevant_dirs()
    futures = [process_file.remote(a_file.path)
               for a_file in os.scandir(filtered_dir)]
    ray.get(futures)
    print("Shutting down Ray...")
    ray.shutdown()
    print(f'Processed {len(futures)} files')
    combine_data(ast_dir)
