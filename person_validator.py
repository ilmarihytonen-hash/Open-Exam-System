import emailvalidator
import configreader
import termcolor

from termcolor import colored
from configreader import config
from emailvalidator import check_email

check_info = config.get("check_info", True)
check_firstname = config.get("check_firstname", True)
check_secondname = config.get("check_secondname", True)
check_date_of_birth = config.get("check_day_of_birth", True)
check_valid_email = config.get("check_email", True)
if check_info:
    if check_firstname:
        try: 
            first_name = input("firstname please:")
        except Exception as e:
            print(colored("[Error]","red"),colored(f"{e}","white"))
    else:
        print(colored("[Debug]", "blue") + colored("Firstname checks disabled in config", "white"))

    if check_secondname:
        try:
            second_name = input("secondname please:")
        except Exception as e:
            print(colored("[Error]","red"),colored(f"{e}","white"))
    else:
        print(colored("[Debug]", "blue") + colored("Secondname checks disabled in config", "white"))

    if check_date_of_birth:
        try:
            time_of_birth = input("time of birth please:")
        except Exception as e:
            print(colored("[Error]","red"),colored(f"{e}","white"))
    else:
        print(colored("[Debug]", "blue") + colored("date of birth checks disabled in config", "white"))

    if check_valid_email:
        try:
            email = input("email please:")
        except Exception as e:
            print(colored("[Error]","red"),colored(f"{e}","white"))
    else:
        print(colored("[Debug]", "blue") + colored("Email checks disabled in config", "white"))

else:
    print(colored("[Debug]", "blue") + colored("Personel checks disabled in config", "white"))

valid_email = check_email(email)
