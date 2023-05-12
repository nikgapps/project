from colorama import Fore


class P:
    @staticmethod
    def yellow(message):
        print(Fore.YELLOW + str(message) + Fore.RESET)

    @staticmethod
    def red(message):
        print(Fore.RED + str(message) + Fore.RESET)

    @staticmethod
    def green(message):
        print(Fore.GREEN + str(message) + Fore.RESET)

    @staticmethod
    def blue(message):
        print(Fore.BLUE + message + Fore.RESET)

    @staticmethod
    def magenta(message):
        print(Fore.MAGENTA + str(message) + Fore.RESET)
