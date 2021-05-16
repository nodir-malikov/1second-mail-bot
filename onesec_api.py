import requests
import random
import string
import lxml.html as ht
from config import EMAIL_DOMAIN


def rand_pass():
    """Generate a random password or random mail"""

    random_source = string.ascii_letters + string.digits
    psw = ""
    for i in range(9):
        psw += random.choice(random_source)

    return psw


class Mailbox:
    """Main operation with 1secmail.com api:
    'get' - get all mail in box
    'read' - read message in box (need message id)
    'del' - clear mailbox, all messages be removed!
    """

    def __init__(self, mail_name):
        """Constructor"""
        self.API = 'https://www.1secmail.com/api/v1/'
        self.s = requests.Session()

        if mail_name == '':
            self._mailbox_ = rand_pass()
            # print(f'use mailbox: {self._mailbox_}@1secmail.com')
        else:
            self._mailbox_ = mail_name  # change to your own test mailbox

    def mail_jobs(self, action, this_id=None):
        """Main operation with 1secmail.com api:
        'get' - get all mail in box
        'read' - read message in box (need message id)
        'del' - clear mailbox, all messages be removed!
        """

        mail_list = 'error'

        act_list = ['getMessages', 'deleteMailbox', 'readMessage']
        act_dict = {
            'get': act_list[0],
            'del': act_list[1],
            'read': act_list[2]
        }

        if action in ['read', 'readMessage'] and this_id is None:
            print('Need message id for reading')
            return mail_list

        if action in act_dict:
            action = act_dict[action]
        else:
            print(f'Wrong action: {action}')
            return mail_list

        if action == 'readMessage':
            mail_list = self.s.get(self.API,
                                   params={'action': action,
                                           'login': self._mailbox_,
                                           'domain': EMAIL_DOMAIN,
                                           'id': this_id
                                           }
                                   )
        if action == 'deleteMailbox':
            mail_list = self.s.post('https://www.1secmail.com/mailbox/',
                                    data={'action': action,
                                          'login': self._mailbox_,
                                          'domain': EMAIL_DOMAIN
                                          }
                                    )
        if action == 'getMessages':
            mail_list = self.s.get(self.API,
                                   params={'action': action,
                                           'login': self._mailbox_,
                                           'domain': EMAIL_DOMAIN
                                           }
                                   )

        return mail_list

    def filtered_mail(self, domain=True, subject=True, date=True):
        """Simple mail filter, all params optional"""

        email = self.mail_jobs('get')
        out_mail = []
        if email != 'error':
            # print(ma.url)
            list_ma = email.json()
            for i in list_ma:
                if not id:
                    id_find = i['id'].find(id) != -1
                else:
                    id_find = id
                if not date:
                    dat_find = i['date'].find(date) != -1
                else:
                    dat_find = date
                if not domain:
                    dom_find = i['from'].lower().find(domain) != -1
                else:
                    dom_find = domain
                if not subject:
                    sub_find = i['subject'].lower().find(subject) != -1
                else:
                    sub_find = subject
                if sub_find and dom_find and id_find and dat_find:
                    out_mail.append(i['id'])

            if len(out_mail) > 0:
                return out_mail
            else:
                return 'not found'
        else:
            return email

    def clear_box(self, domain, subject, clear=True):
        """Clear mail box if we find some message"""

        email = self.filtered_mail(domain, subject)
        if isinstance(email, list):
            email = self.mail_jobs('read', email[0])
            if email != 'error':
                if clear:
                    print('clear mailbox')
                    self.mail_jobs('del')

                return email
            else:
                return email
        else:
            return email

    def get_link(self, domain, subject, x_path='//a', clear=True):
        """Find link inside html mail body by x-path and return link"""

        email = self.clear_box(domain, subject, clear)
        if email != 'error' and email != 'not found':
            mail_body = email.json()['body']
        else:
            return email
            # try:
        web_body = ht.fromstring(mail_body)
        # except Type_of_Exception:
        #    print("except")
        child = web_body.xpath(x_path)[0]
        return child.attrib['href']

    @property
    def mailbox_(self):
        return self._mailbox_


if __name__ == "__main__":
    # user box
    ma = Mailbox('api.test')
    mb = ma.filtered_mail()
    print('all mail id: ', mb)

    if isinstance(mb, list):
        print(mb[0])
        mf = ma.mail_jobs('read', mb[0])
        print('first mail: ', mf.json()['body'])
    else:
        mf = 'not found'

    print("if email from gmail.com contain 'Restore password' subject - return restore link and clear mailbox")
    rl = ma.get_link('gmail.com', 'Restore password')
    print('return link:', rl)
