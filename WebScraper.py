# Nelson Ha Web Scraper for GSU

from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import re

# Initialize the Chrome WebDriver
driver = webdriver.Chrome()

# Maximize the window - IMPORTANT
driver.maximize_window()

# Open the webpage
url = ''  # Replace with the actual URL
driver.get(url)

# Wait for 10 seconds for the page to load
# This also lets the user manually change to the semester they want
wait = WebDriverWait(driver, 10)

# Locate the input element
'''
#Need to work on this, Not finished so have to click Fall Semester 2024 manually

input_element = driver.find_element(By.ID, 's2id_autogen1')

# Click the input element to focus on it
input_element.click()

# Send the Enter key to select the most recent item
input_element.send_keys(Keys.ENTER)

time.sleep(3)

# Locate the "Continue" button by ID
continue_button = driver.find_element(By.ID, 'term-go')

# Click the "Continue" button
continue_button.click()

time.sleep(3)

'''

# Wait for the dropdown to be clickable and select the 'Associates' option
level_dropdown = wait.until(EC.element_to_be_clickable((By.ID, 'txt_level')))
level_dropdown.click()
#associates_option = driver.find_element(By.XPATH, "//option[@value='UA']")
#associates_option.click()
#bachelor_option = driver.find_element(By.XPATH, "//option[@value='US']")
#bachelor_option.click()
#graduate_option = driver.find_element(By.XPATH, "//option[@value='GS']")
#graduate_option.click()
law_option = driver.find_element(By.XPATH, "//option[@value='LW']")
law_option.click()

# Wait for 5 seconds before setting the subject value
time.sleep(5)

# Sets the value of the subject input field to all the subjects
js_script = 'document.getElementById("txt_subject").value = "ACCT,ACT,AS,AAS,ASL,MSA,ANTH,APDB,APBS,APCE,APCL,APCP,APCD,APEU,APFL,APGT,APHP,APHC,APHN,APJB,APJG,AL,APOB,APOR,APPR,APPF,APJP,APTB,APSX,APTP,APTU,APVA,APVL,APVC,ARBC,ART,AE,BIOL,AH,ASTR,BRFV,BMSC,BA,BCOM,BUSA,CPI,CER,CHEM,CHIN,CNHP,COMM,CSD,CIS,CSC,COOP,CPS,CMIS,CRJU,EDCI,DSCI,DFST,DHYG,DBA,DP,DPP,ECE,ECON,EDUC,EPS,EPY,ENGR,ENGL,ESL,ENI,ENVS,EPEL,EPHE,EPRS,EPSF,EURO,EXC,EMBA,FLME,FTA,FI,FOLK,FORL,FREN,GEOG,GEOL,GFA,GEOS,GRMN,GERO,GLOS,GRAD,GRD,GSU,HA,HI,HS,HIST,HON,HADM,HUMN,IFI,ISCI,IEP,INDS,ID,IB,INEX,ITAL,JAPN,JOUR,KH,KORE,EDLA,LAW,LT,LGLS,MGT,MK,MBA,MATH,EDMT,MSL,MUS,MUA,MTM,NSCI,NEUR,NURS,NUTR,OT,PERS,PHIL,PHOT,PT,PHYS,POLS,PORT,PRT,PRLB,PSYC,PHPB,PHPH,PMAP,QRAM,EDRD,RE,RELS,RSCH,RT,RMI,RUSS,EDSC,SCUL,SLIP,EDSS,SW,SOCI,SPAN,SCOM,STAT,STEM,SWAH,TX,TSLE,TEXT,THEA,3DS,URB,WGSS,WLC";'
#js_script = 'document.getElementById("txt_subject").value = "ACCT";' #for Testing
#js_script = 'document.getElementById("txt_subject").value = "BIOL";' #for testing the 2 extra labs
#js_script = 'document.getElementById("txt_subject").value = "BUSA";' #for testing the stability check
driver.execute_script(js_script)

# Click the search button
search_button = driver.find_element(By.ID, 'search-go')
search_button.click()

time.sleep(5)

# Rather than viewing only 10 per page, selects 50 per page to be faster
wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'page-size-select')))
page_size_dropdown = driver.find_element(By.CLASS_NAME, 'page-size-select')
for option in page_size_dropdown.find_elements(By.TAG_NAME, 'option'):
    if option.text == '50':
        option.click()
        break

# Give time for results to load
time.sleep(10)

# Some classes have multiple information
classes = []


# Function to scrape data from the current page
def scrape_current_page():
    rows = driver.find_elements(By.XPATH, "//tr[@data-id]")
    for row in rows:
        campus = row.find_element(By.XPATH, ".//td[@data-property='campus']").text.strip()
        #print("campus success")
        class_id = row.find_element(By.XPATH, ".//td[@data-property='courseReferenceNumber']").text.strip()
        #print("class id success")
        subject = row.find_element(By.XPATH, ".//td[@data-property='subject']").text.strip()
        #print("subject success")
        course_number = row.find_element(By.XPATH, ".//td[@data-property='courseNumber']").text.strip()
        #print("course number success")
        hours = row.find_element(By.XPATH, ".//td[@data-property='creditHours']").text.strip()
        #print("hours success")
        instructor = row.find_element(By.XPATH, ".//td[@data-property='instructor']").text.strip()
        #print("instructor success")
        meeting_days = row.find_element(By.XPATH, ".//div[contains(@class, 'ui-pillbox-summary')]").text.strip()
        #print("meeting days success")
        meeting_time = row.find_element(By.XPATH, ".//td[@data-property='meetingTime']").get_attribute("title")
        #print("meeting time success")

        # Remove unnecessary items in title
        title_element = row.find_element(By.XPATH, ".//td[@data-property='courseTitle']")
        title_text = title_element.text.strip()
        terms_to_remove = [
            'Lecture', 'Supervised Laboratory', 'Large Classroom/', 'Internship/Practicum',
            'Independent Study (Correspond)', 'Seminar', '/', 'Directed Study (one-to-one)', '/Unsupervised Lab',
            'Dissertation', 'Thesis', 'Unsupervised Lab'
        ]
        for term in terms_to_remove:
            title_text = title_text.replace(term, '')

        title = title_text.strip()
        #print("title success")

        # Extract class type(s) example: asynch or face to face
        instruction_type_tags = row.find_elements(By.XPATH, ".//img")
        class_types = []

        # Use the image source to determine
        for tag in instruction_type_tags:
            src = tag.get_attribute('src')
            if 'face-to-face.png' in src:
                class_types.append('Face to Face')
            elif 'lonl_icon.png' in src:
                class_types.append('Online Asynchronous')
            elif 'sonl_icon.png' in src:
                class_types.append('Online Synchronous')
            elif 'hybrid.png' in src:
                class_types.append('Hybrid')
            elif 'low-cost.png' in src:
                class_types.append('Low Cost')
            elif 'no-cost.png' in src:
                class_types.append('No Cost')
            elif 'bnch_icon.png' in src:
                class_types.append('Learning Community Bench')
            elif 'lc_icon.png' in src:
                class_types.append('Learning Community Block')

        class_type = ', '.join(class_types) if class_types else 'Other'  # Combines if there are multiple
        #print("class type success")

        #This is for if we need to check if a class has over 3 meetings/labs somehow. (Idk how we do..)
        stable = ""
        count = meeting_time.count("SMTWTFS")
        if (count > 3):
            stable = "Unstable"
        else:
            stable = "Stable"
        #print("stable success")

        if "(Primary)" in instructor and instructor.count(',') > 1:
            #print("yes")
            # This is to fix the primary instructor part
            instructor_no_periods = re.sub(r'\.', '', instructor)
            cleaned_instructor = re.sub(r'\b(?!\bO\b)[a-zA-Z]\b', '', instructor_no_periods).strip()

            #print(cleaned_instructor)

            # Use regex to split by commas and spaces, but keep parts with parentheses intact
            instructor_parts = re.findall(r'[^,\s()]+(?:,[^,\s()]+)?|\([^)]+\)', cleaned_instructor)

            #print(instructor_parts)
            # Join parts with commas

            cleaned_instructor_parts = [part for part in instructor_parts if len(part) > 1]

            #print(cleaned_instructor_parts)
            formatted_instructor = ', '.join([part.strip() for part in cleaned_instructor_parts])

            # print("Formatted Instructor:", formatted_instructor)

            # Split by commas outside of parentheses
            instructor_parts = re.findall(r'[^,\s()]+(?:,[^,\s()]+)?|\([^)]+\)', formatted_instructor)
            # print(instructor_parts)
            primaryindex = instructor_parts.index('(Primary)')
            first = 0
            second = 0
            first = primaryindex - 2
            second = primaryindex - 1
            # print(instructor_parts[first], instructor_parts[second])
            primary_instructor = instructor_parts[first] + ", " + instructor_parts[second]
            # print(primary_instructor)
            # print(instructor_parts)
            instructor_parts.pop(primaryindex)
            instructor_parts.pop(second)
            instructor_parts.pop(first)
            # print(instructor_parts)
            other_instructors = ", ".join(instructor_parts)
            # print("Other Instructors:", other_instructors)
            if (other_instructors == ""):
                other_instructors = "N/A"
        else:
            if (instructor != ""):
                instructor_no_periods = re.sub(r'\.', '', instructor)
                cleaned_instructor = re.sub(r'\b(?!\bO\b)[a-zA-Z]\b', '', instructor_no_periods).strip()
                cleaned_instructor = re.sub(r'\b\w\b(?!\')', '', instructor_no_periods).strip()
                #print(f"Cleaned: {cleaned_instructor}")
                cleaned_instructor = cleaned_instructor.replace(" (Primary)", "")
                primary_instructor = cleaned_instructor
            else:
                primary_instructor = instructor
            other_instructors = "N/A"

        if (primary_instructor == ""):
            primary_instructor = "N/A"

        #print("instructors success")

        building = ""
        room = ""
        lab_day = ""
        lab_time = ""
        lab_building = ""
        lab_starting = ""
        extra_time = "N/A"
        extra_building = "N/A"
        extra_room = "N/A"
        converted_extralab_range = "N/A"
        extra_starting = "N/A"
        extra_ending = "N/A"
        extra_day = "N/A"
        if 'Building: ' in meeting_time:
            building = meeting_time.split('Building: ')[1].split(' Room: ')[0].strip()
        #print("building success")
        if 'Room: ' in meeting_time:
            room = meeting_time.split('Room: ')[1].split('<')[0].strip()

            # If room is empty, set it to "None"
            if not room:
                room = "None"

            # Check for days in the room text
            days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
            for day in days_of_week:
                if day in room:
                    lab_day = day
                    break

            # Extract lab time from room text
            match_am = re.search(r'.{0,7}(AM).{0,12}', room)
            match_pm = re.search(r'.{0,7}(PM).{0,12}', room)
            if match_am and (not match_pm or match_am.start() < match_pm.start()):
                lab_time = room[match_am.start() - 7: match_am.end() + 12].strip()
            elif match_pm:
                lab_time = room[match_pm.start() - 7: match_pm.end() + 12].strip()
            else:
                lab_time = "N/A"
                lab_day = "N/A"

            # Clean up lab_time
            lab_time = re.sub(r'SMTWTFS', '', lab_time).strip()
            lab_time = re.sub(r'Type:.*', '', lab_time).strip()

            # Extract lab building from room text
            if 'Building: ' in room:
                lab_building = room.split('Building: ')[1].strip().split(' ')[0]

            lab_split = re.findall(r'\d+:\d+', lab_time)
            if len(lab_split) >= 2:
                lab_starting = lab_split[0].strip()
                lab_ending = lab_split[1].strip()
            else:
                lab_starting = "N/A"
                lab_ending = "N/A"
                lab_building = "N/A"

        #print("lab and normal room success")

        # Extract Days and Time from meeting_time
        days = ""
        time_range = ""
        if 'Start Date: ' in meeting_time:
            start_date_split = meeting_time.split('Start Date: ')[1]
            end_date_split = start_date_split.split(' End Date: ')
            days_split = end_date_split[1].split('SMTWTFS')[0].strip()
            time_split = end_date_split[1].split('SMTWTFS')[1].strip().split(" Type:")[0].strip()

            # Remove all digits and '/' characters from the days string
            days = re.sub(r'\d+|/', '', days_split)
            time_range = time_split

        if time_range == "TBA":
            starting_time = "TBA"
            ending_time = "TBA"
        else:
            # Split the time string into starting and ending time
            time_split = re.findall(r'\d+:\d+', time_range)
            if len(time_split) >= 2:
                starting_time = time_split[0].strip()
                ending_time = time_split[1].strip()
            else:
                starting_time = "N/A"
                ending_time = "N/A"

        #print("days and time success")

        # If the class is Asynch, don't need time ranges or starting time/ending time
        if 'Online Asynchronous' in class_types:
            time_range = "N/A"
            starting_time = "N/A"
            ending_time = "N/A"

        def extract_lab_building(meeting_time):
            # Find all occurrences of "Class Building:"
            occurrences = [m.start() for m in re.finditer('Class Building:', meeting_time)]

            if len(occurrences) >= 2:
                # Extract substring starting from the second occurrence
                start_index = occurrences[1] + len('Class Building:')
                substring = meeting_time[start_index:]

                # Find where "Room:" or "R" occurs
                end_index = re.search(r'Room:|R', substring)

                if end_index:
                    lab_building = substring[:end_index.start()].strip()
                    return lab_building

            return "N/A"

        lab_building = extract_lab_building(meeting_time)

        #print("lab building success")

        def extract_lab_room(meeting_time):
            # Find all occurrences of "Room:"
            occurrences = [m.start() for m in re.finditer('Room:', meeting_time)]

            if len(occurrences) >= 2:
                # Extract substring starting from the second occurrence of "Room:"
                start_index = occurrences[1] + len('Room:')

                # Check if there's a "Start Date:" before the next occurrence
                next_start_date = meeting_time.find("Start Date:", start_index)
                if next_start_date != -1:
                    substring = meeting_time[start_index:next_start_date].strip()
                else:
                    # If "Start Date:" is not found, take the substring till the end
                    substring = meeting_time[start_index:].strip()

                # Remove any non-alphanumeric characters from the end
                lab_room = re.sub(r'[^\w\s]', '', substring.split()[0].strip())

                return lab_room

            return "N/A"

        lab_room = extract_lab_room(meeting_time)

        #print("lab room success")

        # method to convert
        def convert_to_24hr(time_str):
            return datetime.strptime(time_str, '%I:%M %p').strftime('%H:%M')

        time_range_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))', time_range)
        if time_range_match:
            starting_time = convert_to_24hr(time_range_match.group(1))
            ending_time = convert_to_24hr(time_range_match.group(2))

        time_range = f"{starting_time} - {ending_time}"

        lab_range_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))', lab_time)
        if lab_range_match:
            lab_starting = convert_to_24hr(lab_range_match.group(1))
            lab_ending = convert_to_24hr(lab_range_match.group(2))

        lab_time = f"{lab_starting} - {lab_ending}"

        check = meeting_time.count("SMTWTFS")

        if (check > 2):
            # Function to extract the substring after the second occurrence of "SMTWTFS"
            def remove_before_second_smtwtfs(meeting_time):
                parts = meeting_time.split("SMTWTFS", 2)
                if len(parts) > 2:
                    return "SMTWTFS".join(parts[2:])
                else:
                    return meeting_time

            # Function to extract the last day from the substring
            def extract_last_day_from_substring(substring):
                days_pattern = r"Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday"
                found_days = re.findall(days_pattern, substring)
                if found_days:
                    return found_days[-1]
                else:
                    return "N/A"

            # Remove everything before the second occurrence of "SMTWTFS"
            substring_after_second_smtwtfs = remove_before_second_smtwtfs(meeting_time)

            # Extract the last day from the resulting substring
            extra_day = extract_last_day_from_substring(substring_after_second_smtwtfs)

            def extract_extra_info(meeting_time):
                # Split the string by "SMTWTFS" occurrences
                splits = re.split(r'SMTWTFS', meeting_time, flags=re.IGNORECASE)

                # Check if there are at least 3 occurrences of "SMTWTFS"
                if len(splits) >= 4:
                    # Join everything after the third occurrence of "SMTWTFS"
                    extra_info = ' '.join(splits[3:]).strip()
                    return extra_info
                else:
                    return "N/A"

            extra_info = extract_extra_info(meeting_time)

            # print(f"Extra Info: {extra_info}")

            def extract_details(extra_info):
                # Extract extra_time using regular expressions
                extra_time_match = re.search(r'\d{2}:\d{2}\s*[APM]{2}\s*-\s*\d{2}:\d{2}\s*[APM]{2}', extra_info)
                extra_time = extra_time_match.group(0) if extra_time_match else "N/A"

                # Extract extra_building using regular expressions
                extra_building_match = re.search(r'Building:\s*(.*?)\s*Room:', extra_info)
                extra_building = extra_building_match.group(1).strip() if extra_building_match else "N/A"

                # Extract extra_room using regular expressions
                extra_room_match = re.search(r'Room:\s*(\d+)', extra_info)
                extra_room = extra_room_match.group(1).strip() if extra_room_match else "N/A"

                return extra_time, extra_building, extra_room

            # Extract details from extra_info
            extra_time, extra_building, extra_room = extract_details(extra_info)
            # print(f"Extra Time: {extra_time}")
            # print(f"Extra Building: {extra_building}")
            # print(f"Extra Room: {extra_room}")

            extra_range_match = re.search(r'(\d{1,2}:\d{2}\s*(?:AM|PM))\s*-\s*(\d{1,2}:\d{2}\s*(?:AM|PM))', extra_time)
            if extra_range_match:
                extra_starting = convert_to_24hr(extra_range_match.group(1))
                extra_ending = convert_to_24hr(extra_range_match.group(2))
            else:
                extra_starting = 'N/A'
                extra_ending = 'N/A'

            converted_extralab_range = f"{extra_starting} - {extra_ending}"

            # print(f"Extra Lab Starting Time: {converted_extralab_range}")
            # print(f"Extra Lab Starting Time: {extra_starting}")
            # print(f"Extra Lab Ending Time: {extra_ending}")

        room = re.split(r'S', room, maxsplit=1)[0].strip()

        # Print the extracted data for debugging
        print("Class ID:", class_id)
        print("Subject:", subject)
        print("Course Number:", course_number)
        print("Hours:", hours)
        print("Title:", title)
        print("Primary Instructor:", primary_instructor)
        print("Other Instructor:", other_instructors)
        print("Meeting Days:", meeting_days)
        print("Building:", building)
        print("Room:", room)
        print("Campus:", campus)
        print("Meeting Time:", meeting_time)
        print("Days:", days)
        print("Time:", time_range)
        print("Starting Time:", starting_time)
        print("Ending Time:", ending_time)
        print("Class Type:", class_type)
        print("Lab Day:", lab_day)
        print("Lab Time:", lab_time)
        print("Lab Building:", lab_building)
        print("Lab Room:", lab_room)
        print("Lab Starting Time:", lab_starting)
        print("Lab Ending Time:", lab_ending)
        print("Extra Lab Day:", extra_day)
        print("Extra Lab Time:", converted_extralab_range)
        print("Extra Lab Building:", extra_building)
        print("Extra Lab Room:", extra_room)
        print("Extra Lab Starting Time:", extra_starting)
        print("Extra Lab Ending Time:", extra_ending)
        print("Stability:", stable)
        print()

        # Append the data as a dictionary to the classes list
        classes.append({
            'ID': class_id,
            'Subject': subject,
            'Course Number': course_number,
            'Hours': hours,
            'Title': title,
            'Primary Instructor': primary_instructor,
            'Other Instructor': other_instructors,
            'Building': building,
            'Room': room,
            'Campus': campus,
            'Days': days,
            'Time': time_range,
            'Starting Time': starting_time,
            'Ending Time': ending_time,
            'Class Type': class_type,
            'Lab Day': lab_day,
            'Lab Time': lab_time,
            'Lab Building': lab_building,
            'Lab Room': lab_room,
            'Lab Starting Time': lab_starting,
            'Lab Ending Time': lab_ending,
            'Extra Lab Day': extra_day,
            'Extra Lab Time': converted_extralab_range,
            'Extra Lab Building': extra_building,
            'Extra Lab Room': extra_room,
            'Extra Lab Starting Time': extra_starting,
            'Extra Lab Ending Time': extra_ending,
            'Stability': stable
        })


# Scrape the first page
scrape_current_page()

# Get the total number of pages
total_pages = int(driver.find_element(By.XPATH, "//span[@class='paging-text total-pages']").text.strip())
print("Total Pages:", total_pages)

# Loop through all pages and scrape data
for page in range(2, total_pages + 1):
    try:
        # Give time for data to fully load for each page and then click Next
        time.sleep(6)
        next_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Next' and contains(@class, 'enabled')]")))
        next_button.click()

        # Wait for data to load again
        time.sleep(6)

        # Scrape data from the current page
        scrape_current_page()

    # Error handler in case the scrape fails, we can tell which page it was
    except Exception as e:
        print(f"Error on page {page}: {e}")
        break

# Create a pandas dataframe from the list of dictionaries
df = pd.DataFrame(classes)

# Specify the path where the CSV file will be saved
output_path = 'classes.csv'

# Export the dataframe to a CSV file
df.to_csv(output_path, index=False)

print(f'Data has been successfully scraped and saved to {output_path}')

# Close the browser
driver.quit()
