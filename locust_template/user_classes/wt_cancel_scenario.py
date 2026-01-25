from locust import task, SequentialTaskSet, HttpUser, constant_pacing, events, FastHttpUser
from config.config import cfg, logger
import re
import random
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_file, open_random_csv_file, generate_flight_dates, \
    process_cancel_request_body


class Cancel(SequentialTaskSet):
    headers_all = {
        'content-type': 'application/x-www-form-urlencoded',
    }

    def on_start(self):
        self.user_data_csv_file = './test_data/user_data.csv'
        self.flight_details_csv_file = './test_data/flight_details.csv'
        self.users_data = open_csv_file(self.user_data_csv_file)
        self.user_data = open_random_csv_file(self.flight_details_csv_file)
        self.random_users_data = open_random_csv_file(self.user_data_csv_file)
        self.random_flight_details = open_random_csv_file(self.flight_details_csv_file)

        logger.info(f'______FLIGHT_DETAILS_OPEN_CSV:{self.random_flight_details}')

        @task()
        def uc_00_getHomePage(self):
            r00_01_response = self.client.get(
                '/WebTours/',
                name="r00_01_response",
                allow_redirects=False,
                headers={
                    'sec-ch-ua': '"Chromium";v="142", "YaBrowser";v="25.12", "Not_A Brand";v="99", "Yowser";v="2.5"',
                    'sec-ch-ua-mobile': '?0'
                },
                # debug_stream=sys.stderr
            )

            with self.client.get(
                    '/WebTours/header.html',
                    name="r00_02_header_html",
                    allow_redirects=False,
                    catch_response=True
                    # debug_stream=sys.stderr
            ) as r00_02_header_html:
                check_http_response(r00_02_header_html, 'images/webtours.png')

            check = 'Web Tours'
            with self.client.get(
                    '/cgi-bin/welcome.pl?signOff=true',
                    name="r00_03_welcome_pl",
                    allow_redirects=False,
                    catch_response=True
                    # debug_stream=sys.stderr
            ) as r00_03_welcome_pl:
                check_http_response(r00_03_welcome_pl, f'{check}')

            with self.client.get(
                    '/cgi-bin/nav.pl?in=home',
                    name="r00_04_nav_pl",
                    allow_redirects=False,
                    catch_response=True
                    # debug_stream=sys.stderr
            ) as r00_04_nav_pl:
                check_http_response(r00_04_nav_pl, 'Web Tours Navigation Bar')

            with self.client.get(
                    '/WebTours/home.html',
                    name="r00_05_home_html",
                    allow_redirects=False,
                    catch_response=True
                    # debug_stream=sys.stderr
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
            self.headers = {'content-type': 'application/x-www-form-urlencoded'}

            self.body_r_01_login_pl = (
                f"userSession={self.user_session}"
                f"&username={self.login}"
                f"&password={self.password}"
                f"&login.x=0"
                f"&login.y=0"
                f"&JSFormSubmit=off"
            )

            print(f"_____BODY LOGIN: {self.body_r_01_login_pl}")
            logger.info(f"_____BODY LOGIN: {self.body_r_01_login_pl}")

            with self.client.post(
                    '/cgi-bin/login.pl',
                    name="r01_01_login_pl",
                    allow_redirects=False,
                    catch_response=True,
                    headers=self.headers,
                    data=self.body_r_01_login_pl
                    # debug_stream=sys.stderr
            ) as r01_01_login_pl:
                check_http_response(r01_01_login_pl, 'Welcome to the Web Tours site.')

        uc_00_getHomePage(self)
        uc_01_Login(self)

    @task()
    def uc_06_itinerary(self):
        with self.client.get(
                '/cgi-bin/welcome.pl?page=itinerary',
                name="r06_01_welcome.pl?page=itinerary'",
                allow_redirects=False,
                catch_response=True
                # debug_stream=sys.stderr
        ) as r06_01_welcome_pl_page_itinerary:
            check_http_response(r06_01_welcome_pl_page_itinerary, "Web Tours")

            with self.client.get(
                    '/cgi-bin/nav.pl?page=menu&in=itinerary',
                    name="r06_02_nav_pl_page_menu_in_itinerary",
                    allow_redirects=False,
                    catch_response=True
            ) as r06_02_nav_pl_page_menu_in_itinerary:
                check_http_response(r06_02_nav_pl_page_menu_in_itinerary, "Web Tours Navigation Bar")

            with self.client.get(
                    '/cgi-bin/itinerary.pl',
                    name="r06_03_itinerary_pl",
                    allow_redirects=False,
                    catch_response=True
            ) as r06_03_itinerary_pl:
                check_http_response(r06_03_itinerary_pl, "Flights List")

                self.flight_ids = re.findall(r'<input type="hidden" name="flightID" value="([^"]*)"\s*/>',
                                             r06_03_itinerary_pl.text)
                self.cgifields_values = re.findall(r'<input type="hidden" name=".cgifields" value="([^"]*)"\s*/>',
                                                   r06_03_itinerary_pl.text)

                logger.info(f"_______Flight IDS: {self.flight_ids}")
                logger.info(f"_______Flight Values: {self.cgifields_values}")

    @task()
    def uc_07_DeleteOneTicket(self):
        if self.flight_ids:
            data_r_07_01 = process_cancel_request_body(self.flight_ids, self.cgifields_values)
            with self.client.post(
                    '/cgi-bin/itinerary.pl',
                    name="r07_01_delete_flight_itinerary_pl",
                    headers=self.headers_all,
                    data=data_r_07_01,
                    catch_response=True
            ) as r07_01_delete_itinerary_pl:
                check_http_response(r07_01_delete_itinerary_pl, "Flights List")

        else:
            logger.info(f"NO TICKETS FOR USERS {self.login}")

class WebToursCancelUserClass(FastHttpUser):
    wait_time = constant_pacing(cfg.webtours_cancel.pacing)
    host = cfg.url
    tasks = [Cancel]
