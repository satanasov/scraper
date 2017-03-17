import configparser

config = configparser.ConfigParser()
config.read('scrape.ini')

def configWrite():
    cfgfile = open("scrape.ini", 'w')
    config.write(cfgfile)