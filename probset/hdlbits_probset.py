from probset import probset

class HDLBitsProbSet(probset.ProbSet):
    """ has many similarities with HDLBitsData in HDLBits_data_manager.py"""
    def __init__(self, path:str=None, more_info_paths:list=[], only_tasks:list=None, exclude_tasks:list=[], filter_content:dict={}):
        super().__init__("task_id", path=path, moreinfo_path_list=more_info_paths, only=only_tasks, exclude=exclude_tasks, filter=filter_content)

    @property
    def task_id_list(self):
        """
        return a list of task_id
        """
        return [i["task_id"] for i in self.data]
    
    def create_empty_set_via_taskids(self, task_id_list):
        """
        return a dictlist with only the task_id in the task_id_list
        """
        self.data = [{"task_id": i} for i in task_id_list]

    def access_data_via_taskid(self, task_id):
        """
        return a dict in all the information of the task_id
        """
        for i in self.data:
            if i["task_id"] == task_id:
                return i
        raise ValueError("task_id %s not found!!!" % (task_id))