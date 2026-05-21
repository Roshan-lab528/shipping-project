import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from datetime import datetime
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
from selenium.webdriver.common.keys import Keys
import sys
sys.stdout.reconfigure(encoding='utf-8')
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
data = []
# -------- DRIVER SETUP --------
options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-blink-features=AutomationControlled")

driver = uc.Chrome(options=options, version_main=148)

# optional (usually not needed with UC)
driver.execute_script(
    "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
)

wait = WebDriverWait(driver, 30)

# -------- OPEN LOGIN PAGE --------
driver.get("https://www.mymsc.com/myMSC/")
# -------- LOGIN --------
time.sleep(10) 

try:
    allowall=driver.find_element(By.CSS_SELECTOR, "button[id='onetrust-accept-btn-handler']")
    allowall.click()
except:
    pass

time.sleep(5)
username=driver.find_element(By.CSS_SELECTOR, "input[type='email']")
username.send_keys("sales@tanuimpex.com")
time.sleep(2)
next=driver.find_element(By.CSS_SELECTOR, "button[type='button']")
time.sleep(2)
next.click()
time.sleep(20)
password=driver.find_element(By.CSS_SELECTOR, "input[type='password']")
password.send_keys("E@Lzy$-Sij82V2*")
time.sleep(5)
login=driver.find_element(By.CSS_SELECTOR, "button[id='next']")
login.click()
time.sleep(10)

driver.execute_script("window.location.href='/instantquote'")
time.sleep(10)

origin_port_code = sys.argv[1]
origin_port_name = sys.argv[2]
destination_port_code = sys.argv[3]
destination_port_name = sys.argv[4]
container_size = sys.argv[5]

print(origin_port_code, destination_port_code)

container_map = {
    "20DV": "1 × 20' ST",
    "40DV": "1 × 40' ST",
    "40HC": "1 × 40' HC"
}

# step 1: main component pakdo
shadow_host = driver.find_element(By.CSS_SELECTOR, "mymsc-instantquote-app")

# step 2: shadow root access karo
shadow_root = driver.execute_script("return arguments[0].shadowRoot", shadow_host)

# step 3: ab andar search karo
all_cont_size = shadow_root.find_elements(
    By.CSS_SELECTOR, "div[data-test-id^='equipment-sizetype-container']"
)

print("Total Containers:", len(all_cont_size))

# 🔥 LOOP (no stale issue)
for i in range(len(all_cont_size)):   # total 3 containers
    try:
        # ✅ har baar fresh elements lo
        all_cont_size = shadow_root.find_elements(
            By.CSS_SELECTOR, "div[data-test-id^='equipment-sizetype-container']"
        )

        con_size = all_cont_size[i]

        actual_size = con_size.find_element(
            By.CSS_SELECTOR, "span.MuiTypography-caption"
        ).text.strip()

        checkbox = con_size.find_element(By.CSS_SELECTOR, "input[type='checkbox']")
        label = con_size.find_element(By.CSS_SELECTOR, "label")

        print("Found:", actual_size)

        # ✅ Select required
        if actual_size == container_size:
            if not checkbox.is_selected():
                driver.execute_script("arguments[0].click();", label)
                print("Selected:", actual_size)

            # ✅ SAVE VALUE
            final_value = container_map.get(actual_size, "")
            print("Saved Value:", final_value)

        # ❌ Uncheck others
        else:
            if checkbox.is_selected():
                driver.execute_script("arguments[0].click();", label)
                print("Unchecked:", actual_size)

    except Exception as e:
        print("Retrying due to:", e)

# ✅ Final output
print("Final Container Value:", container_map.get(container_size, ""))
cont_size=container_map.get(container_size, "")

driver.execute_script(f"""
let host = document.querySelector('mymsc-instantquote-app');
let root = host.shadowRoot;
let input = root.querySelector('#origin');

input.focus();

// React setter
let setter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, "value"
).set;

setter.call(input, "{origin_port_code}");

// events trigger
input.dispatchEvent(new Event('input', {{ bubbles: true }}));
input.dispatchEvent(new Event('change', {{ bubbles: true }}));
""")

time.sleep(5)
# STEP 2: CLICK OPTION

driver.execute_script(f"""
let host = document.querySelector('mymsc-instantquote-app');
let root = host.shadowRoot;

let options = root.querySelectorAll('li');

for (let opt of options) {{
    if (opt.innerText.includes("{origin_port_code}")) {{
        opt.click();
        break;
    }}
}}
""")
time.sleep(5)
print("USNYC SELECT HO GAYA")

driver.execute_script(f"""
let host = document.querySelector('mymsc-instantquote-app');
let root = host.shadowRoot;
let input = root.querySelector('#destination');

input.focus();

// React setter
let setter = Object.getOwnPropertyDescriptor(
    window.HTMLInputElement.prototype, "value"
).set;

setter.call(input, "{destination_port_code}");

// events trigger
input.dispatchEvent(new Event('input', {{ bubbles: true }}));
input.dispatchEvent(new Event('change', {{ bubbles: true }}));
""")

time.sleep(5)

# STEP 2: SELECT OPTION (KEYBOARD)

driver.execute_script(f"""
let host = document.querySelector('mymsc-instantquote-app');
let root = host.shadowRoot;
let input = root.querySelector('#destination');

input.focus();
input.dispatchEvent(new KeyboardEvent('keydown', {{key: 'ArrowDown', bubbles: true}}));
input.dispatchEvent(new KeyboardEvent('keydown', {{key: 'Enter', bubbles: true}}));
""")

print(f"DESTINATION SELECT HO GAYA: {destination_port_code}")

driver.execute_script("""
let host = document.querySelector('mymsc-instantquote-app');
let root = host.shadowRoot;

// button select
let btn = root.querySelector('#search-rate-button');

btn.click();
""")
print("Search button clicked")
time.sleep(20)

today = datetime.today().strftime('%d-%b-%Y')

def get_root():
    host = driver.find_element(By.CSS_SELECTOR, "mymsc-instantquote-app")
    return driver.execute_script("return arguments[0].shadowRoot", host)

def get_cards_and_buttons():
    root = get_root()
    cards = root.find_elements(By.CSS_SELECTOR, "div.carousel-card-container")
    buttons = root.find_elements(By.CSS_SELECTOR, "button[data-test-id*='showDetailsIcon']")
    return cards, buttons

def format_date(date_text):
    try:
        parts = [p.strip() for p in date_text.split("\n") if p.strip()]
        if len(parts) >= 2:
            return f"{parts[0]}-{parts[1].capitalize()}-{datetime.now().year}"
    except:
        pass
    return ""

# =========================
# LOOP
# =========================
cards, buttons = get_cards_and_buttons()
print("Total cards:", len(cards))

for i in range(len(cards)):
    try:
        print(f"\n Processing Card {i}")

        cards, buttons = get_cards_and_buttons()

        if i >= len(cards):
            break

        card = cards[i]
        driver.execute_script("arguments[0].click();", cards[i])

        if not buttons:
            print("No visible button")
            continue

        # DATE
        dates = card.find_elements(By.CSS_SELECTOR, "div.shipping-window-date")

        start_date = format_date(dates[0].text) if len(dates) > 0 else ""
        end_date = format_date(dates[1].text) if len(dates) > 1 else ""

        print(start_date, "|", end_date)

        # SCROLL
        driver.execute_script("arguments[0].scrollIntoView({block:'center'});", card)
        time.sleep(1)

        # 🔥 INNER LOOP ADDED (ONLY CHANGE)
        for j in range(len(buttons)):
            try:
                btn = buttons[j]

                # CLICK
                driver.execute_script("""
                let btn = arguments[0];
                btn.scrollIntoView({block:'center'});
                btn.focus();
                btn.dispatchEvent(new MouseEvent('click', {bubbles:true}));
                """, btn)

                print("Clicked")
                time.sleep(10)

                # WAIT MODAL
                wait.until(lambda d: d.execute_script("""
                    let host = document.querySelector('mymsc-instantquote-app');
                    return host.shadowRoot.querySelector('[data-test-id="BreakdownModal"]') !== null;
                """))

                # =========================
                # 🔥 FINAL FIXED DATA EXTRACT
                # =========================
                records = driver.execute_script("""
                let result = {
                    freight_charge: 0,
                    freight_surcharges: 0,
                    export_surcharges: 0,
                    import_surcharges: 0
                };

                let root = document.querySelector('mymsc-instantquote-app').shadowRoot;
                let modal = root.querySelector('[data-test-id="BreakdownModal"]');
                let rows = modal.querySelectorAll('.standard-charges-row');

                let section = "";

                let import_inr = 0;
                let import_usd = 0;

                rows.forEach(row => {

                    let header = row.querySelector("strong");
                    if(header){
                        let text = header.innerText.trim();

                        if(text.includes("Freight Charge")) section = "freight_charge";
                        else if(text.includes("Freight Surcharges")) section = "freight_surcharges";
                        else if(text.includes("Export Surcharges")) section = "export_surcharges";
                        else if(text.includes("Import Surcharges")) section = "import_surcharges";
                    }

                    let amounts = row.querySelectorAll(".amount-field strong");

                    amounts.forEach(el => {

                        let txt = el.innerText.trim();
                        let num = txt.replace(/[^0-9.]/g, "");
                        if(!num) return;

                        let val = parseFloat(num);

                        if(section === "import_surcharges"){
                            if(txt.includes("INR")) import_inr += val;
                            else import_usd += val;
                        }
                        else if(section === "freight_charge"){
                            result.freight_charge += val;
                        }
                        else if(section === "freight_surcharges"){
                            result.freight_surcharges += val;
                        }
                        else if(section === "export_surcharges"){
                            result.export_surcharges += val;
                        }

                    });

                });

                let import_final = (import_inr / 94) + import_usd;

                result.import_surcharges = parseFloat(import_final.toFixed(1));

                return result;
                """)

                total = round(sum(records.values()), 1)

                records["freight_charge"] = round(records["freight_charge"], 1)
                records["freight_surcharges"] = round(records["freight_surcharges"], 1)
                records["export_surcharges"] = round(records["export_surcharges"], 1)
                records["import_surcharges"] = round(records["import_surcharges"], 1)

                print("Freight:", records["freight_charge"])
                print("Surcharges:", records["freight_surcharges"])
                print("Export:", records["export_surcharges"])
                print("Import:", records["import_surcharges"])
                print("TOTAL:", total)

                data.append([
                    today,
                    "MSC",
                    origin_port_name,
                    destination_port_name,
                    cont_size,
                    20000,
                    start_date,
                    end_date,
                    records["freight_charge"],
                    records["freight_surcharges"],
                    records["export_surcharges"],
                    records["import_surcharges"],
                    total,
                    ""
                ])

                # CLOSE MODAL
                driver.execute_script("""
                let root = document.querySelector('mymsc-instantquote-app').shadowRoot;
                let modal = root.querySelector('[data-test-id="BreakdownModal"]');

                if(modal){
                    let btn = modal.querySelector('button.close-btn');
                    if(btn){
                        btn.dispatchEvent(new MouseEvent('click', {bubbles:true}));
                    }
                }
                """)

                time.sleep(10)

            except Exception as e:
                print("Button Error:", str(e))

    except Exception as e:
        print("Error:", str(e))
        
if len(cards) == 0:
    data.append([
        today,
        "MSC",
        origin_port_name,
        destination_port_name,
        cont_size,
        20000,
        "",
        "",
        "",
        "",
        "",
        "",
        "",
        "No Data"
    ])
    print("No cards found")        
        
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