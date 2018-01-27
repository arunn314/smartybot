import re

class Parser(object):
    def __init__(self):
        self.intents = {
            'security': ['security', 'adt'],
            'email': ['emails', 'from', 'about', 'new'],
            'stock': ['stock', 'price'],
            'weather': ['weather', 'temperature', 'rain'],
            'snap': ['snap'],
            'stream': ['stream'],
            'time': ['time'],
            'wiki': ['what', 'who'],
            'echo': ['say', 'speak', 'tell'],
            'image': ['image'],
            'expense': ['expenses', 'expense','spend'],
            'switch': ['switch', 'turn'],
            'route': ['route', 'fastest', 'steps', 'directions']
        }
        self.expense_types = [
            'food', 'pharmacy', 'misc', 'fuel', 'groceries', 'amazon',
            'walmart', 'auto loan', 'hoa', 'uber', 'tax', 'property tax',
            'electricity', 'phone', 'paypal', 'atm', 'home depot', 'check',
            'credit card', 'mortgage', 'transfer', 'auto insurance', 'movie']

    def get_intent(self, message):
        message = message.lower()
        match_map = {}
        for intent in self.intents:
            matches = 0
            for word in self.intents[intent]:
                if message.find(word) != -1:
                    matches += 1
            match_map[intent] = matches

        best_intent = max(match_map, key=match_map.get)
        if match_map[best_intent] > 0:
            if best_intent == 'wiki':
                for intent in match_map:
                    if intent == 'wiki':
                        continue
                    if match_map[intent] > 0:
                        return intent
            return best_intent
        else:
            return 'unknown'

    def get_entities(self, message, intent):
        args = {}
        if intent == 'image':
            args['test'] = 'test'
        if intent == 'route':
            args['source'] = ''
            args['destination'] = ''
            args['directions'] = True if 'directions' in message.lower() else False
            match = re.search(r'(.*)(to) (.*)', message, re.IGNORECASE)
            text = ''
            if match:
                text = match.group(3)
                text = re.sub(r'[?]', '', text.strip())
                args['destination'] = text.strip()
        if intent == 'expense':
            interval = 7
            num = 1
            unit_val = 7
            if 'week' in message.lower():
                unit_val = 7
            elif 'month' in message.lower():
                unit_val = 30
            elif 'day' in message.lower():
                unit_val = 1
            match = re.search(r'(.*)(last) (\d*) (week|weeks|day|days|month)', message, re.IGNORECASE)
            if match:
                num = int(match.group(3))

            interval = num*unit_val
            args['exp_type'] = 'all'
            for exp_type in self.expense_types:
                if exp_type in message.lower():
                    args['exp_type'] = exp_type
            args['interval'] = interval
        if intent == 'wiki':
            args['query'] = message
        if intent == 'switch':
            if 'on' in message.lower():
                args['action'] = 'on'
            if 'off' in message.lower():
                args['action'] = 'off'
        if intent == 'echo':
            match = re.search(r'(say|tell|echo|speak) (.*)', message, re.IGNORECASE)
            text = ''
            if match:
                text = match.group(2)
                text = re.sub(r'[?]', '', text.strip())
            args['message'] = text
        if intent == 'security':
            msg = message.lower()
            if 'disarm' in msg:
                args['action'] = 'disarm'
            if 'stay' in msg:
                args['action'] = 'stay'
            if 'away' in msg:
                args['action'] = 'away'
            if 'status' in msg:
                args['action'] = 'status'
            if 'sensor' in msg:
                args['action'] = 'sensors'
        if intent == 'weather':
            match = re.search(r'(.*)(in|at) (.*)', message, re.IGNORECASE)
            if match:
                country = 'US'
                location = match.group(3)
                location = re.sub(r'[?]', '', location.strip())
                if ',' in location:
                    city, country = location.split(',')
                else:
                    city = location
                args['city'] = city
                args['country'] = country
        if intent == 'stock':
            match = re.search(r'(.*)(of) (.*)', message, re.IGNORECASE)
            if match:
                company = match.group(3)
                company = re.sub(r'[?]', '', company.strip())
                args['company'] = company

        if intent == 'email':
            match = re.search(r'(.*)(from|about) (.*)', message, re.IGNORECASE)
            if match:
                subject = match.group(3)
                subject = re.sub(r'[?]', '', subject.strip())
                args['term'] = subject
                args['action'] = 'find'
            else:
                args['action'] = 'new'
        return args

obj = Parser()
# inp = ['what is stock price of apple',
#         'did I get any emails from sakthi?',
#         'any new emails today?',
#         'disarm security systems?',
#         'set security to arm stay',
#         'can u set security to away?',
#         'will it rain in milpitas?',
#         'what is the weather in milpitas?',
#         'what is the weather in san francisco, us?']

# for msg in inp:
#     print obj.parse(msg)

# inp = 'any new emails today from fedex?'
# print obj.get_entities(inp, 'email')
# inp = 'turn off lights'
# print obj.get_intent(inp)
# inp = 'show food expenses'
# print obj.get_entities(inp, 'expense')
