import json
import requests
from pprint import pprint
from tokens import vk_access_token
import time

VK_TOKEN = vk_access_token

""" Собрал статусы своих друзей в вк """


def parser_vk(method, silent=False, write_output=True, **params):

    url = f"https://api.vk.com/method/" + method
    response = requests.get(url, params=params)
    j_data = response.json()

    if write_output:
        prefix = params[list(params.keys())[0]]
        new_file_name = f"{method}_{str(prefix)}_vk.txt"

        with open(new_file_name, 'w+', encoding='utf-8') as f:
            json.dump(j_data, f, ensure_ascii=False)

    if not silent:
        pprint(j_data)
    return j_data


if __name__ == '__main__':

    params = {'user_id': 52381661,
              'v': 5.131,
              'access_token': VK_TOKEN}
    method_perm = 'account.getAppPermissions'
    method_friends = 'friends.get'
    method_status = 'status.get'

    # {'response': 1024} Означает, что моё приложение имеет доступ к статусам.
    parser_vk(method_perm, **params)

    the_greatest_ideas = []
    friends = parser_vk(method_friends, **params, silent=True)['response']['items']
    for friend in friends:
        time.sleep(0.4)
        try:

            res = parser_vk(method_status,
                            user_id=friend,
                            v=5.131,
                            access_token=VK_TOKEN,
                            write_output=False)['response']
            status_text = res['text']
            if status_text:
                the_greatest_ideas.append(status_text)

        except KeyError:
            print('Пользователь удалён')

        with open('the_greatest_ideas.txt', 'w', encoding='utf-8') as f:
            f.write('\n'.join([status.replace('\n', ' ') for status in the_greatest_ideas]))
