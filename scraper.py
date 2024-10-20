import ast
import json
import random
import time
import re

from selenium import webdriver
from selenium.common import TimeoutException


class Scraper:
    def __init__(self):
        self.browser = webdriver.Firefox()
        self.rand = random.SystemRandom()

    def scrape(self):
        instance = int(input("Connection instance: "))
        start_line = int(input("Start line: "))
        users = self.read_instance(instance)
        self.load_page('https://www.linkedin.com')
        self.add_cookies()
        ii = 1
        for usr in users:
            if ii < start_line:
                ii += 1
                continue
            if instance == 11:
                self.load_page(f'https://www.linkedin.com/in/{usr}/details/experience/')
            else:
                self.load_page(f'https://www.linkedin.com/in/{usr[0]}/details/experience/')
            experience = self.capture_experience(usr, self.get_source())
            print(experience)
            degree = '1st' if instance == 11 else '2nd'
            with open(f"{degree}-deg-conns/{instance}.json", "a") as ff:
                ff.write(f"{json.dumps(experience)}\n")
            ii += 1
        print()
        print()
        print("SCRAPING COMPLETE")
        self.browser.close()

        # with open('mine.txt', 'r') as ff:
        #     start_line = 250
        #     ii = 1
        #     for line in ff.readlines():
        #         if ii < start_line:
        #             ii += 1
        #             continue
        #         pattern = re.compile(r'https://www.linkedin.com/in/(.*?)/')
        #         username = pattern.findall(line)[0]
        #         print(f"Gathering connections of conn {ii}, {username}")
        #         self.load_page(line.strip())
        #         time.sleep(3)
        #         try:
        #             url = "https://www.linkedin.com" + self.view_connections(self.get_source())
        #         except TypeError:
        #             print("ERROR: No connections found")
        #             continue
        #         self.capture_connections(url, username)
        #         ii += 1
        # self.browser.close()

    def view_connections(self, page_source_lines: list[str]):
        # Initialize a list to hold extracted text
        extracted_texts = []
        pattern = re.compile(r'href="(.*?)"')

        # Loop through each line in the source
        for line in page_source_lines:
            # Check if the line contains the specific span element
            # if '<span aria-hidden="true">' in line:
            # matches = pattern.findall(line)
            # print(matches)

            if '/search/results/people/?connectionOf' in line:
                matches: list[str] = pattern.findall(line)
                if len(matches) > 0:
                    amp = matches[0].replace("amp;", "")
                    open_bracket = amp.replace("%5B", "[")
                    close_bracket = open_bracket.replace("%5D", "]")
                    quotes = close_bracket.replace("%22", '"')
                    url = quotes
                    # Add the extracted text to the list
                    extracted_texts.append(url.strip())

        # Print the extracted texts
        print()
        print("Url found:")
        for text in extracted_texts:
            print(text)
            return text

    def capture_connections(self, url: str, username: str):
        page = url + '&page='
        pattern = re.compile(r'class="app-aware-link " href="https://www.linkedin.com/in/(.*?)\?miniProfileUrn')
        missed_pages = []

        ii = 0
        while ii > -1:
            self.load_page(page + str(ii + 1))
            page_source_lines = self.get_source()

            with open(f'connection-lists/{username}.txt', 'a') as ff:
                unames = 0
                ff.write(f"# Page {ii + 1}:\n")
                for line in page_source_lines:
                    if "No results found" in line:
                        unames = 10
                        ii = -2
                        print("Final page reached")
                        ff.write(f"#\n"
                                 f"# Scraping Complete\n"
                                 f"# Missed pages: {str(missed_pages)}")
                        break
                    matches: list[str] = pattern.findall(line)
                    if len(matches) > 0:
                        ff.write(matches[0] + '\n')
                        unames += 1
                        print(matches[0])
            if unames < 10:
                print(f"Missed {10 - unames} usernames on page {ii + 1}")
                missed_pages.append(ii + 1)
            print(f"Page {ii + 1} scraped")
            ii += 1

    def capture_positions(self, usr: tuple[str, list[str]] | str, page_source_lines: list[str]) -> dict:
        if isinstance(usr, str):
            connection_data: dict = {'usr': usr}
        else:
            connection_data = dict = {'usr': usr[0]}
        pattern = re.compile(r'<!---->(.*?)<!---->')
        div_section = "ZqEubGkshzTjXqgNSyRxRADkIiUxovqoOpU"
        div_header = "display-flex flex-column full-width align-self-center"
        div_link = "https://www.linkedin.com/company/"
        searching = False
        is_position = False

        for line in page_source_lines:
            if div_section in line:
                searching = True
                continue

            if searching:
                if div_header in line and not is_position:
                    is_position = True
                    continue
                elif div_link in line and not is_position:
                    searching = False

    def capture_experience(self, usr: tuple[str, list[str]] | str, page_source_lines: list[str]) -> dict:
        # example_dict = {
        #     "usr": "suzannecampi",
        #     "name": "Suzanne Campi",
        #     "works_at": ["Microsoft"],
        #     "worked_at": ["Meta", "Apple", "Google"],
        #     "first_deg": ["karimi", "andylukens"]
        # }
        if isinstance(usr, str):
            connection_data: dict = {'usr': usr}
        else:
            connection_data: dict = {'usr': usr[0]}
        pattern = re.compile(r'<!---->(.*?)<!---->')
        strip_company_pattern = re.compile(r'(.*?) ·')
        company_entry = "pvs-list__paged-list-item artdeco-list__item pvs-list__item--line-separated pvs-list__item--one-column"
        company_name_bold = "hoverable-link-text t-bold"
        company = ""
        inside_entry = False
        searching = False
        found = False
        present = False
        past = False
        name_found = False

        # Loop through each line in the source
        for line in page_source_lines:
            if 'artdeco-entity-lockup__title ember-view' in line:
                name_found = True
                continue
            if name_found:
                name = line.strip()
                connection_data['name'] = name
                name_found = False

            if inside_entry:
                if company_name_bold in line:
                    searching = True
                    continue
                # Check if the line contains the specific span element
                if '<span aria-hidden="true">' in line and not found:
                    if searching:
                        matches = pattern.findall(line)

                        if len(matches) > 0 and '·' in matches[0]:
                            matches = strip_company_pattern.findall(matches[0])

                        if len(matches) > 0:
                            company = matches[0].strip()
                            # print(matches[0])
                        searching = False
                        found = True
                    else:
                        searching = True
                if found:
                    if '- Present' in line:
                        present = True
                        inside_entry = False
                        continue
                    if company_entry in line:
                        past = True
                    elif 'scaffold-layout__aside' in line:
                        past = True
                        inside_entry = False
            elif company_entry in line:
                inside_entry = True

            if found and present:
                if 'works_at' in connection_data and connection_data['works_at'] is not None:
                    connection_data['works_at'].append(company)
                else:
                    connection_data['works_at'] = [company]
                present = False
                found = False
                searching = False
            elif found and past:
                if 'worked_at' in connection_data and connection_data['worked_at'] is not None:
                    connection_data['worked_at'].append(company)
                else:
                    connection_data['worked_at'] = [company]
                past = False
                found = False
                searching = False

        if not isinstance(usr, str):
            connection_data['first_deg'] = usr[1]
        return connection_data

    def load_page(self, url):
        while True:
            try:
                self.browser.get(url)
                break
            except TimeoutException:
                print()
                print("TIMEOUT")
                print()
                continue

        time.sleep(self.rand.randint(90, 110) / 10)

    def add_cookies(self):
        with open('cookies.txt', 'r') as file:
            for ll in file:
                # Skip comment lines
                if ll.startswith("#"):
                    continue

                # Strip trailing newline and split the line into components
                parts = ll.strip().split('\t')
                # Check if the line has the correct number of components
                if len(parts) == 7:
                    cookie = {
                        'domain': parts[0],
                        'name': parts[5],
                        'value': parts[6],
                        'path': parts[2],
                        'secure': parts[3] == 'TRUE',
                        # Expiry needs to be an integer, but it's optional, omit if causing issues
                        # 'expiry': int(parts[4])
                    }

                    # Add the cookie to the browser session
                    self.browser.add_cookie(cookie)

        # Refresh the page to apply cookies
        self.browser.refresh()
        time.sleep(5)
        print("cookies added")
        time.sleep(5)

    def get_source(self) -> list[str]:
        source = self.browser.page_source
        # Split the HTML source into lines if you're working with the full page source
        return source.split('\n')

    def read_instance(self, instance: int) -> list[tuple[str, list[str]]] | list[str]:
        if instance == 11:
            first_deg_conns: list[str] = []
            pattern = re.compile(r'linkedin.com/in/(.*?)/')
            with open(f'1st-deg-conns/{instance}.txt', 'r') as ff:
                for line in ff.readlines():
                    first_deg_conns.append(pattern.findall(line)[0].strip())
            return first_deg_conns
        else:
            second_deg_conns: list[tuple[str, list[str]]] = []
            with open(f'2nd-deg-conns/{instance}.txt', 'r') as ff:
                for line in ff.readlines():
                    second_deg_conns.append(ast.literal_eval(line.rstrip('\n')))
            return second_deg_conns


if __name__ == '__main__':
    scraper = Scraper()
    scraper.scrape()
