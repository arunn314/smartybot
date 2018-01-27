from gmail_handler import GmailHandler
from adt_handler import ADTHandler
from stock_handler import StockHandler
from weather_handler import WeatherHandler
from wiki_handler import WikiHandler
from plaid_handler import PlaidHandler
from gmaps_handler import GmapsHandler
from plug_handler import PlugHandler

class Processor(object):
    def __init__(self):
        self.adt_handler = ADTHandler()
        self.gmail_handler = GmailHandler()
        self.stock_handler = StockHandler()
        self.weather_handler = WeatherHandler()
        self.wiki_handler = WikiHandler()
        self.plaid_handler = PlaidHandler()
        self.gmaps_handler = GmapsHandler()
        self.plug_handler = PlugHandler()

    """Process commands."""
    def process(self, cmd, args):
        """ Process given command with arguments.

        Args:
            cmd (str): command to execute.
            args (dict): arguments for command.

        Returns:
            response (str); response of command.

        """
        if cmd == 'email':
            handler = self.gmail_handler
            if args['action'] == 'new':
                return handler.get_unread()
            if args['action'] == 'find':
                return handler.search_unread(args['term'])

        if cmd == 'stock':
            handler = self.stock_handler
            return handler.get_stockprice(args['company'])

        if cmd == 'weather':
            handler = self.weather_handler
            return handler.get_temperature(
                args['city'], args['country'])

        if cmd == 'route':
            handler = self.gmaps_handler
            return handler.get_route(
                args['source'], args['destination'], args['directions'])

        if cmd == 'switch':
            handler = self.plug_handler
            if args['action'] == 'on':
                return handler.switch_on()
            if args['action'] == 'off':
                return handler.switch_off()

        if cmd == 'expense':
            handler = self.plaid_handler
            if args['exp_type'] != 'all':
                return handler.get_txns_category(args['exp_type'], args['interval'])
            else:
                return handler.get_summary(args['interval'])

        if cmd == 'security':
            handler = ADTHandler()
            if args['action'] == 'disarm':
                return handler.disarm()
            if args['action'] == 'stay':
                return handler.arm_stay()
            if args['action'] == 'away':
                return handler.arm_away()
            if args['action'] == 'status':
                return handler.get_status()
            if args['action'] == 'sensors':
                return handler.get_sensor_status()

        if cmd == 'wiki':
            handler = self.wiki_handler
            return handler.get_summary(args['query'])

if __name__ == '__main__':
    p = Processor()
    args = {}
    # args['action'] = 'new'
    # args['term'] = 'guille'
    # print p.process('email', args)

    args['action'] = 'status'
    args['term'] = 'guille'
    print p.process('adt', args)
