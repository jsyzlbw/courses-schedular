# Class Scheduler Project

This project is designed to help students plan their course schedule efficiently by filtering out conflicting course sections and providing valid course combinations. The project consists of several Python scripts that work together to load course data, process user preferences, and retrieve course sections from the CUHK SIS website.   
The project havent be completed, the sis_client.py and parser.py are to be completed.   

## Project Structure

## 1. `main.py` - Main Program

The main program serves as the entry point of the project. It performs the following tasks:

- **Loads User Preferences**: Reads the course choices data (`course_choices.json`) to get the student's course preferences (e.g., avoiding 8:30 AM classes, avoiding Friday classes).
- **Loads Course Section Data**: Reads the course section data (`course_sections_data.json`), which contains available course sections and their respective professors and meeting times.
- **Calls the Scheduler**: Uses the data to call the `schedular.py` to find all non-conflicting schedules based on the student’s preferences.
- **Displays Results**: Outputs the valid schedules for the student to choose from.

### Example Usage:
1. Load data from `course_choices.json` and `course_sections_data.json`.
2. Call the scheduling function to filter non-conflicting schedules.
3. Print out all the possible valid schedules.

## 2. `schedular.py` - Non-Conflicting Schedule Filter

The `schedular.py` script contains the logic for filtering out conflicting course schedules based on the student’s preferences.

- **Input**: 
  - `course_data`: Contains a dictionary of available course sections with meeting times.
  - `course_choice`: Contains the courses the student has chosen, along with the preferred professors (or `"prof"` for any professor).
  - `morning_eight_avoid`: A flag to avoid courses that start at 8:30 AM.
  - `friday_avoid`: A flag to avoid any courses scheduled on Fridays.
  
- **Output**: 
  - A list of valid, non-conflicting schedules.

### Key Components:
- **`Meeting` class**: Represents a meeting for a course section, including the day, start time, and end time.
- **`Section` class**: Represents a course section, including the professor and the list of `Meeting` objects.
- **`find_non_conflicting_schedules` function**: This function finds and returns all possible schedules that do not conflict in time.

## 3. `sis_client.py` - Fetch HTML from CUHK SIS (To Be Implemented)

The `sis_client.py` script is responsible for connecting to CUHK's SIS (Student Information System) at `sis.cuhk.edu.cn`. It will fetch the HTML page containing course schedule information.

- **Functionality**:
  - The script will use web scraping techniques (e.g., using the `requests` and `BeautifulSoup` libraries) to send a request to the SIS website and retrieve the HTML content.
  - The script will authenticate and handle any login procedure.

- **Next Steps**:
  - Implement the script to send a request to SIS and fetch the HTML of the course schedule page.

## 4. `parser.py` - Parse HTML and Extract Course Information (To Be Implemented)

The `parser.py` script is responsible for parsing the HTML data fetched from CUHK's SIS and extracting the course section information.

- **Functionality**:
  - It will extract course details such as:
    - Course code
    - Professor
    - Meeting days and times
  - The extracted data will be saved in the `course_sections_data.json` file.

- **Next Steps**:
  - Implement the parsing logic to extract the relevant course data from the HTML.
  - Write the parsed data into `course_sections_data.json` in the appropriate format.

### Expected Flow:
1. `sis_client.py` fetches the HTML from SIS.
2. `parser.py` parses the HTML and extracts the course data.
3. The course data is saved in `course_sections_data.json`, which is then used by `main.py` to filter non-conflicting schedules.

## Data Files

### `course_choices.json`

This file stores the student’s course choices and preferences. It includes:

- **`student_id`**: The student's ID.
- **`password`**: The student's password for authentication (if needed).
- **`morning_eight_avoid`**: A boolean flag to avoid courses that start at 8:30 AM.
- **`friday_avoid`**: A boolean flag to avoid courses on Fridays.
- **`courses`**: A list of the student’s chosen courses, each containing the course code and the preferred professor (or `"prof"` for any professor).

Example format:
```json
{
    "student_id": "123456",
    "password": "securepassword",
    "morning_eight_avoid": true,
    "friday_avoid": false,
    "courses": [
        { "code": "CSC1001", "teacher": "Tom Anderson" },
        { "code": "MAT1011", "teacher": "prof" }
    ]
}    
```

### `course_sections_data.json`
Example format:
```json
{
    "CSC1001": [
        ["Tom Anderson", ["Mon", "8:30", "10:20"], ["Wed", "13:30", "14:50"]],
        ["Judy Trump", ["Tue", "8:30", "10:20"], ["Thu", "13:30", "14:50"]]
    ],
    "MAT1011": [
        ["Joe Tompson", ["Mon", "10:30", "11:50"], ["Wed", "10:30", "11:50"], ["Thu", "10:30", "12:20"]],
        ["John Doe", ["Mon", "14:00", "15:20"], ["Thu", "14:00", "15:20"]]
    ]
}
```
