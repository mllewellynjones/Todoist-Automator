import re
from datetime import datetime

TIMEBOX_TRACKER_RE = re.compile('(?P<tbtracker>\[TBS \d+/\d+\])(?P<Description>.*)')

class Hygienist():
    """Performs periodic hygiene to keep system in a good state"""

    def __init__(self, api_wrapper):
        """Initialise the habit tracker with an API connection"""

        self.api_wrapper = api_wrapper

    def run_daily_hygienist(self):
        """Runs all hygiene tasks that can be run frequently to keep Todoist in shape"""
        self.remove_priorities_from_all_not_due_today()

    def run_hourly_hygienist(self):
        """Runs all hygiene tasks that should only be run once in the early hours of the morning"""
        self.ensure_timebox_trackers_accurate()

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

    def ensure_timebox_trackers_accurate(self):
        """Updates the timebox trackers for every task based on how many timebox subtasks have been completed"""

        for item in self.api_wrapper.get_all_items():

            if item['content'].startswith('[TBS'):
                total_timeboxes = 0
                completed_timeboxes = 0

                master_id = item['id']

                # Feels inefficient to loop through everything again
                for sub_item in self.api_wrapper.get_all_items():
                    if sub_item['parent_id'] == master_id:
                        total_timeboxes += 1

                        if sub_item['checked'] == 1:
                            completed_timeboxes += 1

                timebox_tracker_match = TIMEBOX_TRACKER_RE.search(item['content'])

                if timebox_tracker_match:
                    new_content = ('[TBS {}/{}]'.format(completed_timeboxes, total_timeboxes)
                                   + timebox_tracker_match.group('Description'))
                    item.update(content=new_content)

                # Collapse the item regardless of initial state
                item.update(collapsed=1)
