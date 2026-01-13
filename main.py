import schedular
import os
import json

# Function to load course data and course choice data from JSON files
def load_data():
    course_choice_file = './data/course_choices_data.json'
    course_sections_file = './data/course_sections.json'

    # Read the course choice data
    if os.path.exists(course_choice_file):
        with open(course_choice_file, 'r') as file:
            course_choice_data = json.load(file)
    else:
        print(f"Error: {course_choice_file} does not exist.")
        return None, None

    # Read the course section data
    if os.path.exists(course_sections_file):
        with open(course_sections_file, 'r') as file:
            course_sections_data = json.load(file)
    else:
        print(f"Error: {course_sections_file} does not exist.")
        return None, None

    return course_sections_data, course_choice_data

# Function to process course choices and extract relevant information
def process_courses(course_choice_data):
    course_choice = {}
    for course in course_choice_data['courses']:
        course_choice[course['code']] = course['teacher']  # Map course code to teacher (or 'prof')
    return course_choice

# Function to print the valid schedules to the user
def print_schedule(schedules):
    if not schedules:
        print("No valid schedules found.")
        return

    print(f"Found {len(schedules)} possible schedule(s):\n")

    # Loop through each valid schedule and print its details
    for idx, schedule in enumerate(schedules, 1):
        print(f"\nSchedule #{idx}")
        for row in schedule["compact"]:
            day, start, end, course_code, professor = row
            print(f"  {day} {start}-{end}  {course_code} ({professor})")

def main():
    # Load course data and course choice data
    course_data, course_choice_data = load_data()

    if not course_data or not course_choice_data:
        print("Exiting program due to missing data.")
        return

    # Process course_choice_data to create a proper course_choice dictionary
    course_choice = process_courses(course_choice_data)

    # Get the user's preferences for scheduling (like avoiding early morning or Friday classes)
    morning_eight_avoid = course_choice_data.get("morning_eight_avoid", False)
    friday_avoid = course_choice_data.get("friday_avoid", False)

    # Call the scheduler function to get all non-conflicting schedules
    schedules = schedular.find_non_conflicting_schedules(
        course_data=course_data,
        course_choice=course_choice,
        morning_eight_avoid=morning_eight_avoid,
        friday_avoid=friday_avoid,
    )

    # Print the possible valid schedules to the user
    print_schedule(schedules)


if __name__ == "__main__":
    main()
