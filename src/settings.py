import configparser

conf = configparser.ConfigParser()
conf.read('settings.ini')

marker_dpi = int(conf['marker']['dpi'])
marker_file_path = conf['marker']['file_path']

scan_dpi = int(conf['markSheet']['scan_dpi'])
margin_top = int(conf['markSheet']['margin_top'])
margin_bottom = int(conf['markSheet']['margin_bottom'])

threshold_start = int(conf['threshold']['start'])
threshold_stop = int(conf['threshold']['stop'])
threshold_step = int(conf['threshold']['step'])