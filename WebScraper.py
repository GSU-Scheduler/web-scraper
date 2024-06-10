#Nelson Ha Web Scraper for GSU

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
# Can currently only do one level at a time (associates, bachelor, graduate, law)
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
driver.execute_script(js_script)

# Click the search button
search_button = driver.find_element(By.ID, 'search-go')
search_button.click()

time.sleep(3)

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
        class_id = row.find_element(By.XPATH, ".//td[@data-property='courseReferenceNumber']").text.strip()
        subject = row.find_element(By.XPATH, ".//td[@data-property='subject']").text.strip()
        course_number = row.find_element(By.XPATH, ".//td[@data-property='courseNumber']").text.strip()
        hours = row.find_element(By.XPATH, ".//td[@data-property='creditHours']").text.strip()
        instructor = row.find_element(By.XPATH, ".//td[@data-property='instructor']").text.strip().split(" (")[0]
        meeting_days = row.find_element(By.XPATH, ".//div[contains(@class, 'ui-pillbox-summary')]").text.strip()
        meeting_time = row.find_element(By.XPATH, ".//td[@data-property='meetingTime']").get_attribute("title")

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

        building = ""
        room = ""
        if 'Building: ' in meeting_time:
            building = meeting_time.split('Building: ')[1].split(' Room: ')[0].strip()
        if 'Room: ' in meeting_time:
            room = meeting_time.split('Room: ')[1].split('<')[0].strip()

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

        # If the class is Asynch, don't need time ranges or starting time/ending time
        if 'Online Asynchronous' in class_types:
            time_range = "N/A"
            starting_time = "N/A"
            ending_time = "N/A"

        # Print the extracted data for debugging
        print("Class ID:", class_id)
        print("Subject:", subject)
        print("Course Number:", course_number)
        print("Hours:", hours)
        print("Title:", title)
        print("Instructor:", instructor)
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
        print()

        # Append the data as a dictionary to the classes list
        classes.append({
            'ID': class_id,
            'Subject': subject,
            'Course Number': course_number,
            'Hours': hours,
            'Title': title,
            'Instructor': instructor,
            'Building': building,
            'Room': room,
            'Campus': campus,
            'Days': days,
            'Time': time_range,
            'Starting Time': starting_time,
            'Ending Time': ending_time,
            'Class Type': class_type
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
        time.sleep(5)
        next_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//button[@title='Next' and contains(@class, 'enabled')]")))
        next_button.click()

        # Wait for data to load again
        time.sleep(5)

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
