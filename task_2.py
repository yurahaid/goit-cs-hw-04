import os
import time
from multiprocessing import Queue
from multiprocessing import Pool, Manager


def find_keywords_in_file(files_queue: Queue, result_queue: Queue, keywords: list):
    """
    :param files_queue: A queue object containing file paths to be processed.
    :param result_queue: A queue object where the result will be put.
    :param keywords: A list of keywords to search for within each file.
    :return: This function does not return a value. It operates primarily through the side effect of putting results in the `result_queue`.
    """
    while True:
        file_path = files_queue.get()
        if file_path is None:
            break

        keyword_files = {keyword: [] for keyword in keywords}

        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                words = content.split()

                for keyword in keywords:
                    if keyword in words:
                        keyword_files[keyword].append(file_path)
        except FileNotFoundError:
            print("The file does not exist:", file_path)
        except Exception as e:
            print(f"An error occurred: {e}")

        result_queue.put(keyword_files)


def find_keywords_in_files(directory, keywords):
    """
    :param directory: The path to the directory containing files to search for keywords.
    :param keywords: A list of keywords to search for within the files.
    :return: A dictionary where keys are keywords and values are lists of file paths that contain the respective keyword.
    """
    with Manager() as manager:
        input_queue = manager.Queue()
        result_queue = manager.Queue()

        # Adding file paths to queue before starting processes
        for filename in os.listdir(directory):
            input_queue.put(os.path.join(directory, filename))

        # Add sentinel values to indicate end of the queue
        num_workers = 2
        for _ in range(num_workers):
            input_queue.put(None)

        with Pool(processes=num_workers) as pool:
            args = [(input_queue, result_queue, keywords)] * num_workers
            pool.starmap(find_keywords_in_file, args)

        keyword_files = {keyword: [] for keyword in keywords}
        while not result_queue.empty():
            result = result_queue.get()
            for keyword, paths in result.items():
                keyword_files[keyword].extend(paths)

        return keyword_files


user_input = input("Enter keywords separated by commas: ")

keywords = [keyword.strip() for keyword in user_input.split(',') if keyword.strip()]

start_time = time.time()

result = find_keywords_in_files('./dist', keywords)

elapsed_time = time.time() - start_time
print(f"Execution time: {elapsed_time:.10f} seconds")
print(result)
