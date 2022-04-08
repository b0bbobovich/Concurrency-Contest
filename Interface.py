import abc


class Downloader:

    @abc.abstractmethod
    def launch(self, subreddits):
        pass
