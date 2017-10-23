# -*- coding: utf-8 -*-
from telegram.ext import Updater, MessageHandler, Filters
from settings import api_token, logLevel
import sys
import logging
import re
from libs.daemonize import Daemon
from libs.setLogger import setLogger


log = setLogger('Daneel.log', logLevel)

def delete_method(bot, update):
    if not update.message.text:
        log.debug("It does not contain text")
        return

    log.debug("It contains text: %s" % update.message.text)
    mlist=[r'^[0x][0-9A-Za-z]{40,42}$', r'^[13][a-km-zA-HJ-NP-Z1-9]{25,34}$', ]

    for i in mlist:
        if re.search(i, update.message.text):
            log.info("Detected blacklisted expression!")
            update.message.reply_text('SCAM ATTEMPT DETECTED! Message deleted')
            deleted = bot.delete_message(chat_id=update.message.chat_id, message_id=update.message.message_id)
            if not deleted:
                log.error("DONT DELETED")
            else:
                log.info("MESSAGE DELETED")

def run_bot():
    updater = Updater(token=api_token)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(MessageHandler(Filters.all, delete_method))

    updater.start_polling()

    updater.idle()

class DaneelDaemon(Daemon):
    def run(self):
        log.info('Daneel initialized')
        run_bot()

if __name__ == "__main__":
    daemon = DaneelDaemon(
        pidfile='/tmp/daneel.pid',
        stdout='/tmp/daneel.log',
        stderr='/tmp/daneel.error',
    )
    if len(sys.argv) > 1:
        if 'start' == sys.argv[1]:
            daemon.start()
        elif 'stop' == sys.argv[1]:
            daemon.stop()
        elif 'restart' == sys.argv[1]:
            daemon.restart()
        else:
            print "Unknown command"
            sys.exit(2)
        sys.exit(0)
    else:
        print "usage: %s start|stop|restart" % sys.argv[0]
        sys.exit(2)
