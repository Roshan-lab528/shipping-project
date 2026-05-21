import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import sys
sys.stdout.reconfigure(encoding='utf-8')
from datetime import datetime
import pandas as pd
import re
import os
# ================= FILE =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))            
file_path = os.path.join(BASE_DIR, "global", "rates.xlsx")
print(BASE_DIR)
print(file_path)
columns = [
    "date",
    "ship_line",
    "org_port",
    "dest_port",
    "cont_type",
    "weight",
    "etd_from",
    "eta_to",
    "ocean_frt",
    "frt_surchg",
    "exp_surchg",
    "imp_surchg",
    "total_usd",
    "remarks"
]

container_map = {
    "20ft Dry Van": "1 × 20' ST",
    "40ft Dry Van": "1 × 40' ST",
    "40ft Dry Van High Cube": "1 × 40' HC"
}

origin_port_code = sys.argv[1]
origin_port_name = sys.argv[2]
destination_port_code = sys.argv[3]
destination_port_name = sys.argv[4]
container_size = sys.argv[5]
print("Received arguments:", origin_port_code, origin_port_name, destination_port_code, destination_port_name, container_size)


# -------- DRIVER SETUP --------
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")
driver = uc.Chrome( options=options, version_main=148, use_subprocess=True )

wait = WebDriverWait(driver, 30)

# -------- OPEN LOGIN PAGE --------
driver.get("https://my.icontainers.com/sign-in")
# -------- LOGIN --------
while True:
    try:
        username = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='email']")))
        username.clear()
        username.send_keys("aman.aggarwal@softwareimpex.com")

        password = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password']")))
        password.clear()
        password.send_keys("4gRmrzs2FPf3Knj")

        remember = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='remember']")))
        remember.click()

        login_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']")))
        login_btn.click()      
        time.sleep(20)
        # Example: dashboard ya logout button check
        dashboard = driver.find_element(By.CSS_SELECTOR, "div[class='sc-dxjgzI fCktDF']").text.strip()
        print(dashboard)
        time.sleep(5)
        if "Aman" in dashboard:
            print("Login successful!")
            driver.execute_script("window.location.href='/get-quote/ocean?selectedShipmentType=FCL'")
            time.sleep(5)
            break
        else:
            print("Login failed, retrying...")
    except Exception as e:
        print("Login error:", e)
        
origin_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='origin']")))
origin_input.send_keys(origin_port_code)
origin_options = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-testid='locationDropdownItem']")))
driver.execute_script("arguments[0].click();", origin_options[0])

dest_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "input[name='destination']")))
dest_input.send_keys(destination_port_code)

dest_option = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-testid='locationDropdownItem']")))
time.sleep(2)
driver.execute_script("arguments[0].click();", dest_option[0])
time.sleep(2)


input_box = wait.until(EC.element_to_be_clickable((
    By.XPATH, "//input[contains(@id,'react-select')]"
)))
input_box.click()

# type to trigger dropdown
input_box.send_keys(container_size)

# dynamic xpath
option = wait.until(EC.presence_of_element_located((
    By.XPATH, f"//div[@role='option' and contains(.,'{container_size}')]"
)))

driver.execute_script("arguments[0].click();", option)
commodity_box = wait.until(EC.element_to_be_clickable((
    By.XPATH, "(//input[contains(@id,'react-select')])[2]"
)))
commodity_box.click()
commodity_box.send_keys("Dry or General Cargo")
commodity = wait.until(EC.presence_of_element_located((
    By.XPATH, "//div[@role='option' and contains(.,'Dry or General Cargo')]"
)))
driver.execute_script("arguments[0].click();", commodity)
time.sleep(3)

search_btn = wait.until(EC.element_to_be_clickable((
    By.CSS_SELECTOR, "button[type='submit']"
)))
search_btn.click()
time.sleep(30)
print("Final Container Value:", container_map.get(container_size, ""))
cont_size=container_map.get(container_size, "")
data = []
today = datetime.today().strftime('%d-%b-%Y')
cards = []

time.sleep(30)
# try:
#     all_rates_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-testid='ALL_RATES']")))
#     all_rates_btn.click()
# except:
#     pass
time.sleep(2)
try:
    cards = wait.until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[data-testid='SingleRate']"))
    )
except:
    data.append([today, "ICONTAINERS", origin_port_name, destination_port_name, cont_size, 20000, "", "", "", "", "", "", "", "No Data"])
    print("Stopping scraper...")
    cards = []

print("Total cards:", len(cards))

try:
    driver.find_element(By.CSS_SELECTOR, "button[aria-label='Close']").click()
    time.sleep(2)
except:
    pass    

def format_end_date(raw_end_date):
    try:
        return datetime.strptime(raw_end_date, "%d %b %Y").strftime("%d-%b-%Y")
    except Exception as e:
        return None

for lo in cards:
    try:
        start_date = 'Valid Until'

        raw_end_date = lo.find_element(
            By.XPATH,
            ".//div[.='Valid Until']/following::div[contains(@class,'value')][1]"
        ).text

        end_date = format_end_date(raw_end_date)
        print(start_date, end_date)

        # open modal
        shows = lo.find_element(By.CSS_SELECTOR, "a[data-testid='ShowRateDetailsButton']")
        driver.execute_script("arguments[0].click();", shows)

        # wait for modal content
        wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//div[.='Origin Charges']")
        ))

        # Origin
        otext = driver.find_element(
            By.XPATH,
            "//div[.='Origin Charges']/ancestor::div[contains(@class,'SectionHeader')]//span"
        ).text
        origin_charge = round(float(re.search(r"[\d,]+\.?\d*", otext).group().replace(",", "")), 2)

        # Freight
        ftext = driver.find_element(
            By.XPATH,
            "//div[.='Freight Charges']/ancestor::div[contains(@class,'SectionHeader')]//span"
        ).text
        freight_charge = round(float(re.search(r"[\d,]+\.?\d*", ftext).group().replace(",", "")), 2)

        export_charge = 0
        import_charge = 0

        total = round(origin_charge + freight_charge + export_charge + import_charge, 2)

        data.append([
            today,
            "ICONTAINERS",
            origin_port_name,
            destination_port_name,
            cont_size,
            20000,
            start_date,
            end_date,
            origin_charge,
            freight_charge,
            export_charge,
            import_charge,
            total,
            ""
        ])

        # close modal
        close_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "button[aria-label='close']")
        ))
        driver.execute_script("arguments[0].click();", close_btn)

        # wait modal close
        wait.until(EC.invisibility_of_element_located(
            (By.XPATH, "//div[.='Origin Charges']")
        ))

    except Exception as e:
        print("Error in one card:", e)
   
new_df = pd.DataFrame(data, columns=columns)
try:
    old_df = pd.read_excel(file_path)
    final_df = pd.concat([old_df, new_df], ignore_index=True)
except:
    final_df = new_df
final_df.to_excel(file_path, index=False)

print("Data saved successfully")
try:
    driver.quit()
except:
    pass