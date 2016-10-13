import urllib2
import json
import base64
import ConfigParser

class termcolors:
  BOLD = '\033[1m'
  BLUE = '\033[1;94m'
  END = '\033[0m'


API_URL = "https://api.github.com"

config = ConfigParser.ConfigParser()
config.read('auth.cfg')

AUTH_USERNAME = config.get('auth', 'username')
AUTH_TOKEN = config.get('auth', 'token')

INDIVIDUALS_MENTIONED = config.get('pull_requests', 'individuals').split(',')
TEAMS_MENTIONED = config.get('pull_requests', 'teams').split(',')

def get_json(url):
  base64string = base64.encodestring('%s:%s' % (AUTH_USERNAME, AUTH_TOKEN)).replace('\n', '')

  request = urllib2.Request(url)
  request.add_header("Authorization", "Basic %s" % base64string)

  response = urllib2.urlopen(request)
  return json.load(response)

def pull_requests_mentioning_individual(username):
  individual_url = API_URL + '/search/issues?q=mentions:%s+state:open' % username
  return get_json(individual_url)['items']

def pull_requests_mentioning_team(team):
  team_url = API_URL + '/search/issues?q=team:%s+state:open' % team
  return get_json(team_url)['items']

def merge(dict, data):
  for item in data:
    dict[item['url']] = item

def fancy_terminal_text(text, color):
  return color + text + termcolors.END

by_url = {}

for individual in INDIVIDUALS_MENTIONED:
  merge(by_url, pull_requests_mentioning_individual(individual))
for team in TEAMS_MENTIONED:
  merge(by_url, pull_requests_mentioning_team(team))

values = sorted(by_url.values(), key=lambda item: item['created_at'], reverse=True)

print
for i, pull_request in enumerate(values):
  color = termcolors.BOLD if i % 2 == 0 else termcolors.BLUE
  line = '%s (%s) - %s' % (fancy_terminal_text(pull_request['title'], color), pull_request['user']['login'], pull_request['html_url'])
  for label in pull_request['labels']:
    line += ' (%s)' % label['name']
  print line
