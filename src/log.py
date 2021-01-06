import logging

logging.basicConfig(filename='error.log', format='[%(levelname)s]-%(asctime)s : %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


class DiscordLog:

    @staticmethod
    def Spam(user, nameCommand):
        print("spam")
        logging.warning(f"{user} is spamming {nameCommand}")
