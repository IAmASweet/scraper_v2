import re
from settings.settings import get_config


def clean_up_text(arr_text):
    quote = eval(get_config(section='Default', key='quotes'))
    non_break_space = u'\xa0'
    arr_clean_text = []
    for text in arr_text:
        clean_text = text.replace(non_break_space, ' ')
        if quote:
            clean_text = clean_text.replace('"', '')
        clean_text = re.sub('[^\x00-\x7Fа-яА-Я]', "",
                            clean_text).strip()
        arr_clean_text.append(clean_text)
    return arr_clean_text


