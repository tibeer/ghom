import os
import sys
import yaml

from github import Github
from loguru import logger


logger.remove()
logger_format = (
    "<black>{time:YYYY-MM-DD HH:mm:ss.SSS}</black> | "
    "<level>{extra[action]: <6}</level> | "
    "<cyan>{extra[compartment]: <17}</cyan> | "
    "<level>{message}</level>"
)
logger.configure(extra={"action": "INFO", "compartment": "main"})
logger.add(sys.stdout, format=logger_format)


def get_config(ghom_config):
    with open(ghom_config) as stream:
        try:
            config = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
    return config


class Conf:
    # start with 2 as get_organization() and get_rate_limit()
    # a few lines further are also api calls
    rate_counter = 1
    dry_run = os.getenv("INPUT_GHOM_DRY", "False") == "True"
    token = os.getenv("INPUT_GHOM_TOKEN")
    ghom_config = os.getenv("INPUT_GHOM_CONFIG", "ghom.yaml")
    org = os.getenv("GITHUB_REPOSITORY_OWNER")

    config = get_config(ghom_config)
    ghom_logger = logger.bind()
    gh_handle = Github(login_or_token=token)

    # print start message
    # get_rate_limit() does not increase the used api requests for an
    # unknown reason. if you perform a "gh api rate_limit" it does though
    old_limit = gh_handle.get_rate_limit().core
    ghom_logger.info(f"ghom started with {old_limit.remaining} of {old_limit.limit} api calls left")
    if dry_run:
        ghom_logger.info("ghom dry-run mode is active")

    org_handle = gh_handle.get_organization(org)

    def increase_rate_counter(self, amount=1):
        self.rate_counter = self.rate_counter + amount

    def set_log_compartment(self, compartment):
        self.ghom_logger = self.ghom_logger.bind(compartment=compartment)

    def set_log_action(self, action):
        self.ghom_logger = self.ghom_logger.bind(action=action)

    def log_generic(self, message):
        self.set_log_action("INFO")
        self.ghom_logger.info(f"{message}")

    def log_addition(self, message):
        self.set_log_action("ADD")
        self.ghom_logger.success(f"{message}")

    def log_change(self, message):
        self.set_log_action("CHANGE")
        self.ghom_logger.warning(f"{message}")

    def log_deletion(self, message):
        self.set_log_action("DELETE")
        self.ghom_logger.error(f"{message}")

    def log_critical(self, message):
        self.set_log_action("ERROR")
        self.ghom_logger.error(f"{message}")

    def print_end_message(self):
        # get_rate_limit() does not increase the used api requests for an
        # unknown reason. if you perform a "gh api rate_limit" it does though
        new_limit = self.gh_handle.get_rate_limit().core
        self.set_log_compartment("main")
        self.log_generic(f"ghom calculated a total of {self.rate_counter} api calls (this can be incorrect)")
        # new_limit.remaining needs to be decreased by one as the get() is also a request
        self.log_generic(f"ghom actually used {self.old_limit.remaining - new_limit.remaining} api calls")
        self.log_generic(f"ghom ended with {new_limit.remaining} of {new_limit.limit} api calls left")
