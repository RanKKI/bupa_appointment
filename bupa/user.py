from dataclasses import dataclass


@dataclass
class UserInfo:
    hapID: str
    email: str
    firstName: str
    surname: str
    dob: str  # DD/MM/YYYY, i.e. 23/07/1999
