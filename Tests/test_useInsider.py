import time

from selenium import webdriver
from selenium.common import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pytest
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


@pytest.fixture
def driver():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--start-maximized")  # Opens in full-screen mode
    options.add_argument("--disable-dev-shm-usage")

    driver = webdriver.Chrome(options=options)
    yield driver
    driver.quit()

@pytest.fixture
def setup(driver):
    # Open the website and perform setup tasks
    driver.get("https://useinsider.com/")
    # Accept cookies
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.LINK_TEXT, "Accept All"))).click()

    return driver  # Return the driver for use in tests

# Helper method to scroll to element.
def scroll_to_element(driver, element):
    actions = ActionChains(driver)
    actions.move_to_element(element).perform()


@pytest.mark.main
def test_homepage(driver):
    driver.get("https://useinsider.com/")
    assert "Insider" in driver.title


@pytest.mark.main
def test_filter_jobs(driver):
    driver.get("https://useinsider.com/careers/quality-assurance/")
    driver.find_element(By.LINK_TEXT, "See all QA jobs").click()

    # When ran without setup, Accept cookies
    try:
        WebDriverWait(driver, 2).until(
            EC.element_to_be_clickable((By.LINK_TEXT, "Accept All"))
        ).click()
        print("Clicked 'Accept All'.")
    except TimeoutException:
        # If the "Accept All" button is not found, just continue without error
        print("'Accept All' button not found, continuing...")

    # Open location filter and attempt to select "Istanbul, Turkey" with retries if needed
    # NOTE: Data takes time to load and dropdown needs to be re-openned so we use retries (expected behavior?)
    location_filter_xpath = "//*[@id='select2-filter-by-location-container']"
    location_option_xpath = "//li[contains(@class, 'select2-results__option') and text()='Istanbul, Turkey']"

    max_attempts = 3
    delay_seconds = 5
    attempts = 0

    while attempts < max_attempts:
        try:
            # Click the location dropdown
            location_filter = driver.find_element(By.XPATH, location_filter_xpath)
            location_filter.click()

            # Attempt to click on "Istanbul, Turkey" option
            driver.find_element(By.XPATH, location_option_xpath).click()
            print("Location option 'Istanbul, Turkey' selected.")
            break  # Exit loop if successful

        except NoSuchElementException:
            attempts += 1
            print(
                f"Location option not found, retrying in {delay_seconds} seconds... (Attempt {attempts}/{max_attempts})")
            driver.find_element(By.XPATH, "//*[@id='top-filter-form']/div[1]/label").click()
            time.sleep(delay_seconds)

    else:
        raise Exception("Failed to select location option 'Istanbul, Turkey' after multiple attempts.")

    # Open department filter and select "Quality Assurance"
    department_filter = driver.find_element(By.XPATH, "//*[@id='select2-filter-by-department-container']")
    department_filter.click()

    department_option = driver.find_element(By.XPATH,
                                            "//li[contains(@class, 'select2-results__option') and text()='Quality Assurance']")
    driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});",
                          department_option)
    department_option.click()

    # Wait for the filtered job list to be visible
    WebDriverWait(driver, 10).until(
        EC.visibility_of_element_located((By.XPATH, "//div[@class='position-list-item-wrapper bg-light']"))
    )

    # Check that the job list appears
    job_list = driver.find_elements(By.XPATH, "//*[contains(@class, 'position-list-item')]")
    assert len(job_list) > 0, "No jobs found after applying the filters."

    # Validate each job's details
    for job in job_list:
        # Find the position title
        position = job.find_element(By.XPATH, ".//p[contains(@class, 'position-title')]")
        # Find the department
        department = job.find_element(By.XPATH, ".//span[contains(@class, 'position-department')]")
        # Find the location
        location = job.find_element(By.XPATH, ".//div[contains(@class, 'position-location')]")

        assert "Quality Assurance" in position.text, f"Position text does not contain 'Quality Assurance'."
        assert "Quality Assurance" in department.text, f"Department text does not contain 'Quality Assurance'."
        assert "Istanbul, Turkey" in location.text, f"Location text does not contain 'Istanbul, Turkey'."

        # Hover over the element to reveal the "View Role" button
        view_role_button = job.find_element(By.XPATH, ".//a[contains(text(), 'View Role')]")
        # Hover to trigger visibility
        action = ActionChains(driver)
        action.move_to_element(view_role_button).perform()
        # Wait a bit to ensure the button becomes visible
        WebDriverWait(driver, 5).until(
            EC.visibility_of(view_role_button)
        )
        # Scroll the button into view smoothly
        driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center', inline: 'nearest'});",
                              view_role_button)
        view_role_button.click()
        # Wait for the new tab to be opened
        WebDriverWait(driver, 10).until(lambda d: len(d.window_handles) > 1)
        # Switch to the new tab (the new tab will be at index 1, assuming this is the first additional tab opened)
        driver.switch_to.window(driver.window_handles[1])
        # Assert URL in new tab
        WebDriverWait(driver, 10).until(EC.url_contains("jobs.lever.co"))
        assert "jobs.lever.co" in driver.current_url, f"Expected a URL containing 'jobs.lever.co', but got {driver.current_url}"

        driver.close()  # Close the new tab
        driver.switch_to.window(driver.window_handles[0])  # Switch back to the original tab

    print("Page title contains 'Quality Assurance'.")
    print("All jobs passed the checks and redirection to Lever form is verified.")
