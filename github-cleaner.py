#!/usr/bin/env python3
# # Based upon https://github.com/PyGithub/PyGithub
# # Setup API key from Settings > Developer > Personal Access Token
# #   Remember to give Repo and Delete access
# #   Save it in mycanvas.ini as "github_key" in [api]
import os
import sys
import logging
import argparse
import configparser
from github import Github

# http://stackoverflow.com/questions/8299270/ultimate-answer-to-relative-python-imports
# relative imports do not work when we run this module directly
PACK_DIR = os.path.dirname(os.path.join(os.getcwd(), __file__))
ADDTOPATH = os.path.normpath(os.path.join(PACK_DIR, '..'))
# add more .. depending upon levels deep
sys.path.append(ADDTOPATH)

SCRIPTPATH = os.path.dirname(os.path.realpath(__file__))
DEVNULL = open(os.devnull, 'wb')

class GitHubCleaner(object):
    """ SEtup a reasonable environment to delete repos using Github API"""
    scriptpath = SCRIPTPATH
    logfd = None
    log = logging.getLogger("githubcleaner")

    def __init__(self, args):
        """Find configuration files with the api"""
        self.args = args
        # setup logger
        logpath = 'github-cleaner.log'
        floglevel = logging.DEBUG
        cloglevel = logging.INFO
        self.log.setLevel(floglevel)
        self.log.addHandler(logging.FileHandler(logpath))
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(cloglevel)
        self.log.addHandler(console_handler)
        self.log.info("Logging to %s", logpath)
        self.log.debug("File logging set at %s", floglevel)
        self.log.debug("Console logging level at %s", cloglevel)

        # setup the config file
        configpaths = [args.configfile, "./github-cleaner.ini", "~/.github-cleaner.ini"]
        cp = configparser.ConfigParser()
        configfile = None
        def checkfile(filepath):
            return os.path.isfile(filepath) and os.access(filepath, os.R_OK)
        for configpath in configpaths:
            self.log.debug("Looking for config file in %s", configpath)
            if configpath is None:
                continue
            configpath = os.path.expanduser(configpath)  #deal with ~
            if not checkfile(configpath):
                continue
            configfile = cp.read([configpath])
            self.log.info("Using configuration file at %s", configpath)
            break

        if configfile is None:
            self.log.error("Error:  Couldn't find a configuration file.")
            sys.exit()

        def config2dict(section):
            """convert a parsed configuration into a dict for storage"""
            config = {setarg: setval for setarg, setval
                  in cp.items(section)}
            for setarg, setval in config.items():
                self.log.debug('setting: %s = %s', setarg, setval)
            return config
        config = {}
        for section in ['api', 'courses']:
            config[section] = config2dict(section)
        self.config = config
        self.configfile = configfile

### Parsing our arguments
PARSER = argparse.ArgumentParser(
    description='GitHub Repository Cleaner')
PARSER.add_argument('--version', action="version", version="%(prog)s 0.1")  #version init was depricated
PARSER.add_argument('repofilter',#required!
                    help='Match criteria for repos')
PARSER.add_argument('-c', '--configfile',
                    help='configuration file location (override)')
PARSER.add_argument('-O', '--organization', 
                    help='What organization to find repos from')

ARGS = PARSER.parse_args()
GHC = GitHubCleaner(ARGS)

# First create a Github instance:
# using an access token
g = Github(GHC.config["api"]["github_key"])

# # Github Enterprise with custom hostname
# g = Github(base_url="https://{hostname}/api/v3", login_or_token="access_token")

repositories = set()
# Then play with your Github objects:
#
print(f"Searching for repo to meet filter: {ARGS.repofilter}")
if ARGS.organization:
    print(f"Searching organization:  {ARGS.organization}")
    for repo in g.get_organization(ARGS.organization).get_repos():
        repositories.add(repo.name)

else:
    for repo in g.get_user().get_repos():   
        repositories.add(repo.name)
        #print(repo.name)



# # Note: Gets rate limited and fails if too many hits
# content_files = g.search_code(query=ARGS.repofilter)
# for content in content_files:
#     repositories.add(content.repository.full_name)
#     rate_limit = g.get_rate_limit()
#     if rate_limit.search.remaining == 0:
#         print('WARNING: Rate limit on searching was reached.  Results are incomplete.')
#         break
 
for repo in sorted(repositories):
    print(repo)
