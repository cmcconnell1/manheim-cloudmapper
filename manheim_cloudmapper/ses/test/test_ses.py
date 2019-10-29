# Copyright 2017-2019 Manheim / Cox Automotive
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from manheim_cloudmapper.ses.ses import SES
from unittest.mock import patch, call, mock_open, Mock, ANY

pbm = 'manheim_cloudmapper.ses.ses'


class TestInit(object):
    def test_all_options(self):
        with patch('%s.boto3.client' % pbm) as mock_boto:
            cls = SES(region='us-east-1')
            assert cls.region == 'us-east-1'
            assert mock_boto.mock_calls == [
                call('ses', region_name='us-east-1')
            ]


class SESTester(object):

    def setup(self):
        self.mock_boto = Mock()
        with patch('%s.boto3.client' % pbm) as m_boto:
            m_boto.return_value = self.mock_boto
            m_boto.return_value.get_caller_identity.return_value = {
                'UserId': 'MyUID',
                'Arn': 'myARN',
                'Account': '1234567890'
            }
            self.cls = SES(region='us-east-1')


class TestSendEmail(SESTester):

    def test_send_email(self):
        with patch('%s.logger' % pbm, autospec=True) as mock_logger, \
                patch('%s.open' % pbm, mock_open(read_data='foo'),
                      create=True) as m_open:

            self.cls.send_email(
                    sender='foo@maheim.com',
                    recipient='bar@manheim.com',
                    subject='foo',
                    body_text='body',
                    body_html='<html></html>',
                    attachments=['report.html'])

            assert self.mock_boto.mock_calls == [
                call.send_raw_email(Destinations=['bar@manheim.com'],
                                    RawMessage={'Data': ANY},
                                    Source='foo@maheim.com')
            ]

            assert m_open.mock_calls == [
                call('report.html', 'rb'),
                call().read()
            ]
            assert mock_logger.mock_calls == [
                call.info('Email sent!')
            ]
