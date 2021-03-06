from todoist_tools import api_wrapper, habit_tracker, hygiene
import argparse

#########################################
# Set up and run the argument parser
#########################################
parser = argparse.ArgumentParser(description='Choose Todoist task to run')
parser.add_argument('--start_of_day_checklist', action='store_true')
parser.add_argument('--end_of_day_checklist', action='store_true')
parser.add_argument('--weekly_review_checklist', action='store_true')
parser.add_argument('--update_habits', action='store_true')
parser.add_argument('--run_daily_hygienist', action='store_true')
parser.add_argument('--run_hourly_hygienist', action='store_true')

args = parser.parse_args()

#########################################
# Connect to Todoist and make updates
#########################################
api = api_wrapper.ApiWrapper()
habits = habit_tracker.HabitTracker(api)
hygienist = hygiene.Hygienist(api)

# Start of day checklist
if args.start_of_day_checklist:
    api.copy_project_contents_to_inbox('Start-of-Day Checklist')

# End of day checklist
if args.end_of_day_checklist:
    api.copy_project_contents_to_inbox('End-of-Day Checklist')

# Weekly review checklist
if args.weekly_review_checklist:
    api.copy_project_contents_to_inbox('Weekly Review Checklist')

# Update habits
if args.update_habits:
    habits.update_habits()

# Run daily hygienist
if args.run_daily_hygienist:
    hygienist.run_daily_hygienist()

# Run hourly hygienist
if args.run_hourly_hygienist:
    hygienist.run_hourly_hygienist()

#########################################
# Commit all changes at once
#########################################
api.commit()

