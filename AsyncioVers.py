import asyncio
import json
import os
import sys
import time
from datetime import datetime

import aiofiles
import aiohttp

from Interface import Downloader
from bcolols import bcolors


class AsyncRedditDownloader(Downloader):

    def __init__(self):
        self.data = None
        self.client_wait_time = None
        self.data_path = None

    def init_downloader(self, subreddits):
        cwd_path = os.getcwd()
        self.data_path = os.path.join(cwd_path, 'AsyncRedditDownloader')
        os.mkdir(self.data_path)
        self.client_wait_time = len(subreddits) * 3

    async def get_data(self, subreddit, session):
        api = 'https://api.pushshift.io/reddit/comment/search/'
        params = {'sort': 'asc',
                  'sort_type': 'created_utc',
                  'size': 3,
                  'subreddit': subreddit}

        start_time = time.time()
        while True:
            async with session.get(api, params=params) as resp:
                status = resp.status
                if status // 100 != 2:
                    print(f'{bcolors.FAIL}{status}{bcolors.ENDC}: {bcolors.BOLD}{subreddit}{bcolors.ENDC}')
                    await asyncio.sleep(1)
                    continue
                if time.time() - start_time > self.client_wait_time:
                    print(f'{bcolors.FAIL}Server do not response{bcolors.ENDC}')
                    break
                self.data = await resp.json()
                break

        if not self.data:
            print(f'{bcolors.WARNING}Empty data{bcolors.ENDC}')
        else:
            self.edit_data()
            await self.save_data(subreddit, status)

    def edit_data(self):
        for profile in self.data['data']:
            for profile_param in list(profile.keys()):
                if profile_param == 'created_utc':
                    profile[profile_param] = datetime.fromtimestamp(profile[profile_param]).strftime(
                        '%Y-%m-%d %H:%M:%S')

                if profile_param not in ['body', 'created_utc', 'author']:
                    del profile[profile_param]

    async def save_data(self, subreddit, status):

        file_path = os.path.join(self.data_path, f'{subreddit}.txt')
        async with aiofiles.open(file_path, 'w') as f:
            await f.write(json.dumps(self.data, indent=2))
            print(
                f'{bcolors.OKGREEN}{status}{bcolors.ENDC}: {bcolors.BOLD}{subreddit}{bcolors.ENDC} successfully downloaded')

    async def gather(self, subreddits):
        async with aiohttp.ClientSession() as session:
            tasks = []
            for subreddit in subreddits:
                task = self.get_data(subreddit, session)
                tasks.append(task)
            try:
                await asyncio.gather(*tasks)
            except Exception:
                print(sys.exc_info())

    def launch(self, subreddits):
        self.init_downloader(subreddits)
        if sys.platform:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.gather(subreddits))


if __name__ == '__main__':
    working_dir = os.getcwd()
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
    if sys.platform:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    downl = AsyncRedditDownloader()
    downl.launch(subreddits)
    duration = time.time() - time_start
    print(f'{bcolors.OKCYAN}Process time: {duration} sec{bcolors.ENDC}')
