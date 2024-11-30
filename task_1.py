import concurrent.futures
import os
import time


def find_keywords_in_file(file_path, keywords):
    """
    :param file_path: The path of the file to be searched for keywords.
    :param keywords: A list of keywords to search for within the file.
    :return: A dictionary where keys are keywords and values are lists of file paths in which the keywords were found.
    """
    keyword_files = {keyword: [] for keyword in keywords}

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
            words = content.split()

            for keyword in keywords:
                if keyword in words:
                    keyword_files[keyword].append(file_path)
    except FileNotFoundError:
        print("The directory does not exist.")
    except Exception as e:
        print(f"An error occurred: {e}")

    return keyword_files


def find_keywords_in_files(directory, keywords):
    """
    :param directory: The path to the directory containing files to search for keywords.
    :param keywords: A list of keywords to search for within the files.
    :return: A dictionary where keys are keywords and values are lists of file paths that contain the respective keyword.
    """
    files = [os.path.join(directory, filename) for filename in os.listdir(directory)]

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        keyword_files = {}
        for result in executor.map(lambda file_path: find_keywords_in_file(file_path, keywords), files):
            for keyword, paths in result.items():
                if keyword not in keyword_files:
                    keyword_files[keyword] = []
                keyword_files[keyword].extend(paths)

    return keyword_files


user_input = input("Enter keywords separated by commas: ")
keywords = [keyword.strip() for keyword in user_input.split(',') if keyword.strip()]

start_time = time.time()

result = find_keywords_in_files('./dist', keywords)

elapsed_time = time.time() - start_time
print(f"Execution time: {elapsed_time:.10f} seconds")
print(result)
