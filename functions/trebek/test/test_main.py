from unittest.mock import MagicMock, PropertyMock

import pytest
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.exceptions import BadRequestKeyError

import main
import model


class TestParseRequest:
    @pytest.fixture
    def success_request(self):
        req = MagicMock()
        type(req).form = PropertyMock(
            return_value=ImmutableMultiDict([("callFrom", "from"), ("callTo", "to")])
        )
        return req

    @pytest.fixture
    def fail_request(self):
        req = MagicMock()
        type(req).form = PropertyMock(return_value=ImmutableMultiDict([("foo", "bar")]))
        return req

    def test_succeeds_with_good_request(self, success_request):
        res = main.parse_request(success_request)
        assert isinstance(res, model.ForwardingRequest)

    def test_extract_data_from_form_data(self, success_request):
        res = main.parse_request(success_request)
        assert res.numberFrom == "from"
        assert res.numberTo == "to"

    def test_fails_with_bad_request(self, fail_request):
        with pytest.raises(BadRequestKeyError):
            main.parse_request(fail_request)
