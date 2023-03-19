import json


def get_channels(key):
    with open("settings/channels.json") as f:
        data = json.load(f)[key]
        return data

def set_channels(task, channel):
    prev_data = get_channels('channels')
    data = []
    if task == 'delete_channel':
        data = delete_channels(data=prev_data, channel=channel)
    if task == 'add_channel':
        data = add_channels(data=prev_data, channel=channel)
    dict_json = {'channels': data}
    if data:
        with open("settings/channels.json", "w") as f:
            json.dump(dict_json, f)
        return True
    else:
        return False


def add_channels(data, channel):
    for item in data:
        if item['id'] == channel['id']:
            return False
    data.append({'id': channel['id'], 'name': channel['name'], 'link': channel['link']})
    return data


def delete_channels(data, channel):
    index = search_value(data, channel)
    print(index)
    if index > -1:
        data.pop(index)
        return data
    return False


def search_value(data, target):
    for index, channel in enumerate(data):
        for key, value in channel.items():
            if value == target['link']:
                return index
    return False
