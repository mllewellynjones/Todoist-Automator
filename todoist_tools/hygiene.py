from datetime import datetime

class Hygienist():
    """Performs periodic hygiene to keep system in a good state"""

    def __init__(self, api_wrapper):
        """Initialise the habit tracker with an API connection"""

        self.api_wrapper = api_wrapper

    def run_hygienist(self):
        """Runs all periodic hygiene tasks"""
        self.remove_priorities_from_all_not_due_today()


    def remove_priorities_from_all_not_due_today(self):
        """Priorities can be accidentally assigned to tasks not due today, e.g. if the task is recurring. This
        removes all those priorities"""

        today = datetime.now().date()

        for item in self.api_wrapper.get_all_items():

            try:
                item_due_date = datetime.strptime(item['due']['date'], "%Y-%m-%d").date()
                if item['priority'] != 1 and item_due_date != today:
                    item.update(priority=1)

            except TypeError:
                continue


