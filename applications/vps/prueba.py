from datetime import datetime

def active_buttons_time():
    today = datetime.now()
    date = datetime(2022,11,27,19,10,0)
    print(date.weekday())
    match date.weekday():
        case 4:
            if date.hour >= 15:
                return True
            else:
                return False
        case 5:
            return True
        case 6:
            if date.hour <= 18:
                return True
            else:
                return False
        case _:
            return False

print(active_buttons_time())
