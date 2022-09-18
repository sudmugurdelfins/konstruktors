from cmath import log
import requests
import json
import datetime
import time
import yaml
import logging
import logging.config
import yaml

from configparser import ConfigParser
from datetime import datetime
# Loading logging configuration
with open('./log_worker.yaml', 'r') as stream:
   log_config = yaml.safe_load(stream)

logging.config.dictConfig(log_config)
# Creating logger
logger = logging.getLogger('root')
logger.info('Asteroid processing service')

# Initiating and reading config values
logger.info('Loading configuration from file')

# Norāda api atslēgu un no kurienes velk datus.
try:
	config = ConfigParser()
	config.read('config.ini')

	nasa_api_key = config.get('nasa', 'api_key')
	nasa_api_url = config.get('nasa', 'api_url')
except:
	logger.exception('')
logger.info('DONE')

# Getting todays date
dt = datetime.now()
request_date = str(dt.year) + "-" + str(dt.month).zfill(2) + "-" + str(dt.day).zfill(2)  
logger.debug("Generated today's date: " + str(request_date))

#Pieprasa informāciju no NASA
logger.debug("Request url: " + str(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key))
r = requests.get(nasa_api_url + "rest/v1/feed?start_date=" + request_date + "&end_date=" + request_date + "&api_key=" + nasa_api_key)
#Atbilde pieprasijumam
logger.debug("Response status code: " + str(r.status_code))
logger.debug("Response headers: " + str(r.headers))
logger.debug("Response content: " + str(r.text))
#Pārbauda vai pieprasijums ir bijis veiksmīgs.
if r.status_code == 200:
#saņem visu json informaciju zem = json_data
	json_data = json.loads(r.text)
#izveido listu priekš safe un hazardous astriodiem
	ast_safe = []
	ast_hazardous = []
#pārbauda vai ir astriodi, ja ir, tads izvada daudzumu
	if 'element_count' in json_data:
		ast_count = int(json_data['element_count'])
		logger.info("Asteroid count today: " + str(ast_count))
#ja daudzums ir vairāk par 0
		if ast_count > 0:
			#parbauda katru rindu ar tuvajiem zemes objektiem pieprasijuma listē
			for val in json_data['near_earth_objects'][request_date]:
				#parbauda vai norādītas vērtības ir rindā kurai iet cauri
				if 'name' and 'nasa_jpl_url' and 'estimated_diameter' and 'is_potentially_hazardous_asteroid' and 'close_approach_data' in val:
					#uzstāda temporary vērtības
					tmp_ast_name = val['name']
					tmp_ast_nasa_jpl_url = val['nasa_jpl_url']
					#pārbauda vai ir kilometra vērtība , ja nav, izvada temp diameter vērtību kā -1
					if 'kilometers' in val['estimated_diameter']:
						#veic velvienu pārbaudi vai ir min un max estimated diametra vērtības, ja ir , apaļo min un max vērtības un uzstāda temporary vērtības noapaļotas līdz 3 decimālzīmem.
						if 'estimated_diameter_min' and 'estimated_diameter_max' in val['estimated_diameter']['kilometers']:
							tmp_ast_diam_min = round(val['estimated_diameter']['kilometers']['estimated_diameter_min'], 3)
							tmp_ast_diam_max = round(val['estimated_diameter']['kilometers']['estimated_diameter_max'], 3)
						#ja nav min un max vertības, temporary vertības ir -2
						else:
							tmp_ast_diam_min = -2
							tmp_ast_diam_max = -2
					else:
						tmp_ast_diam_min = -1
						tmp_ast_diam_max = -1
					#uzstāda ka ir hazardous astreoids, temp vertība
					tmp_ast_hazardous = val['is_potentially_hazardous_asteroid']
					#pārbauda vai ir close approach data
					if len(val['close_approach_data']) > 0:
						#parbauda vai ir nepieciesamas vertibas
						if 'epoch_date_close_approach' and 'relative_velocity' and 'miss_distance' in val['close_approach_data'][0]:
							tmp_ast_close_appr_ts = int(val['close_approach_data'][0]['epoch_date_close_approach']/1000)
							#uzstāda approach utc laiku
							tmp_ast_close_appr_dt_utc = datetime.utcfromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							#uzstada local approach laiku
							tmp_ast_close_appr_dt = datetime.fromtimestamp(tmp_ast_close_appr_ts).strftime('%Y-%m-%d %H:%M:%S')
							#parbauda vai ir prasita veriba
							if 'kilometers_per_hour' in val['close_approach_data'][0]['relative_velocity']:
								#apreķina astroida atrumu un pārvērs float vertibu pilnā skaitlī
								tmp_ast_speed = int(float(val['close_approach_data'][0]['relative_velocity']['kilometers_per_hour']))
							else:
								#ja nav kilometru vertibas noraditas, -1 ir atruma vertiba
								tmp_ast_speed = -1
							#ja ir kilometru vertiba close approuch rinda
							if 'kilometers' in val['close_approach_data'][0]['miss_distance']:
								#tiek atrasta miss distance, aprēķināta un noapaļota lidz 3 skaitļiem aiz komata.
								tmp_ast_miss_dist = round(float(val['close_approach_data'][0]['miss_distance']['kilometers']), 3)
							else:
								#ja nav, tad -1 ir vertiba
								tmp_ast_miss_dist = -1
						else:
							#uzstāda default vertibas ja nav atrasta close approach , relitave velocity, miss distance
							tmp_ast_close_appr_ts = -1
							tmp_ast_close_appr_dt_utc = "1969-12-31 23:59:59"
							tmp_ast_close_appr_dt = "1969-12-31 23:59:59"
					else:
						#uzstada default vertibas ja nav atrasta close approach data
						logger.debug("No close approach data in message")
						tmp_ast_close_appr_ts = 0
						tmp_ast_close_appr_dt_utc = "1970-01-01 00:00:00"
						tmp_ast_close_appr_dt = "1970-01-01 00:00:00"
						tmp_ast_speed = -1
						tmp_ast_miss_dist = -1
#izvada datus par astroidu
					logger.info("------------------------------------------------------- >>")
					logger.info("Asteroid name: " + str(tmp_ast_name) + " | INFO: " + str(tmp_ast_nasa_jpl_url) + " | Diameter: " + str(tmp_ast_diam_min) + " - " + str(tmp_ast_diam_max) + " km | Hazardous: " + str(tmp_ast_hazardous))
					logger.info("Close approach TS: " + str(tmp_ast_close_appr_ts) + " | Date/time UTC TZ: " + str(tmp_ast_close_appr_dt_utc) + " | Local TZ: " + str(tmp_ast_close_appr_dt))
					logger.info("Speed: " + str(tmp_ast_speed) + " km/h" + " | MISS distance: " + str(tmp_ast_miss_dist) + " km")
					
					# Adding asteroid data to the corresponding array
					#parbauda vai astroids ir bistams vai safe
					if tmp_ast_hazardous == True:
						ast_hazardous.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])
					else:
						ast_safe.append([tmp_ast_name, tmp_ast_nasa_jpl_url, tmp_ast_diam_min, tmp_ast_diam_max, tmp_ast_close_appr_ts, tmp_ast_close_appr_dt_utc, tmp_ast_close_appr_dt, tmp_ast_speed, tmp_ast_miss_dist])

		else:
			#Ja astroidu skaits ir mazaks pa 0 izvada šo
			logger.info("No asteroids are going to hit earth today")
	#izvada astroidu daudzumu katra lista
	logger.info("Hazardous asteorids: " + str(len(ast_hazardous)) + " | Safe asteroids: " + str(len(ast_safe)))
	#parbauda cik daudz astroidu ir bistami, un ja ir vairak pa 0
	if len(ast_hazardous) > 0:
		#sakarto pēc tuvāka laika
		ast_hazardous.sort(key = lambda x: x[4], reverse=False)
		#izprinte informaciju par tuvakkajiem laika ziņa astroidiem
		logger.info("Today's possible apocalypse (asteroid impact on earth) times:")
		for asteroid in ast_hazardous:
			logger.info(str(asteroid[6]) + " " + str(asteroid[0]) + " " + " | more info: " + str(asteroid[1]))
		#izprinte informaciju par tuvakajiem astroidiem kilometros
		ast_hazardous.sort(key = lambda x: x[8], reverse=False)
		logger.info("Closest passing distance is for: " + str(ast_hazardous[0][0]) + " at: " + str(int(ast_hazardous[0][8])) + " km | more info: " + str(ast_hazardous[0][1]))
	else:
		logger.info("No asteroids close passing earth today")
#Ja api nenostrādāja, izmet šo.
else:
	logger.critical("Unable to get response from API. Response code: " + str(r.status_code) + " | content: " + str(r.text))
