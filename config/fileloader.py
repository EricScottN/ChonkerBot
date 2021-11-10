import json
import csv
import shutil
from config.all_global_variables import FilePaths


class FileNotFoundError(Exception):
    pass


class FileLoader:
    def __init__(self):
        self.template = FilePaths.json_queue_template
        self.current_queues = FilePaths.json_queue_updated
        self.jumblies_time = FilePaths.json_jumbles_time

    def load_queues(self):
        try:
            with open(self.current_queues) as queue_file:
                queues = json.load(queue_file)
                return queues
        except:
            raise FileNotFoundError('Cannot locate json file')

    def dump_queues(self, updated_queue):
        try:
            with open(self.current_queues, 'w') as queue_file:
                json.dump(updated_queue, queue_file, indent=4)
        except:
            raise FileNotFoundError('No current json file')

    def dump_jumblies_time(self, updated_jumblies_time):
        with open(self.jumblies_time, 'w') as jumblies_time_file:
            json.dump(updated_jumblies_time, jumblies_time_file, indent=4, default=str)

    @staticmethod
    def load_json(json_file):
        with open(json_file) as jf:
            result_dict = json.load(jf)
            return result_dict

    @staticmethod
    def dump_json(updated_json, json_file):
        with open(json_file, 'w') as jf:
            json.dump(updated_json, jf, indent=4)

    @staticmethod
    def copy_json_file(date, file_name):
        index = file_name.find('.json')
        new_file_path = file_name[:index] + "_" + date + file_name[index:]
        shutil.copyfile(file_name, new_file_path)

    @staticmethod
    def load_txt(file_name):
        results_lines = open(file_name)
        content = results_lines.read()
        results_list = content.splitlines()
        results_lines.close()
        return results_list

    @staticmethod
    def add_text_line(line, file_name):
        with open(file_name, "a") as txt_file:
            txt_file.write(f'\n{line}')


fileloader = FileLoader()
