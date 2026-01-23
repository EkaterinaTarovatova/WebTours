from locust import task, SequentialTaskSet, HttpUser, constant_pacing, events, FastHttpUser
from config.config import cfg, logger
import sys
import re
import random
from datetime import datetime, timedelta
from utils.assertion import check_http_response
from utils.non_test_methods import open_csv_file, open_random_csv_file, generate_flight_dates
from urllib.parse import quote_plus
import html


class PurchaseFlightTicket(SequentialTaskSet):

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

    @task()
    def uc_02_Check_Flights(self):
        if not hasattr(self, 'user_session'):
            self.interrupt(msg="No user_session available")

        with self.client.get(
                '/cgi-bin/welcome.pl?page=search',
                name="r02_01_welcome_pl",
                allow_redirects=False,
                catch_response=True,
                # debug_stream=sys.stderr
        ) as r02_01_welcome_pl:
            check_http_response(r02_01_welcome_pl, 'Web Tours')

        with self.client.get(
                '/cgi-bin/nav.pl?page=menu&in=flights',
                name="r02_02_menu_flights",
                allow_redirects=False,
                catch_response=True
                # debug_stream=sys.stderr
        ) as r02_02_menu_flights:
            check_http_response(r02_02_menu_flights, 'Web Tours Navigation Bar')

        with self.client.get(
                '/cgi-bin/reservations.pl?page=welcome',
                name="r02_03_welcome",
                allow_redirects=False,
                catch_response=True,
                # debug_stream=sys.stderr
        ) as r02_03_welcome:
            check_http_response(r02_03_welcome, 'Flight Selections')

    @task()
    def uc_03_FindFlights(self):
        self.random_flights_row = random.choice(self.random_flight_details)
        logger.info(f"_____FLIGHTS_ROW: {self.random_flights_row}")
        self.depart = self.random_users_row["depart"]
        self.arrive = self.random_users_row["arrive"]
        self.seatType = self.random_flights_row["seat_type"]
        self.seatPref = self.random_flights_row["seat_pref"]

        self.dates_dict = generate_flight_dates()
        logger.info(f"_____DATES_DICT: {self.dates_dict}")
        self.depart_date = self.dates_dict["depart_date"]
        self.return_date = self.dates_dict["return_date"]

        data_r03_01 = (
            f"advanceDiscount=0"
            f"&depart={self.depart}"
            f"&departDate={self.depart_date}"
            f"&arrive={self.arrive}"
            f"&returnDate={self.return_date}"
            f"&numPassengers=1"
            f"&seatPref={self.seatPref}"
            f"&seatType={self.seatType}"
            f"&findFlights.x=74"
            f"&findFlights.y=10"
            f"&.cgifields=roundtrip"
            f"&.cgifields=seatType"
            f"&.cgifields=seatPref"
        )

        logger.info(f"_____DATA_R03_01: {data_r03_01}")

        with self.client.post(
                '/cgi-bin/reservations.pl',
                name="r03_01_reservations",
                allow_redirects=False,
                catch_response=True,
                data=data_r03_01,
                headers=self.headers,
                # debug_stream=sys.stderr
        ) as r03_01_reservations:
            check_http_response(r03_01_reservations, 'Flight Selections')

        self.dict_outboundFlight = re.findall(
            r'<input type="radio" name="outboundFlight" value="([^"]*)"',
            r03_01_reservations.text
        )
        logger.info(f"_____DICT_OUTBOUNDFLIGHT: {self.dict_outboundFlight}")

    @task()
    def uc_04_ChooseFlightOptions(self):
        self.random_flights_row = random.choice(self.random_flight_details)
        self.seatType = self.random_flights_row["seat_type"]
        self.seatPref = self.random_flights_row["seat_pref"]
        self.outboundFlight = quote_plus(random.choice(self.dict_outboundFlight))

        logger.info(f"_____DATES_DICT: {self.dates_dict}")

        self.depart_date = self.dates_dict["depart_date"]
        self.return_date = self.dates_dict["return_date"]

        data_r04_01 = f'outboundFlight={self.outboundFlight}&numPassengers=1&advanceDiscount=0&seatType={self.seatType}&seatPref={self.seatPref}&reserveFlights.x=65&reserveFlights.y=18'
        logger.info(f"_____DATA_R04_01: {data_r04_01}")

        with self.client.post(
                '/cgi-bin/reservations.pl',
                name="r04_01_reservations_pl",
                allow_redirects=False,
                catch_response=True,
                data=data_r04_01,
                headers=self.headers,
                debug_stream=sys.stderr
        ) as r04_01_reservations_pl:
            check_http_response(r04_01_reservations_pl, 'Flight Reservation')

        text = r04_01_reservations_pl.text

        first_name_match = re.search(r'name="firstName" value="([^"]*)"', text)
        self.firstName = html.unescape(first_name_match.group(1)).strip() if first_name_match else ""

        last_name_match = re.search(r'name="lastName" value="([^"]*)"', text)
        self.lastName = html.unescape(last_name_match.group(1)).strip() if last_name_match else ""

        pass1_match = re.search(r'name="pass1" value="([^"]*)"', text)
        self.pass1 = html.unescape(pass1_match.group(1)).strip() if pass1_match else ""

    @task()
    def uc_05_PaymentFlight(self):

        cities = [
            "New York NY", "Los Angeles CA", "Chicago IL", "Houston TX",
            "Phoenix AZ", "Philadelphia PA", "San Antonio TX", "San Diego CA"
        ]
        street_names = ["Oak", "Maple", "Pine", "Cedar", "Elm", "Main", "Park", "Washington"]

        address1 = f"{random.randint(100, 999)} {random.choice(street_names)} Ave"
        address2 = f"{random.choice(cities)} {random.randint(10000, 99999)}"

        test_cards = ["424242424242", "555555555555", "400005665566"]
        creditCard = random.choice(test_cards)
        expDate = ""

        data_r05_01 = (
            f"firstName={self.firstName}"
            f"&lastName={self.lastName}"
            f"&address1={address1}"
            f"&address2={address2}"
            f"&pass1={quote_plus(self.pass1)}"
            f"&creditCard={creditCard}"
            f"&expDate={expDate}"
            f"&oldCCOption="
            f"&numPassengers=1"
            
            f"&seatType=Coach"
            f"&seatPref=None"
            f"&outboundFlight={self.outboundFlight}"
            f"&advanceDiscount=0"
            f"&returnFlight="
            f"&JSFormSubmit=off"
            f"&buyFlights.x=76"
            f"&buyFlights.y=4"
            f"&.cgifields=saveCC"
        )

        logger.info(f"_____DATA_R05_01: {data_r05_01}")

        with self.client.post(
                '/cgi-bin/reservations.pl',
                name="r05_01_reservations_pl",
                allow_redirects=False,
                catch_response=True,
                data=data_r05_01,
                headers=self.headers,
                debug_stream=sys.stderr
        ) as r05_01_reservations_pl:
            check_http_response(r05_01_reservations_pl, 'Thank you for booking through Web Tours.')


class WebToursBaseUserClass(FastHttpUser):
    wait_time = constant_pacing(cfg.pacing)
    host = cfg.url
    tasks = [PurchaseFlightTicket]
