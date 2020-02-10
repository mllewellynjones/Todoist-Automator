from datetime import datetime
import re

HABIT_RE = re.compile("\[(?P<counter>\d+)\](?P<text>.*)")

class HabitTracker():
    """Monitors and updates habits maintained in Todoist"""

    def __init__(self, api_wrapper):
        """Initialise the habit tracker with an API connection"""

        self.api_wrapper = api_wrapper

    def get_habits_list(self):
        """Returns a list of all habits in the habit project"""

        return self.api_wrapper.get_root_items_in_project('HABITS')
           
    def update_habits(self):
        """Updates all habits by:

        1) Resetting counters on all overdue habits and mark them as complete
        2) Incrementing the counters on all habits due yesterday that are
        not overdue

        This routine should be right at the end of the day, so tht uncompleted
        habits can be marked as complete to move them to tomorrow
        """
    
        habit_list = self.get_habits_list()
        for habit in habit_list:
            if self.habit_is_overdue(habit):
                # It's the end of the day and the habit was due today (or earlier)
                # - reset the counter
                self.reset_habit_counter(habit)
            elif self.habit_due_today(habit):
                # The habit was due today and is not overdue, it must have been
                # completed - increment counter
                self.increment_habit_counter(habit)

        return None


    def habit_is_overdue(self, habit):
        """Checks if a habit is overdue, returning True if so and false otherwise"""

        today = datetime.now().date()
        habit_due_date = datetime.strptime(habit['due']['date'], "%Y-%m-%d").date()

        if habit_due_date <= today:
            return True
        else:
            return False


    def habit_due_today(self, habit):
        """Determines if the habit should have been due today (based on recurrence)"""

        day_today = datetime.strftime(datetime.now(), '%A').lower()
        workdays = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']

        if habit['due']['string'] == 'every day':
            return True
        elif habit['due']['string'] == 'every workday' and day_today in workdays:
            return True
        elif day_today in habit['due']['string']:
            return True
        else:
            return False


    def reset_habit_counter(self, habit):
        """Returns the numeric habit counter to zero, assuming contents of the form:
            
        [COUNTER] Habit name
        """

        habit_format_match = HABIT_RE.search(habit['content'])

        if habit_format_match:
            new_habit_content = '[0]' + habit_format_match.group('text')
            habit.update(content=new_habit_content)
            habit.close()

        return None


    def increment_habit_counter(self, habit):
        """Increments the habit counter by 1 for the given habit"""

        habit_format_match = HABIT_RE.search(habit['content'])

        if habit_format_match:
            habit_counter = int(habit_format_match.group('counter'))
            new_habit_content = ('[' + str(habit_counter+1) + ']'
                                 + habit_format_match.group('text')
                                )
            habit.update(content=new_habit_content)
