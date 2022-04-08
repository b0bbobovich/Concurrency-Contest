import time
import os
from datetime import datetime

from AsyncioVers import AsyncRedditDownloader
from multiprocessingPool import MultiprocessRedditDownloader
from ThreadPool import ThreadRedditDownloader
from Interface import Downloader
from bcolols import bcolors


class ConcurrencyContest:
    def __init__(self, subreddits) -> None:
        self.subreddits = subreddits
        self.contest_participants = []
        self.contest_result = {}

    def add_downloader(self, participant: Downloader) -> None:
        if issubclass(type(participant), Downloader):
            self.contest_participants.append(participant)
        else:
            print(f'{type(participant).__name__} not downloader obj')

    def run(self) -> None:
        print("\u001b[31m[ 🏁 READY! STEADY! GO! 🏆 ]\u001b[0m")
        for participant in self.contest_participants:

            print(f'{bcolors.HEADER}{participant} starting{bcolors.ENDC}')
            time_start = time.time()

            participant.launch(self.subreddits)

            duration = time.time() - time_start
            self.contest_result[type(participant).__name__] = duration
            print(f'{bcolors.HEADER}{participant} finished{bcolors.ENDC}')

        for participant, result in self.contest_result.items():
            print(f'{bcolors.OKCYAN}{participant}{bcolors.ENDC}: finished with time {bcolors.OKBLUE}{result} sec{bcolors.ENDC}')

        sorted_participants_list = sorted(self.contest_result.items())
        winner, result = sorted_participants_list[0]
        print(f'{bcolors.WARNING}WE HAVE A CHAMPION!!!{bcolors.ENDC} - GOOD JOB {bcolors.OKCYAN}{winner}{bcolors.ENDC}. Your time - {bcolors.OKBLUE}{result}{bcolors.ENDC}')


if __name__ == "__main__":
    with open('subreddits.txt', 'r') as file:
        content = file.read()
        subreddits = content.splitlines()
    if subreddits:
        cwd_path = os.getcwd()
        curr_time = datetime.now().strftime("%d.%m %H.%M.%S")
        dir_path = os.path.join(cwd_path, curr_time)
        os.mkdir(dir_path)
        os.chdir(dir_path)

    contest = ConcurrencyContest(subreddits)
    contest.add_downloader(AsyncRedditDownloader())
    contest.add_downloader(MultiprocessRedditDownloader())
    contest.add_downloader(ThreadRedditDownloader())

    contest.run()
