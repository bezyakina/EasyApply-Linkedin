import json
import re
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys


class EasyApplyLinkedin:
    def __init__(self, data):
        """Parameter initialization."""

        self.email = data["email"]
        self.password = data["password"]
        self.keywords = data["keywords"]
        self.location = data["location"]
        self.search_pattern_include = data["search_pattern_include"]
        self.search_pattern_exclude = data["search_pattern_exclude"]
        self.driver = webdriver.Chrome(data["driver_path"])

    def login_linkedin(self):
        """This function logs into your personal LinkedIn profile."""

        # go to the LinkedIn login url
        self.driver.get("https://www.linkedin.com/login")

        # introduce email and password and hit enter
        login_email = self.driver.find_element_by_name("session_key")
        login_email.clear()
        login_email.send_keys(self.email)
        login_pass = self.driver.find_element_by_name("session_password")
        login_pass.clear()
        login_pass.send_keys(self.password)
        login_pass.send_keys(Keys.RETURN)

    def job_search(self):
        """This function goes to the 'Jobs' section a looks for all the jobs
        that matches the keywords and location."""

        # go to Jobs
        jobs_link = self.driver.find_element_by_link_text("Jobs")
        jobs_link.click()

        time.sleep(5)

        # search based on keywords and location and hit enter
        search_keywords = self.driver.find_element_by_xpath(
            "//input[starts-with(@id, 'jobs-search-box-keyword')]"
        )
        search_keywords.clear()
        search_keywords.send_keys(self.keywords)
        search_location = self.driver.find_element_by_xpath(
            "//input[starts-with(@id, 'jobs-search-box-location')]"
        )
        search_location.clear()
        search_location.send_keys(self.location)
        search_location.send_keys(Keys.RETURN)

    def filter(self):
        """This function filters all the job results by 'Easy Apply' and
        'Experience level'."""

        # select all filters, click on Easy Apply and Experience level,
        # and apply the filter
        all_filters_button = self.driver.find_element_by_xpath(
            "//button[@data-control-name='all_filters']"
        )
        all_filters_button.click()
        time.sleep(3)
        easy_apply_button = self.driver.find_element_by_xpath(
            "//label[@for='linkedinFeatures-f_AL']"
        )
        easy_apply_button.click()
        time.sleep(3)
        experience_level_button = self.driver.find_element_by_xpath(
            "//label[@for='experience-4']"
        )
        experience_level_button.click()
        time.sleep(3)
        apply_filter_button = self.driver.find_element_by_xpath(
            "//button[@data-control-name='all_filters_apply']"
        )
        apply_filter_button.click()

    def find_offers(self):
        """This function finds all the offers through all the pages result
        of the search and filter."""

        # find the total amount of results (in case there are more than just
        # 24 of them)
        total_results = self.driver.find_element_by_class_name(
            "display-flex.t-12.t-black--light.t-normal"
        )
        total_results_int = int(total_results.text.split(" ")[0])
        print(total_results_int)

        time.sleep(3)

        # get results for the first page
        current_page = self.driver.current_url
        results = self.driver.find_elements_by_class_name(
            "occludable-update.artdeco-list__item--offset-2.artdeco"
            "-list__item.p0.ember-view"
        )

        # for each job add, submits application if no questions asked
        for result in results:
            hover = ActionChains(self.driver).move_to_element(result)
            hover.perform()
            titles = result.find_elements_by_class_name(
                "disabled.ember-view.job-card-container__link."
                "job-card-list__title"
            )
            # filter each title with include and exclude patterns
            for title in titles:
                include = re.search(self.search_pattern_include, title.text)
                if include is not None:
                    exclude = re.search(
                        self.search_pattern_exclude, title.text
                    )
                    if exclude is None:
                        self.submit_apply(title)

        # if there is more than one page, find the pages and apply to the
        # results of each page
        if total_results_int > 24:
            time.sleep(3)

            # find the last page and construct url of each page based on the
            # total amount of pages
            find_pages = self.driver.find_elements_by_class_name(
                "artdeco-pagination__indicator.artdeco-pagination__indicator"
                "--number.ember-view"
            )
            total_pages = find_pages[len(find_pages) - 1].text
            total_pages_int = int(re.sub(r"[^\d.]", "", total_pages))
            get_last_page = self.driver.find_element_by_xpath(
                "//button[@aria-label='Page " + str(total_pages_int) + "']"
            )
            get_last_page.send_keys(Keys.RETURN)
            time.sleep(3)
            last_page = self.driver.current_url
            total_jobs = int(last_page.split("start=", 1)[1])

            # go through all available pages and job offers and apply
            for page_number in range(25, total_jobs + 25, 25):
                self.driver.get(current_page + "&start=" + str(page_number))
                time.sleep(3)
                results_ext = self.driver.find_elements_by_class_name(
                    "occludable-update.artdeco-list__item--offset-2.artdeco"
                    "-list__item.p0.ember-view"
                )
                for result_ext in results_ext:
                    hover_ext = ActionChains(self.driver).move_to_element(
                        result_ext
                    )
                    hover_ext.perform()
                    titles_ext = result_ext.find_elements_by_class_name(
                        "disabled.ember-view.job-card-container__link.job"
                        "-card-list__title"
                    )
                    for title_ext in titles_ext:
                        include = re.search(
                            self.search_pattern_include, title_ext.text
                        )
                        if include is not None:
                            exclude = re.search(
                                self.search_pattern_exclude, title_ext.text
                            )
                            if exclude is None:
                                self.submit_apply(title_ext)
        else:
            self.close_session()

    def submit_apply(self, job_add):
        """This function submits the application for the job add found"""

        print("You are applying to the position of: ", job_add.text)
        job_add.click()
        time.sleep(3)

        # click on the easy apply button, skip if already applied to the
        # position
        try:
            in_apply = self.driver.find_element_by_xpath(
                "//button[@data-control-name='jobdetails_topcard_inapply']"
            )
            in_apply.click()
        except NoSuchElementException:
            print("You already applied to this job, go to next...")
            pass
        time.sleep(3)

        # try to submit if submit application is available...
        try:
            submit = self.driver.find_element_by_xpath(
                "//button[@data-control-name='submit_unify']"
            )
            submit.send_keys(Keys.RETURN)
            time.sleep(3)
            dismiss_button = self.driver.find_element_by_xpath(
                "//button[@aria-label='Dismiss']"
            )
            dismiss_button.click()

        # ... if not available, discard application and go to next
        except NoSuchElementException:
            print("Not direct application, going to next...")
            try:
                discard = self.driver.find_element_by_xpath(
                    "//button[@data-test-modal-close-btn]"
                )
                discard.send_keys(Keys.RETURN)
                time.sleep(3)

                discard_confirm = self.driver.find_element_by_xpath(
                    "//button[@data-test-dialog-primary-btn]"
                )
                discard_confirm.send_keys(Keys.RETURN)
                time.sleep(3)
            except NoSuchElementException:
                pass

        time.sleep(3)

    def close_session(self):
        """This function closes the actual session."""

        print("End of the session, see you later!")
        self.driver.close()

    def apply(self):
        """Apply to job offers."""

        self.driver.maximize_window()
        self.login_linkedin()
        time.sleep(5)
        self.job_search()
        time.sleep(5)
        self.filter()
        time.sleep(5)
        self.find_offers()
        time.sleep(5)
        self.close_session()


if __name__ == "__main__":
    with open("config.json") as config_file:
        data = json.load(config_file)

    bot = EasyApplyLinkedin(data)
    bot.apply()
