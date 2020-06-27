import os
import re
import time
import shutil
import requests
import settings
import progressbar

from typing import Dict, List, NoReturn

reg_ex = r'[\w-]+.(jpg|png|txt)'


class VKSmallWrapper:

    def __init__(self, token: int, group_id: int):
        '''
        :param token: VK Token
        :param group_id: Group id
        '''
        if not token:
            raise ValueError('No token specified')

        self.group_id = group_id
        self.version = "5.80"
        self.token = token
        self.api_url = f"https://api.vk.com/method/{{}}?access_token={self.token}&v={self.version}"


    def execute_api(self, method: str, params: Dict):
        try:
            result = requests.get(self.api_url.format(method), params=params).json()
            return result
        except:
            raise ValueError('Response is not correct')


def number_of_group(count: int) -> List:
    count_posts = []
    max_value_post = 100  # Максимальное кол-во постов
    offset = 0  # Отступ

    while count != 0:
        if count >= max_value_post:
            count_posts.append([max_value_post, offset])
            offset += max_value_post
            count -= max_value_post
        else:
            count_posts.append([count, offset])
            count -= count
    return count_posts


def download_images(name: str, links: List) -> NoReturn:
    print(f"Start downloading {len(links)} images.")

    bar = progressbar.ProgressBar(maxval=len(links), widgets=[
        f'Downloading {len(links)} images: ',
        progressbar.Bar(marker='#', left='[', right=']', fill='.'),
        progressbar.Percentage(),
    ]).start()

    if not os.path.exists(f"output/"):
        os.makedirs(f"output/")

    l = 0
    for link in links:
        l += 1
        bar.update(l)
        result = re.search(reg_ex, link)
        if result:
            g = result.group(0)
        else:
            continue

        img_bytes = requests.get(link, stream=True)
        try:
            if not os.path.exists(f"output/group_id_{name}/"):
                os.makedirs(f"output/group_id_{name}")

            with open(f"output/group_id_{name}/{g}", 'wb') as f:
                img_bytes.raw.decode_content = True
                shutil.copyfileobj(img_bytes.raw, f)
        except Exception as e:
            print(f"ERROR: {e}")

    bar.finish()


def parse_images_from_post(posts) -> List:
    links = []
    for post in posts['response']['items']:
        if not post.get("attachments", None):
            continue
        for att in post['attachments']:
            if not att['type'] == "photo":
                continue

            if "sizes" in att['photo']:
                m_s_ind = -1
                m_s_wid = 0

                for i, size in enumerate(att['photo']["sizes"]):
                    if size["width"] > m_s_wid:
                        m_s_wid = size["width"]
                        m_s_ind = i

                link = att['photo']["sizes"][m_s_ind]["url"]
                links.append(link)
            elif "url" in att['photo']:
                link = att['photo']['url']
                links.append(link)

    return links


def get_links(vk_api, count: int, offset=None) -> List:
    counts = number_of_group(count)
    links = []

    for count in counts:
        params = {
            'owner_id': vk_api.group_id * -1,  # ID владельца(отрицательно для групп)
            'count': count[0],
            'filter': 'owner'
        }
        if offset:
            params['offset'] = offset + count[1]
        else:
            params['offset'] = count[1]

        res = vk_api.execute_api("wall.get", params)
        l = parse_images_from_post(res)
        for li in l:
            links.append(li)

        time.sleep(5)

    return links


def main():
    try:
        v = settings.token
        del v
    except:
        raise ValueError('Token is not specified')

    group_id = input("Enter group id: ")

    if not group_id:
        print("Group id is not presented")
        exit()
    elif not group_id.isdigit():
        raise ValueError("Group id is not integer")
    else:
        group_id = int(group_id)

    offset = input("Enter offset is need? (Just enter if not needed): ")
    if offset and not offset.isdigit():
        raise ValueError("Offset is not integer")
    elif offset:
        offset = int(offset)

    count = input("Enter count of posts with images parse: ")
    if not count:
        print("Count is not presented")
        exit()
    elif not count.isdigit():
        raise ValueError("Count is not integer")
    else:
        count = int(count)

    vk_api = VKSmallWrapper(settings.token, group_id)
    links = get_links(vk_api, count, offset)

    download_images(str(vk_api.group_id), links)


if __name__ == '__main__':
    main()
