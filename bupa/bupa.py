import datetime
import re

from bs4 import BeautifulSoup

from bupa.user import UserInfo
from bupa.utils import extract_form_data, make_request


def login(user: UserInfo):
    searchRoot, response = make_request(
        "https://bmvs.onlineappointmentscheduling.net.au/oasis/Search.aspx",
        method="GET",
    )

    data = extract_form_data(
        searchRoot,
        extra={
            "ctl00$ContentPlaceHolder1$txtHAPID": user.hapID,
            "ctl00$ContentPlaceHolder1$txtEmail": user.email,
            "ctl00$ContentPlaceHolder1$txtFirstName": user.firstName,
            "ctl00$ContentPlaceHolder1$txtSurname": user.surname,
            "ctl00$ContentPlaceHolder1$txtDOB": user.dob,
            "ctl00$ContentPlaceHolder1$btnSearch": "Search",
        },
    )

    root, response = make_request(
        "https://bmvs.onlineappointmentscheduling.net.au/oasis/Search.aspx",
        method="POST",
        data=data,
    )

    return root, response


def get_current_appointments(root: BeautifulSoup):
    rows = root.find_all("div", {"class": "appointments-row"})
    for row in rows:
        value = row.find("div", {"class": "fLeft"})
        try:
            # Monday, 22 January 2024 @ 08:30 AM
            date, time = value.text.split("@")
            date = datetime.datetime.strptime(date.strip(), "%A, %d %B %Y")
            time = datetime.datetime.strptime(time.strip(), "%I:%M %p")
            return date.replace(hour=time.hour, minute=time.minute)
        except ValueError:
            continue
    return None


def modify_appointment(root: BeautifulSoup, response):
    data = extract_form_data(
        root,
        keep=[
            "__VIEWSTATE",
            "__EVENTARGUMENT",
            "__EVENTVALIDATION",
            "__VIEWSTATEGENERATOR",
        ],
        extra={
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$repAppointments$ctl00$lnkChangeAppointment",
            "ctl00$ContentPlaceHolder1$hdnDeclinedPaymentReason": "",
            "ctl00$ContentPlaceHolder1$hidRefundOrTransfer": "",
        },
    )
    url = "https://bmvs.onlineappointmentscheduling.net.au/oasis/SearchResults.aspx"
    root, response = make_request(
        url,
        data=data,
        method="POST",
        headers={
            "Referer": response.url,
            "Origin": "https://bmvs.onlineappointmentscheduling.net.au",
        },
    )
    return root, response


def get_appointment_dates(html: str):
    content = html
    availableDates = re.findall(r"new Date\((?:(\d+),(\d+),(\d+))\)", content)
    appointments = []
    for year, month, day in availableDates:
        appointments.append(
            datetime.datetime(year=int(year), month=int(month) + 1, day=int(day))
        )

    return appointments


def fetch_appointments(root, response):
    data = extract_form_data(
        root,
        keep=[
            "__VIEWSTATE",
            "__EVENTARGUMENT",
            "__EVENTVALIDATION",
            "__VIEWSTATEGENERATOR",
        ],
        extra={
            "__EVENTTARGET": "ctl00$ContentPlaceHolder1$btnCont",
            "__EVENTARGUMENT": "",
            "ctl00$ContentPlaceHolder1$hdnChangeLocPartnerToBupa": "",
            "ctl00$ContentPlaceHolder1$hdnChangeLocBupaToPartner": "",
            "ctl00$ContentPlaceHolder1$SelectLocation1$txtSuburb": "",
            "ctl00$ContentPlaceHolder1$SelectLocation1$ddlState": "",
            "rbLocation": "135",
            "ctl00$ContentPlaceHolder1$SelectLocation1$hdnSearchCoord": "",
            "ctl00$ContentPlaceHolder1$hdnLocationID": "135",
        },
    )

    root, response = make_request(
        "https://bmvs.onlineappointmentscheduling.net.au/oasis/ModifyAppointment.aspx",
        method="POST",
        data=data,
        headers={
            "Referer": response.url,
            "Origin": "https://bmvs.onlineappointmentscheduling.net.au",
            "Content-Type": "application/x-www-form-urlencoded",
            "Sec-Fetch-Site": "same-origin",
        },
    )

    current_date = get_current_appointments(root)
    appointments = get_appointment_dates(response.text)
    return current_date, appointments

