import requests
import json

# Moodle configurations
MOODLE_URL = "https://your-moodle-site.com"
TOKEN = "your-webservice-token"
ENDPOINT = f"{MOODLE_URL}/webservice/rest/server.php"

# Function to create a course
def create_course(category_id, course_name, course_idnumber, scorm_format="singleactivity"):
    """
    Create a Moodle course with a single activity format.
    :param category_id: ID of the category where the course will be created.
    :param course_name: Name of the course to be created.
    :param course_idnumber: Unique identifier for the course.
    :param scorm_format: Format of the course (default: "singleactivity").
    :return: Course ID of the created course.
    """
    payload = {
        'wstoken': TOKEN,
        'moodlewsrestformat': 'json',
        'wsfunction': 'core_course_create_courses',
        'courses[0][fullname]': course_name,
        'courses[0][shortname]': course_name,
        'courses[0][categoryid]': category_id,
        'courses[0][idnumber]': course_idnumber,
        'courses[0][format]': scorm_format
    }

    response = requests.post(ENDPOINT, data=payload)
    response_data = response.json()
    
    if response.status_code == 200 and isinstance(response_data, list):
        course_id = response_data[0]['id']
        print(f"Course '{course_name}' created successfully with ID {course_id}.")
        return course_id
    else:
        print(f"Error creating course: {response_data}")
        raise Exception("Course creation failed.")

# Function to upload a SCORM package to a course
def upload_scorm_package(course_id, scorm_file_path):
    """
    Upload a SCORM package to the specified course.
    :param course_id: ID of the course to upload the SCORM package to.
    :param scorm_file_path: Path to the SCORM package file.
    """
    # Upload the SCORM file
    upload_url = f"{ENDPOINT}?wstoken={TOKEN}&moodlewsrestformat=json&wsfunction=core_files_upload"
    files = {'file': open(scorm_file_path, 'rb')}
    upload_response = requests.post(upload_url, files=files)
    upload_data = upload_response.json()

    if upload_response.status_code == 200 and 'itemid' in upload_data:
        itemid = upload_data['itemid']
        print(f"SCORM package uploaded successfully with item ID {itemid}.")
    else:
        print(f"Error uploading SCORM package: {upload_data}")
        raise Exception("SCORM package upload failed.")

    # Add the SCORM package to the course
    scorm_payload = {
        'wstoken': TOKEN,
        'moodlewsrestformat': 'json',
        'wsfunction': 'mod_scorm_add_scorm',
        'courseid': course_id,
        'name': 'SCORM Package',
        'intro': 'Uploaded SCORM package',
        'files[0][itemid]': itemid
    }
    scorm_response = requests.post(ENDPOINT, data=scorm_payload)
    scorm_data = scorm_response.json()

    if scorm_response.status_code == 200 and 'id' in scorm_data:
        print(f"SCORM package added successfully to course ID {course_id}.")
    else:
        print(f"Error adding SCORM package: {scorm_data}")
        raise Exception("Adding SCORM package to course failed.")

# Main execution flow
if __name__ == "__main__":
    try:
        # Specify your details here
        category_id = 1  # Replace with your category ID
        course_name = "Sample SCORM Course"
        course_idnumber = "SCORM_001"
        scorm_file_path = "/path/to/your/scorm/package.zip"

        # Create the course
        course_id = create_course(category_id, course_name, course_idnumber)

        # Upload the SCORM package
        upload_scorm_package(course_id, scorm_file_path)

    except Exception as e:
        print(f"Error: {e}")
