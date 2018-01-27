import re
import wikipedia as wiki


class WikiHandler(object):
    def format_content(self, content):
        content = re.sub(r'\([^)]*\)', '', content)
        content = re.sub(r'\[[^\]]*\]', '', content)
        return content

    def parse_query(self, query):
        match = re.search(r'(what|who) is (.*)', query, re.IGNORECASE)
        title = ''
        if match:
            title = match.group(2)
            title = re.sub(r'[?]', '', title.strip())
            return title
        else:
            return ''

    def default_response(self):
        return 'Sorry, I dont know about it.'


    def get_summary(self, query):
        title = self.parse_query(query)
        if title == '':
            return self.default_response()

        pages = wiki.search(title)
        page_name = ''
        if pages:
            page_name = pages[0]
            if page_name:
                page = wiki.page(page_name)
                content = page.content[0:2000]
                content = self.format_content(content)
                sents = content.split('. ')
                summary = '. '.join(sents[0:2])
                return summary
        else:
            return self.default_response()
