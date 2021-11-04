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
        self.animals = FilePaths.csv_animals
        self.thanks = FilePaths.json_thanks
        self.jumblies_time = FilePaths.json_jumbles_time
        self.psn = FilePaths.json_psn
        self.rdowords = FilePaths.csv_rdo_words
        self.winelines = FilePaths.txt_winelines
        self.pics_n_gifs = FilePaths.json_pics_n_gifs
        self.eightball = FilePaths.txt_eightball

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

    def load_animals(self):
        animals_list = []
        with open(self.animals, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                animals_list.append(row[0])
        return animals_list

    def load_jumblies_time(self):
        with open(self.jumblies_time) as jumblies_time_file:
            jumblies_time_dict = json.load(jumblies_time_file)
            return jumblies_time_dict

    def dump_jumblies_time(self, updated_jumblies_time):
        with open(self.jumblies_time, 'w') as jumblies_time_file:
            json.dump(updated_jumblies_time, jumblies_time_file, indent=4, default=str)

    def load_thanks(self):
        with open(self.thanks) as thanks_file:
            thanks_dict = json.load(thanks_file)
            return thanks_dict

    def dump_thanks(self, updated_thanks):
        with open(self.thanks, 'w') as thanks_file:
            json.dump(updated_thanks, thanks_file, indent=4)

    def load_psn(self):
        with open(self.psn) as psn_file:
            psn_dict = json.load(psn_file)
            return psn_dict

    def dump_psn(self, updated_psn):
        with open(self.psn, 'w') as psn_file:
            json.dump(updated_psn, psn_file, indent=4)

    def copy_thx_file(self, date):
        file_name = self.thanks
        index = file_name.find('.json')
        new_file_path = file_name[:index] + "_" + date + file_name[index:]
        shutil.copyfile(self.thanks, new_file_path)

    def load_rdowords(self):
        rdowords_list = []
        with open(self.rdowords, "r") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',')
            for row in csv_reader:
                rdowords_list.append(row[0])
        return rdowords_list

    def load_wine(self):
        winelines = open(self.winelines)
        content = winelines.read()
        wine_list = content.splitlines()
        winelines.close()
        return wine_list

    def load_ball(self):
        eightballlines = open(self.eightball)
        content = eightballlines.read()
        responses = content.splitlines()
        eightballlines.close()
        return responses

    def add_wine(self, line):
        with open(self.winelines, "a") as txt_file:
            txt_file.write(f'\n{line}')

    def load_pics_n_gifs(self):
        with open(self.pics_n_gifs) as pics_n_gifs_file:
            pics_n_gifs_dict = json.load(pics_n_gifs_file)
            return pics_n_gifs_dict

    def dump_pics_n_gifs(self, updated_pics_n_gifs):
        with open(self.pics_n_gifs, 'w') as pics_n_gifs_file:
            json.dump(updated_pics_n_gifs, pics_n_gifs_file, indent=4)

fileloader = FileLoader()