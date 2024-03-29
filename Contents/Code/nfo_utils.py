import os


def find_nfo_file_in_folder(folder):
    answer = None
    extension = "nfo"
    nfo_files = [file for file in os.listdir(folder) if file.endswith(extension)]
    if len(nfo_files) == 1:
        answer = os.path.join(folder, nfo_files[0])

    return answer
