from bot import bot
from subject import *
from search import *
from paginator import *
from admin import *

import os


TOKEN = os.environ.get('UNIMELB_HELPER_TOKEN')
bot.run(TOKEN)