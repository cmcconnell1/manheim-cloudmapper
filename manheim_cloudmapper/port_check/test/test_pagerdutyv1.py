import sys
import json
import pytest
from manheim_cloudmapper.port_check.pagerdutyv1 import PagerDutyV1

# https://code.google.com/p/mock/issues/detail?id=249
# py>=3.4 should use unittest.mock not the mock package on pypi
if (
        sys.version_info[0] < 3 or
        sys.version_info[0] == 3 and sys.version_info[1] < 4
):
    from mock import patch, call, Mock, mock_open, DEFAULT
else:
    from unittest.mock import patch, call, Mock, mock_open, DEFAULT

pbm = 'manheim_cloudmapper.port_check.pagerdutyv1'
pb = '%s.PagerDutyV1' % pbm

class TestInit(object):

    @patch.dict(
        'os.environ',
        {'PD_SERVICE_KEY': 'cKey'},
        clear=True
    )
    def test_no_options(self):
        cls = PagerDutyV1('foo')
        assert cls._account_name == 'foo'
        assert cls._service_key == 'cKey'
        assert cls._incident_key == 'cloudmapper-foo'

    @patch.dict('os.environ', {}, clear=True)
    def test_all_options(self):
        cls = PagerDutyV1(
            'foo', service_key='cKey', incident_key='cloudmapper-foo'
        )
        assert cls._account_name == 'foo'
        assert cls._service_key == 'cKey'
        assert cls._incident_key == 'cloudmapper-foo'

    @patch.dict('os.environ', {}, clear=True)
    def test_no_crit_key(self):
        with pytest.raises(RuntimeError) as exc:
            PagerDutyV1('foo')
        assert str(exc.value) == 'ERROR: PagerDutyV1 alert ' \
                                 'provider requires ' \
                                 'service_key parameter or' \
                                 ' PD_SERVICE_KEY ' \
                                 'environment variable.'
                            
class PagerDutyV1Tester(object):

    def setup(self):
        with patch('%s.__init__' % pb) as m_init:
            m_init.return_value = None
            self.cls = PagerDutyV1('acctname')
            self.cls._account_name = None
            self.cls._incident_key = 'iKey'
            self.cls._service_key = None
        
class TestSendEvent(PagerDutyV1Tester):

    def test_success(self):
        mock_http = Mock()
        mock_resp = Mock(
            status=200, data='{"status": "success", "message": '
                             '"Event processed", "incident_key":'
                             ' "iKey"}'
        )
        mock_http.request.return_value = mock_resp
        expected = json.dumps(
            {'foo': 'bar', 'service_key': 'sKey'}, sort_keys=True
        ).encode('utf-8')
        with patch('%s.urllib3.PoolManager' % pbm) as mock_pm:
            mock_pm.return_value = mock_http
            self.cls._send_event('sKey', {'foo': 'bar'})
        assert mock_http.mock_calls == [
            call.request(
                'POST', self.cls.pd_url,
                headers={'Content-type': 'application/json'},
                body=expected
            )
        ]

    def test_invalid_event(self):
        mock_http = Mock()
        mock_resp = Mock(
            status=400, data='{"status": "invalid event",'
                             '"message": "Event object is invalid", '
                             '"errors": ["foo"]}'
        )
        mock_http.request.return_value = mock_resp
        expected = json.dumps(
            {'foo': 'bar', 'service_key': 'sKey'}, sort_keys=True
        ).encode('utf-8')
        with patch('%s.urllib3.PoolManager' % pbm) as mock_pm:
            mock_pm.return_value = mock_http
            with pytest.raises(RuntimeError):
                self.cls._send_event('sKey', {'foo': 'bar'})
        assert mock_http.mock_calls == [
            call.request(
                'POST', self.cls.pd_url,
                headers={'Content-type': 'application/json'},
                body=expected
            )
        ]

class TestEventDict(PagerDutyV1Tester):

    def test_no_account_name(self):
        assert self.cls._event_dict() == {
            'incident_key': 'iKey',
            'details': {},
            'client': 'cloudmapper'
        }

    def test_with_account_name(self):
        self.cls._account_name = 'myAcct'
        assert self.cls._event_dict() == {
            'incident_key': 'iKey',
            'details': {'account_name': 'myAcct'},
            'client': 'cloudmapper'
        }
    
class TestOnSuccess(PagerDutyV1Tester):

    def test_happy_path(self):
        self.cls._service_key = 'cKey'
        self.cls._account_name = 'myAcct'
        with patch('%s._event_dict' % pb, autospec=True) as m_ed:
            m_ed.return_value = {'event': 'dict', 'details': {}}
            with patch('%s._send_event' % pb, autospec=True) as m_send:
                self.cls.on_success()
        assert m_ed.mock_calls == [call(self.cls)]
        assert m_send.mock_calls == [
            call(self.cls, 'cKey', {
                'event': 'dict',
                'details': {},
                'event_type': 'resolve',
                'description': 'cloudmapper in myAcct found '
                               'no problems'
            })
        ]
    
    def test_no_account_name(self):
        self.cls._service_key = 'cKey'
        with patch('%s._event_dict' % pb, autospec=True) as m_ed:
            m_ed.return_value = {'event': 'dict', 'details': {}}
            with patch('%s._send_event' % pb, autospec=True) as m_send:
                self.cls.on_success()
        assert m_ed.mock_calls == [call(self.cls)]
        assert m_send.mock_calls == [
            call(self.cls, 'cKey', {
                'event': 'dict',
                'details': {},
                'event_type': 'resolve',
                'description': 'cloudmapper in  found '
                               'no problems'
            })
        ]

class TestOnFailures(PagerDutyV1Tester):

    def test_failure_exception(self):
        self.cls._account_name= 'aName'
        self.cls._service_key = 'cKey'
        data = {'event': 'data', 'details': {}}
        exc = RuntimeError('foo')
        expected = {
            'event': 'data',
            'details': {
                'exception': exc.__repr__()
            },
            'event_type': 'trigger',
            'description': 'cloudmapper in aName '
                           'failed with an exception: %s' % exc.__repr__()
        }
        with patch.multiple(
            pb,
            autospec=True,
            _event_dict=DEFAULT,
            _send_event=DEFAULT
        ) as mocks:
            mocks['_event_dict'].return_value = data
            self.cls.on_failure({'p': 'd'}, exc=exc)
        assert mocks['_event_dict'].mock_calls == [call(self.cls)]
        assert mocks['_send_event'].mock_calls == [
            call(self.cls, 'cKey', expected)
        ]

    def test_failure(self):
        self.cls._account_name= 'aName'
        self.cls._service_key = 'cKey'
        data = {'event': 'data', 'details': {}}
        expected = {
            'event': 'data',
            'details': {
                'hosts_with_ports': 'acct\tapigateway\tabc123.execute-api.us-east-1.amazonaws.com\tb\'80,443\'\tabc1245\n'
                                    'acct\tapigateway\twww576.execute-api.us-east-1.amazonaws.com\tb\'80,443\'\twwwe8932\n'
            },
            'event_type': 'trigger',
            'description': 'cloudmapper in aName '
                           'had publicly accesible ports'
        }
        with patch.multiple(
            pb,
            autospec=True,
            _event_dict=DEFAULT,
            _send_event=DEFAULT
        ) as mocks:
            mocks['_event_dict'].return_value = data
            problem_str = ("%s\t%s\t%s\t%s\t%s" % ('acct','apigateway','abc123.execute-api.us-east-1.amazonaws.com','80,443'.encode("ascii"),'abc1245') + '\n')
            problem_str += ("%s\t%s\t%s\t%s\t%s" % ('acct','apigateway','www576.execute-api.us-east-1.amazonaws.com','80,443'.encode("ascii"),'wwwe8932') + '\n')
            self.cls.on_failure(problem_str)
        assert mocks['_event_dict'].mock_calls == [call(self.cls)]
        assert mocks['_send_event'].mock_calls == [
            call(self.cls, 'cKey', expected)
        ]