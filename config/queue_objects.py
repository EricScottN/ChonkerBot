from config.fileloader import fileloader
from config.all_global_variables import ActivityStrings


class AllQueueObjects:
    def __init__(self):
        self.all_queues = fileloader.load_queues()

    def get_all_queues(self):
        all_queues = self.all_queues
        return all_queues

    def get_queues(self, queue_num):
        all_queues = self.get_all_queues()
        queues = all_queues['all_queues'][queue_num]
        return queues

    def get_hosts_list(self, queue_num, activity):
        queue = self.get_queues(queue_num)
        hosts = queue[activity]['hosts']
        return hosts

    def get_list_of_host_ids(self, activity):
        list_of_host_ids = []
        if activity == ActivityStrings.delivery_str:
            queue_num = 0
        elif activity == ActivityStrings.moonshine_str:
            queue_num = 1
        elif activity == ActivityStrings.bounty_str:
            queue_num = 2
        elif activity == ActivityStrings.nature_str:
            queue_num = 3
        elif activity == ActivityStrings.posse_str:
            queue_num = 4

        hosts_lists = self.get_hosts_list(queue_num, activity)

        if not hosts_lists:
            return list_of_host_ids
        else:
            for host_dict in hosts_lists:
                list_of_host_ids.append(host_dict['host_id'])
            return list_of_host_ids

    def get_host_dict(self, host_id, activity):
        if activity == ActivityStrings.delivery_str:
            queue_num = 0
        if activity == ActivityStrings.moonshine_str:
            queue_num = 1
        if activity == ActivityStrings.bounty_str:
            queue_num = 2
        if activity == ActivityStrings.nature_str:
            queue_num = 3
        if activity == ActivityStrings.posse_str:
            queue_num = 4

        for host_dict in self.get_hosts_list(queue_num, activity):
            if host_dict['host_id'] == host_id:
                return host_dict

    def get_list_of_members(self, host_id, activity):
        host_dict = self.get_host_dict(host_id, activity)
        list_of_members_dicts = host_dict['members']
        return list_of_members_dicts

    def get_queue_info(self, role):
        queue_number = None
        activity = None

        if role == 'd':
            queue_number = 0
            activity = ActivityStrings.delivery_str
        elif role == 'm':
            queue_number = 1
            activity = ActivityStrings.moonshine_str
        elif role == 'b':
            queue_number = 2
            activity = ActivityStrings.bounty_str
        elif role == 'n':
            queue_number = 3
            activity = ActivityStrings.nature_str
        elif role == 'p':
            queue_number = 4
            activity = ActivityStrings.posse_str

        return queue_number, activity

aqo = AllQueueObjects()
