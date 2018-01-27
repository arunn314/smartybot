from gmail import Gmail
from datetime import date
from config import GMAIL_CONFIG

class GmailHandler(object):
    def __init__(self):
        """Initialise Gmail object"""
        self.obj = Gmail()
        self.obj.login(GMAIL_CONFIG['username'], GMAIL_CONFIG['password'])
        self.unread = self.obj.inbox().mail(unread=True)

    def get_unread(self, recent=False):
        if recent:
            self.unread = self.obj.inbox().mail(unread=True, on=date.today())
        else:
            self.unread = self.obj.inbox().mail(unread=True)
        return self._format_msg_count(len(self.unread))

    def search_unread(self, term):
        """Search sender or subject for a given term.

        Args:
            term (str): term to search.

        Returns:
            subject (str): subject of email with term/from sender

        """
        self.unread = self.obj.inbox().mail(unread=True)
        term = term.lower()
        result = []
        for mail in self.unread:
            mail.fetch()
            subject = mail.subject
            sender = mail.fr
            if term in subject.lower() or term in sender:
                result.append(mail.subject)

        return self._format_search_results(result)

    """Formatting methods."""
    def _format_msg_count(self, msg_count):
        if msg_count:
            msg = 'You have {msg_count} new emails.'
            msg = msg.format(msg_count=msg_count)
        else:
            msg = 'You have no new emails.'
        return msg

    def _format_search_results(self, results):
        msg = self._format_msg_count(len(results))
        results.insert(0, msg)
        msg = '\n'.join(results)
        return msg

    def __del__(self):
        """Destructor"""
        self.obj.logout()
