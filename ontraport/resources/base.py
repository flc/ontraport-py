import datetime
import logging
import urlparse

import requests
import dateutil.parser
from lxml import etree

from .. import config
from ..exceptions import *


logger = logging.getLogger("ontraport")


class Resource(object):
    endpoint = None

    def get_api_url(self):
        return urlparse.urljoin(config.api_base_url, self.endpoint)

    def get_api_key(self):
        return config.api_key

    def get_app_id(self):
        return config.app_id

    def get_common_params(self):
        return {
            'appid': self.get_app_id(),
            'key': self.get_api_key(),
        }

    def get_request_params(self, req_type, **params):
        params.update(self.get_common_params())
        params['reqType'] = req_type
        if 'return_id' not in params:
            # return_id:
            # 1 - full contact record(s) is/are returned in addition
            #     to the standard Success/Failure message
            # 2 - returns the contact ID and date last modified for
            #     the contact(s) in addition to standard Success/Failure message
            params['return_id'] = 1
        # "f_add - boolean"
        # When set, forces a new contact to be added (regardless if a contact with a
        # matching email address is found).
        # Note: "Add" requests initialize this to true, "update"
        # requests initialize it to false
        return params

    def check_response(self, response):
        xml = response.content
        try:
            result_tag = etree.fromstring(xml)
            self.response_result_tag = result_tag
        except XMLSyntaxError:
            logger.debug("response xml: %s", xml)
            raise APIFailureError(xml)

        error_tag = result_tag.find("error")
        if error_tag is None:
            return True
        else:
            logger.debug("response xml: %s", xml)
            raise APIFailureError(error_tag.text.strip())

    def log_request_params(self, params):
        _params = params.copy()
        if 'appid' in _params:
            _params['appid'] = "XXX"
        if 'key' in params:
            _params['key'] = "XXX"
        logger.debug("request params: %s", _params)

    def request(self, req_type, **params):
        params = self.get_request_params(req_type, **params)
        if not params.get('appid'):
            raise ValueError('You must specify APP ID.')
        if not params.get('key'):
            raise ValueError('You must specify API Key.')
        self.log_request_params(params)
        # return
        response = requests.post(self.get_api_url(), params)
        if response.status_code != 200:
            raise APINonOKResponseError(
                "API responded with status_code: %s",
                response.status_code
                )
        self.check_response(response)
        return response


class XMLResourceMixin(object):
    outer_tag = ''
    xml_field_mapping = {}
    list_item_separator =  "*/*"
    date_fields = set()

    @staticmethod
    def dict_reverse(data):
        return {v: k for k, v in data.items()}

    @property
    def rev_xml_field_mapping_reverse(self):
        return self.dict_reverse(self.xml_field_mapping)

    @staticmethod
    def convert_to_timestamp(date):
        if isinstance(date, datetime.date):
            return date.strftime("%s")
        return date

    def get_xml(self):
        root = etree.Element(self.outer_tag)
        for group_name, field_mapping in self.xml_field_mapping.items():
            group_el = etree.Element('Group_Tag')
            group_el.attrib['name'] = group_name
            for attr, field_name in field_mapping.items():
                field_el = etree.Element('field')
                field_el.attrib['name'] = field_name
                value = getattr(self, attr, '')
                if value:
                    if isinstance(value, (list, tuple)):
                        text = self.list_item_separator.join(value)
                    else:
                        text = value
                    field_el.text = text
                    group_el.append(field_el)
            if len(group_el):
                root.append(group_el)
        return root

    @classmethod
    def object_from_xml(cls, xml):
        root = etree.fromstring(xml)
        obj_root = root.find(cls.outer_tag)
        if obj_root is None:
            return None

        field_mapping = cls.xml_field_mapping
        params = {}
        params['id'] = obj_root.attrib.get("id")

        for group_tag in obj_root.findall("Group_Tag"):
            field_data = field_mapping.get(group_tag.attrib.get("name"))
            if not field_data:
                continue
            field_data = cls.dict_reverse(field_data)
            for field_tag in group_tag.findall("field"):
                key = field_data.get(field_tag.attrib.get("name"))
                if not key:
                    continue
                value = field_tag.text
                if not value:
                    continue
                # try to parse datetime
                if key in cls.date_fields:
                    try:
                        value = dateutil.parser.parse(value)
                    except (TypeError, ValueError):
                        pass
                else:
                    # try to parse sequence
                    if cls.list_item_separator in value:
                        value = [v.strip() for v in value.split(cls.list_item_separator) if v.strip()]
                params[key] = value
        obj = cls(**params)
        obj._xml_response = xml
        return obj

    def serialize(self):
        el = self.get_xml()
        s = etree.tostring(el)
        return s


class ListMixin(object):

    def all(self, **params):
        pass


class CreateMixin(object):
    create_req_type = ""

    @classmethod
    def create(cls, **params):
        force_create = params.pop("force_create", False)
        obj = cls(**params)
        data = obj.serialize()
        kwargs = {
            'req_type': cls.create_req_type,
            'data': data
        }
        if force_create:
            # XXX why does this not work?
            # tried with True, "true", "" and non of them
            # force added a contact
            kwargs['f_add'] = ""
        resp = obj.request(**kwargs)
        xml = resp.content
        return cls.object_from_xml(xml)

    @classmethod
    def force_create(cls, **params):
        params['force_create'] = True
        return cls.create(**params)


class RetrieveMixin(object):
    fetch_xml_id_tag = ""
    fetch_req_type = "fetch"

    @classmethod
    def retrieve(cls, id, **params):
        obj = cls(**params)

        xml = etree.Element(obj.fetch_xml_id_tag)
        xml.text = str(id)
        data = etree.tostring(xml)

        resp = obj.request(
            req_type=obj.fetch_req_type,
            data=data,
            )
        xml = resp.content
        return cls.object_from_xml(xml)


class UpdateMixin(object):

    def save(self):
        pass


class DeleteMixin(object):
    delete_xml_id_tag = ""
    delete_req_type = "delete"

    def delete(self):
        if not hasattr(self, "id"):
            raise Exception("id is not set")

        xml = etree.Element(self.fetch_xml_id_tag)
        xml.text = str(self.id)
        data = etree.tostring(xml)

        resp = self.request(
            req_type=self.delete_req_type,
            data=data,
            )
        xml = resp.content
        root = etree.fromstring(xml)
        # XXX if the contact does not exist it still return Success
        if root.text == "Success":
            return True
        return False
