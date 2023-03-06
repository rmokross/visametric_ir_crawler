from selenium import webdriver
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from datetime import datetime, date


# KATENÜBERWEISUNG:
# 	KARAJ
# 	TEHERAN
# 	NORMAL
# 	2 Antragsteller
# 	ZAHLUNGSART: Karten-und modile Zahlung

# 	KARTE: 6037697617573701
# 	DATE KARTE: 1401/12/02
# 	TRANSACTIONID: 10949109


# ANSTRAGSSTELLER:

# 	SHEBANR: IR750190000000338403647009
# 	PER_NAME: سارا مزرعی جورشری

# 	P1: 
# 		Vorname: SARA
# 		Name: MAZRAEİ JORSHARY
# 		GEB. DAT:
# 			TAG: 22
# 			Mon: 09
# 			JAHR: 1977
# 		PASSNR: X60449556
# 		TEL: 00989981125045
# 		EMAIL: sara_mzj@yahoo.com
	
# 	P2:
# 		Vorname: BİJAN
# 		Name: KALANTARİ
# 		GEB. DAT:
# 			TAG: 21
# 			Mon: 01
# 			JAHR: 1970
# 		PASSNR: B61735470
# 		TEL: 00989981125045
# 		EMAIL: sara_mzj@yahoo.com

BASE_URL = "https://ir-appointment.visametric.com/de"
CHROME_PATH = "C:\\Users\\Robby\\Projekte\\visametric_ir_crawler\\chromedriver.exe"
NATIONALITY="Iran"
UPPER_LIMIT_CALENDAR_SEARCH = 30

# ANTRTAGSDETAILS
RESIDENCE = "KARAJ"
ACC_CENTER = "TEHERAN"
SERVICETYPE = "NORMAL"
NUM_OF_APPLICANTS = 2
PAYMENTTYPE = "Card" # check payment_map
STR_CARDNUMBER = "6037697617573701"
TRANSACTION_ID = "10949109"
STR_PAYMENT_YEAR = "1401"
STR_PAYMENT_MONTH = "Esfand"
PAYMENT_DAY = 2

# Dict for PAYMENTTYPE input
map_payment = {
    "Card" : "atm",
    "Transfer" : "transfer"
}

# Dict for persian month mapping "Month Name" : "Month Number" 
map_pers_month = {
    "Farvardin" : 1,
    "Ordibehesht" : 2,
    "Khordad" : 3,
    "Tir" : 4,
    "Mordad" : 5,
    "Shahrivar" : 6,
    "Mehr" : 7,
    "Aban" : 8,
    "Azar" : 9,
    "Dey" : 10,
    "Bahman" : 11,
    "Esfand" : 12
}

# Set Webdriver options
options = webdriver.ChromeOptions()
options.headless = False
options.add_argument("--disable-notifications")

# Start Webdriver
driver = webdriver.Chrome(executable_path=CHROME_PATH, options=options)
wait = WebDriverWait(driver, 10)

#### 1. PAGE ONE ####
driver.get(BASE_URL)

# Start Schengen Form
driver.find_element(By.XPATH, '//a[@id="schengenBtn"]').click()

# Einverständniserklärung
driver.find_element(By.XPATH, '//input[@name="surveyStart"]').click()
#wait.until(EC.element_to_be_clickable((By.XPATH, '//input[@name="nationality" and @value="{NATIONALITY}"]')))
sleep(2)
driver.find_element(By.XPATH, f'//input[@name="nationality" and @value="{NATIONALITY}"]').click()

# SOLVE reCAPTCHA
sleep(60)

driver.find_element(By.XPATH, '//button[@id="btnSubmit"]').click()

#### 2. PAGE TWO ####

#wait.until(EC.element_to_be_clickable((By.XPATH, '//select[@id="city"]')))
sleep(2)
# City dropdown
city_dropdown = Select(driver.find_element(By.XPATH, '//select[@id="city"]'))
city_dropdown.select_by_visible_text(RESIDENCE)

# Annahmezentrum dropdown
annahme_dropdown = Select(driver.find_element(By.XPATH, '//select[@id="office"]'))
annahme_dropdown.select_by_visible_text(ACC_CENTER)

# Serviceart dropdown
service_dropdown = Select(driver.find_element(By.XPATH, '//select[@id="officetype"]'))
service_dropdown.select_by_visible_text(SERVICETYPE)

# Anzahl der Antragssteller dropdown
service_dropdown = Select(driver.find_element(By.XPATH, '//select[@id="totalPerson"]'))
service_dropdown.select_by_visible_text(f"{NUM_OF_APPLICANTS} Antragsteller")

# Zahlungsdialog
sleep(2)
try:
    driver.find_element(By.XPATH, f'//input[@name="paytype" and @value="{map_payment[PAYMENTTYPE]}"]').click()
except NoSuchElementException as e:
    print("Element not found: ", e)
sleep(2)
driver.find_element(By.XPATH, '//input[@id="paymentCardInput"]').send_keys(STR_CARDNUMBER)
# Enter correct date value
driver.find_element(By.XPATH, '//input[@id="popupDatepicker2"]/following-sibling::span').click()
sleep(2)
target_date = datetime.strptime(f"{STR_PAYMENT_YEAR} {map_pers_month[STR_PAYMENT_MONTH]}", "%Y %m")
counter = 0
str_year_month_pers = date.today().strftime("%Y %m") ## ADJUST PERS CAL
str_year_month_pers = "1401 Esfand"
while True:
    if counter == UPPER_LIMIT_CALENDAR_SEARCH:
        raise Exception(f"Couldn't pick the correct date (UPPER_LIMIT_CALENDAR_SEARCH set to {UPPER_LIMIT_CALENDAR_SEARCH})")

    cur_month_page_text = driver.find_element(By.XPATH, f'//div[text()="{str_year_month_pers}"]').text
    cur_date = datetime.strptime(cur_month_page_text, "%Y %m")
    
    if cur_date == target_date:
        data_date = f"{STR_PAYMENT_YEAR},{map_pers_month[STR_PAYMENT_MONTH]},{PAYMENT_DAY}"
        driver.find_element(By.XPATH, f'//td[@data-date="{data_date}"]').click()
        break
    elif cur_date > target_date:
        driver.find_element(By.XPATH, f'//div[text()="{str_year_month_pers}"]/preceding-sibling::div').click()
        counter += 1
        continue
    else:
        driver.find_element(By.XPATH, f'//div[text()="{str_year_month_pers}"]/following-sibling::div').click()
        counter += 1
        continue

# check for results
driver.find_element(By.XPATH, '//a[@id="checkCardListBtn"]').click()

# Select Transaction
driver.find_element(By.XPATH, f'//td[text()="{TRANSACTION_ID}"]/preceding-sibling::td').click()

# Go to next page of form
driver.find_element(By.XPATH, '//a[@id="btnAppCountNext"]')