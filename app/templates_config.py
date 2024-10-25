from typing import Union
from fastapi.templating import Jinja2Templates
from datetime import datetime

def time_format(value: Union[datetime, str]):
    if isinstance(value, str):
        try:
            dt = datetime.fromisoformat(value)
            return dt.strftime("%H:%M")
        except:
            return value
    elif isinstance(value, datetime):
        return value.strftime("%H:%M")
    return value


templates = Jinja2Templates(directory="templates")
templates.env.filters["time_format"] = time_format
