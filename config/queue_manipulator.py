


class QueueManipulator:
    def add_to_queue(self, list_of_members_dict, member_id, member_display_name):
        list_of_members_dict.append({member_id: member_display_name})



qm = QueueManipulator()