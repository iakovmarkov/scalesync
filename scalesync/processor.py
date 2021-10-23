import logging
from bluepy import btle
from rauth.service import OAuth1Service

log = logging.getLogger(__name__)

class ScanProcessor():
    def __init__(self, config):
        self.config = config
        self.previous_weight = 0
        btle.DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        if dev.addr == self.config['scale_mac'].lower() and isNewDev:
            for (sdid, desc, data) in dev.getScanData():
                ### Xiaomi V1 Scale ###
                if data.startswith('1d18') and sdid == 22:
                    self.parse_data_v1(data)

                ### Xiaomi V2 Scale ###
                if data.startswith('1b18') and sdid == 22:
                    self.parse_data_v2(data)

    def parse_data_v1(self, data):
        measunit = data[4:6]
        measured = int((data[8:10] + data[6:8]), 16) * 0.01

        if measunit.startswith(('03', 'b3')): 
            unit = 'lbs'
        if measunit.startswith(('12', 'b2')): 
            unit = 'jin'
        if measunit.startswith(('22', 'a2')): 
            unit = 'kg'
            measured = measured / 2

        if unit:
            weight = round(measured, 2)

            log.debug(f"Data from scale: {weight}{unit}")

            if self.previous_weight != weight:
                self.record_values(weight=weight, unit=unit, hasImpedance=hasImpedance, impendance=impendance)
                self.previous_weight = weight

    def parse_data_v2(self, data):
        ctrlByte1 = bytes.fromhex(data[4:])[1]
        isStabilized = ctrlByte1 & (1<<5)
        hasImpedance = ctrlByte1 & (1<<1)

        measunit = data[4:6]
        measured = int((data[28:30] + data[26:28]), 16) * 0.01
        
        if measunit == "03":
            unit = 'lbs'
        if measunit == "02": 
            unit = 'kg'
            measured = measured / 2
        
        if unit and isStabilized:
            weight = round(measured, 2)
            impendance = str(int((data[24:26] + data[22:24]), 16))

            log.debug(f"Data from scale: {weight}{unit}, impendance {impendance} {hasImpedance}")

            if self.previous_weight != weight + int(impendance):
                self.previous_weight = weight + int(impendance)
                self.record_values(weight=weight, unit=unit, hasImpedance=hasImpedance, impendance=impendance)

    def record_values(self, weight, unit, hasImpedance, impendance):
      for user in self.config['users']:
        if (weight > user['weight_threshold']):
          login = user['login']
          log.info(f"Logging weight {weight} for user {login}.")

          oauth = OAuth1Service(
            name='fatsecret',
            consumer_key=self.config['app_key'],
            consumer_secret=self.config['app_secret'],
            request_token_url='https://www.fatsecret.com/oauth/request_token',
            access_token_url='https://www.fatsecret.com/oauth/access_token',
            authorize_url='https://www.fatsecret.com/oauth/authorize',
            base_url='https://platform.fatsecret.com/rest/server.api'
          )

          session = oauth.get_session((user['token'], user['secret']))

          params = {
            'method': 'weight.update', 
            'format': 'json', 
            'current_weight_kg': weight,
            'weight_type': unit,
          }

          r = session.get('https://platform.fatsecret.com/rest/server.api', params=params)
          log.info(f'Logging result: {r.text}')

          return

        log.warning(f'Could not find user to log {weight}')
