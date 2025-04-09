from copy import deepcopy
from utils import file_util

class ProbSet:
    """
    - a class to manage the list of dict
    - form:

    {
        id_key: "xxx", #the key to identify the dict
        content1: xxx,
        content2: xxx,
        ...
    }
    """
    def __init__(self, id_key:str, path:str=None, moreinfo_path_list:list=[], only:list=None, exclude:list=[], filter:dict={}):
        self.id_key = id_key
        if path is not None:
            try:
                self.data = file_util.read_jsonl_file(path)
            except:
                self.data = file_util.read_json_file(path)
            if moreinfo_path_list != []:
                try:
                    moreinfo = [file_util.read_jsonl_file(moreinfo_path) for moreinfo_path in moreinfo_path_list]
                except:
                    moreinfo = [file_util.read_json_file(moreinfo_path) for moreinfo_path in moreinfo_path_list]
                for info in moreinfo:
                    self.merge(info)
            self.filter(filter)
            self.del_items(only, del_by_list=False)
            self.del_items(exclude)
        else:
            self.data = []

    @property
    def num(self):
        return len(self.data)
        
    def data_clean(self, only=None, exclude=[], filter={}):
        self.del_items(only, del_by_list=False)
        self.del_items(exclude)
        self.filter(filter)

    def find_data_by_id(self, id):
        for prob_data in self.data:
            if prob_data[self.id_key] == id:
                return prob_data
        raise ValueError("Cannot find the problem infomation with %s: "%(self.id_key) + id + ".")

    def merge(self, additional_data):
        """merge additional data into the original data"""
        for data in self.data:
            for add_data in additional_data:
                if data[self.id_key] == add_data[self.id_key]:
                    for key, value in add_data.items():
                        if key != self.id_key:
                            data[key] = value

    def filter(self, filter_dict, del_en=True):
        """
        #### Function
        - filtering the data by the key and value.
        - only the data that has the key and value will remain
        - the output will always be the filtered data, but I recommend to directly use `self.data` to get the filtered data if del_en is True
        #### Input
        - filter_dict: dict; the key and value to filter the data
        - del_en: bool; if True, the data that doesn't have the key and value will be deleted from the data. If False, the data will not change but output the filtered data
        """
        if del_en:
            for key, value in filter_dict.items():
                self.data = [prob_data for prob_data in self.data if prob_data.get(key) == value]
        else:
            filtered_data = deepcopy(self.data)
            for key, value in filter_dict.items():
                filtered_data = [prob_data for prob_data in filtered_data if prob_data.get(key) == value]
            return filtered_data

    def del_items(self, id_list, del_by_list=True):
        """
        - id_list: list of ids
        - del_by_list: bool; if True, data having the task_id in the list will be deleted. If False, the data that doesn't have the task_id in the list will be deleted
        """
        # avoid default list = [] and del_by_list = False to del all the data
        if id_list is not None and id_list != []:
            if del_by_list:
                self.data = [prob_data for prob_data in self.data if prob_data[self.id_key] not in id_list]
            else: # del the data that doesn't have the task_id in the list
                self.data = [prob_data for prob_data in self.data if prob_data[self.id_key] in id_list]