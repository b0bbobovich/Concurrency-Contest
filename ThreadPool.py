import time
import requests
import json
import os
import threading
import concurrent.futures
from datetime import datetime

from Interface import Downloader
from bcolols import bcolors


class ThreadRedditDownloader(Downloader):
    def __init__(self):
        self.__thread_local = threading.local()
        self.data = None

    def __get_thread_local_session(self):
        if not hasattr(self.__thread_local, 'session'):
            self.__thread_local.session = requests.session()
        return self.__thread_local.session

    def __init_downloader(self, subreddits):
        self._waiting_time = len(subreddits) * 3
        self.data_dir_path = os.path.join(os.getcwd(), 'ThreadRedditDownloader')
        os.mkdir(self.data_dir_path)

    def __worker(self, subreddit):
        api = 'https://api.pushshift.io/reddit/comment/search/'
        params = {'sort': 'asc',
                  'sort_type': 'created_utc',
                  'size': 3,
                  'subreddit': subreddit}

        session = self.__get_thread_local_session()
        start_time = time.time()

        while True:
            with session.get(api, params=params) as resp:
                status = resp.status_code
                if status // 100 != 2:
                    print(
                        f'{bcolors.FAIL}{status}{bcolors.ENDC}: {bcolors.BOLD}{subreddit}{bcolors.ENDC}')
                    time.sleep(1)
                    continue

                if time.time() - start_time > self._waiting_time:
                    print(f'{bcolors.FAIL}Server do not response{bcolors.ENDC}')
                    break
                self.data = resp.json()
                break

        if not self.data:
            print('Empty data')
        else:
            self.edit_data()
            self.save_data(subreddit, status)

    def edit_data(self):
        for profile in self.data['data']:
            for profile_param in list(profile.keys()):
                if profile_param == 'created_utc':
                    profile[profile_param] = datetime.fromtimestamp(profile[profile_param]).strftime(
                        '%Y-%m-%d %H:%M:%S')

                if profile_param not in ['body', 'created_utc', 'author']:
                    del profile[profile_param]

    def save_data(self, subreddit, status):
        file_path = os.path.join(self.data_dir_path, f'{subreddit}.txt')
        with open(f'{file_path}', 'w') as f:
            json.dump(self.data, f, indent=2)
            print(
                f'{bcolors.OKGREEN}{status}{bcolors.ENDC}: {bcolors.BOLD}{subreddit}{bcolors.ENDC} successfully downloaded.')

    def launch(self, subreddits):
        self.__init_downloader(subreddits)
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(self.__worker, subreddits)


if __name__ == '__main__':
    with open('subreddits.txt', 'r') as file:
        content = file.read()
        subreddits = content.splitlines()

    if subreddits:
        cwd_path = os.getcwd()
        curr_time = datetime.now().strftime("%d.%m %H.%M.%S")
        dir_path = os.path.join(cwd_path, curr_time)
        os.mkdir(dir_path)
        os.chdir(dir_path)

    time_start = time.time()
    downl = ThreadRedditDownloader()
    downl.launch(subreddits)
    duration = time.time() - time_start
    print(f'{bcolors.OKCYAN}Process time: {duration} sec{bcolors.ENDC}')
