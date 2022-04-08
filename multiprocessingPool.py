import time
import requests
import json
from datetime import datetime
import multiprocessing
import os

from Interface import Downloader
from bcolols import bcolors

session: requests.Session = None
client_wait_time = 0
data_dir_path = ''


class MultiprocessRedditDownloader(Downloader):
    @staticmethod
    def init_process(waiting_time, path):
        global session, client_wait_time, data_dir_path
        if not session:
            session = requests.session()
        client_wait_time = waiting_time
        data_dir_path = path

    @staticmethod
    def worker(subreddit):
        api = 'https://api.pushshift.io/reddit/comment/search/'
        params = {'sort': 'asc',
                  'sort_type': 'created_utc',
                  'size': 3,
                  'subreddit': subreddit}

        process_name = multiprocessing.current_process().name
        data = None
        start_time = time.time()

        while True:
            with session.get(api, params=params) as resp:
                status = resp.status_code
                if status // 100 != 2:
                    print(f'{bcolors.FAIL}{status}{bcolors.ENDC}: {bcolors.BOLD}{subreddit}{bcolors.ENDC}, process: {process_name}')
                    time.sleep(1)
                    continue

                if time.time() - start_time > client_wait_time:
                    print(f'{bcolors.FAIL}Server do not response{bcolors.ENDC}')
                    break
                data = resp.json()
                break

        if 'data' not in data:
            print(f'{bcolors.WARNING}Empty data{bcolors.ENDC}')
        else:
            for profile in data['data']:
                for profile_param in list(profile.keys()):
                    if profile_param == 'created_utc':
                        profile[profile_param] = datetime.fromtimestamp(profile[profile_param]).strftime('%Y-%m-%d %H:%M:%S')

                    if profile_param not in ['body', 'created_utc', 'author']:
                        del profile[profile_param]
            file_path = os.path.join(data_dir_path, f'{subreddit}.txt')
            with open(f'{file_path}', 'w') as f:
                json.dump(data, f, indent=2)
                print(f'{bcolors.OKGREEN}{status}{bcolors.ENDC}: {bcolors.BOLD}{subreddit}{bcolors.ENDC} successfully downloaded. {process_name}')

    def launch(self, subreddits):
        waiting_time = len(subreddits) * 3
        data_path = os.path.join(os.getcwd(), 'MultiprocessRedditDownloader')
        os.mkdir(data_path)
        with multiprocessing.Pool(initializer=MultiprocessRedditDownloader.init_process, initargs=(waiting_time, data_path)) as pool:
            pool.map(MultiprocessRedditDownloader.worker, subreddits)


if __name__ == '__main__':
    with open('subreddits.txt', 'r') as file:
        content = file.read()
        subreddits = content.splitlines()
    if subreddits:
        cwd_path = os.getcwd()
        curr_time = datetime.now().strftime("%d.%m %H.%M.%S")
        working_dir = os.path.join(cwd_path, curr_time)
        os.mkdir(working_dir)
        os.chdir(working_dir)

    time_start = time.time()
    downl = MultiprocessRedditDownloader()
    downl.launch(subreddits)
    duration = time.time() - time_start
    print(f'{bcolors.OKCYAN}Process time: {duration} sec{bcolors.ENDC}')

