# -*- coding: utf-8 -*-

import os
import unittest
from mopa import create_app
from mopa.infrastructure import send_mail, asynchronously


@unittest.skip('Tests are slow')
class MailTestCase(unittest.TestCase):

    def setUp(self):
        self.app = app = create_app()
        app.testing = True
        self.client = app.test_client()

    def tearDown(self):
        pass

    def set_current_user(self, email, user_id, is_admin=False):
        os.environ['USER_EMAIL'] = email or ''
        os.environ['USER_ID'] = user_id or ''
        os.environ['USER_IS_ADMIN'] = '1' if is_admin else '0'

    def test_full_email_is_sent(self):

        send_mail(
            [('To Example', 'to@example.com'), 'you@example.com'],
            '[Mail Test] - I should be delivered to the inbox',
            '''
                <html>
                    <head></head>
                    <body>
                        <h1>Hello, wellcome to the mailing group</h1>
                        <p>See you in the inbox</p>
                        <br/>
                        <br/>
                        </p>Regards</p>
                    </body>
                </html>
            ''',
            is_html=True,
            cc = 'him@example.com, herr@example.com',
            bcc = ['them@example.com', ('You Know Who', 'youknowwho@example.com')],
            sender = ('App', 'notifications@example.com'),
            reply_to = 'no-reply@example.com',
            attachments = [os.path.abspath(os.path.dirname(__file__)) + '/mail_test.py', os.path.abspath(os.path.dirname(__file__)) + '/__init__.py']
        )

    def test_full_email_is_sent_async(self):
        jobs = []

        send_mail = asynchronously(send_mail)
        jobs.append(
            send_mail(
                [('To Example', 'to@example.com'), 'you@example.com'],
                '[Mail Test] - I should be delivered to the inbox',
                '''
                    <html>
                        <head></head>
                        <body>
                            <h1>Hello, wellcome to the mailing group</h1>
                            <p>See you in the inbox</p>
                            <br/>
                            <br/>
                            </p>Regards</p>
                        </body>
                    </html>
                ''',
                is_html=True,
                cc = 'him@example.com, herr@example.com',
                bcc = ['them@example.com', ('You Know Who', 'youknowwho@example.com')],
                sender = ('App', 'notifications@example.com'),
                reply_to = 'no-reply@example.com',
                attachments = [os.path.abspath(os.path.dirname(__file__)) + '/mail_test.py', os.path.abspath(os.path.dirname(__file__)) + '/__init__.py']
            )
        )

        for j in jobs:
            j.join()

    def test_view_on_browser(self):
        pass
