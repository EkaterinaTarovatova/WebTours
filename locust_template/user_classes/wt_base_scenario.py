from locust import task, SequentialTaskSet, HttpUser, constant_pacing, events, FastHttpUser
from config.config import cfg, logger
import sys, re, random
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_file, open_random_csv_file


class PurchaseFlightTicket(SequentialTaskSet):
    def on_start(self):
        self.user_data_csv_file = './test_data/user_data.csv'
        self.users_data = open_csv_file(self.user_data_csv_file)
        self.random_users_data = open_random_csv_file(self.user_data_csv_file)
        logger.info(f'______LIST_OF_USERS:{self.random_users_data}')

    @task()
    def uc_00_getHomePage(self):
        r00_01_response = self.client.get(
            '/WebTours/',
            name="r00_01_response",
            allow_redirects=False,
        )

        with self.client.get(
                '/WebTours/header.html',
                name="r00_02_header_html",
                allow_redirects=False,
                catch_response=True
        ) as r00_02_header_html:
            check_http_response(r00_02_header_html, 'images/webtours.png')

        check = 'Web Tours'
        with self.client.get(
                '/cgi-bin/welcome.pl?signOff=true',
                name="r00_03_welcome_pl",
                allow_redirects=False,
                catch_response=True
        ) as r00_03_welcome_pl:
            check_http_response(r00_03_welcome_pl, f'{check}')

        with self.client.get(
                '/cgi-bin/nav.pl?in=home',
                name="r00_04_nav_pl",
                allow_redirects=False,
                catch_response=True
        ) as r00_04_nav_pl:
            check_http_response(r00_04_nav_pl, 'Web Tours Navigation Bar')

        with self.client.get(
                '/WebTours/home.html',
                name="r00_05_home_html",
                allow_redirects=False,
                catch_response=True
        ) as r00_05_home_html:
            check_http_response(r00_05_home_html, 'Welcome to the Web Tours site.')

        match = re.search(r'name="userSession" value="([^"]+)"', r00_04_nav_pl.text)
        if match:
            self.user_session = match.group(1)
        else:
            self.interrupt(msg="Could not find userSession in response")

    @task()
    def uc_01_Login(self):
        if not hasattr(self, 'user_session'):
            self.interrupt(msg="No user_session available")

        self.random_users_row = random.choice(self.random_users_data)
        self.login = self.random_users_row["username"]
        self.password = self.random_users_row["password"]

        self.body_r_01_login_pl = f'userSession={self.user_session}&username={self.login}&password={self.password}&login.x=0&login.y=0&JSFormSubmit=off'
        print(f"_____BODY LOGIN: {self.body_r_01_login_pl}")
        logger.info(f"_____BODY LOGIN: {self.body_r_01_login_pl}")

        with self.client.post(
                '/cgi-bin/login.pl',
                name="r01_01_login_pl",
                allow_redirects=False,
                catch_response=True,
                headers={'content-type': 'application/x-www-form-urlencoded'},
                data=self.body_r_01_login_pl
        ) as r01_01_login_pl:
            check_http_response(r01_01_login_pl, 'Welcome to the Web Tours site.')


class WebToursBaseUserClass(FastHttpUser):
    wait_time = constant_pacing(cfg.pacing)
    host = cfg.url
    tasks = [PurchaseFlightTicket]