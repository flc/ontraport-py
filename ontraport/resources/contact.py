import datetime

from lxml import etree

from .base import *


class Contact(
    Resource,
    XMLResourceMixin,
    CreateMixin,
    RetrieveMixin,
    DeleteMixin,
    ):
    endpoint = "cdata.php"
    outer_tag = "contact"
    xml_field_mapping = {
        'Contact Information': {
            'first_name': 'First Name',
            'last_name': 'Last Name',
            'email': 'Email',
            'address': 'Address',
            'address_2': 'Address 2',
            'birthday': 'Birthday',
            'city': 'City',
            'company': 'Company',
            'country': 'Country',
            'skype': 'Skype',
            'best_time_to_contact': 'Best time to contact',
            'fax': 'Fax',
            'name': 'Name',
            'office_phone': 'Office Phone',
            'sms_number': 'SMS Number',
            'state': 'State',
            'title': 'Title',
            'website': 'Website',
            'zip_code': 'Zip Code',
        },
        'Sequences and Tags': {
            'tags': 'Contact Tags',
            'sequences': 'Sequences',
        },
        'System Information': {
            'date_added': 'Date Added',
            'last_activity': 'Last Activity',
            'date_modified': 'Date Modified',
            'contact_id': 'Contact ID',
            'spent': 'Spent',
        }
    }
    date_fields = set(['birthday', 'date_added', 'last_activity', 'date_modified'])
    fetch_xml_id_tag = "contact_id"
    delete_xml_id_tag = "contact_id"
    create_req_type = "add"
    update_req_type = "update"
    fetch_req_type= "fetch"
    delete_req_type = "delete"

    def __init__(self, **params):
        self.params = params
        for k, v in params.items():
            setattr(self, k, v)

    @classmethod
    def get_deleted(self, start, end):
        req_type = 'get_deletedcontacts'
        xml = etree.Element('dateStart')
        xml.text = str(self.convert_to_timestamp(start))
        data = etree.tostring(xml)

        return obj.request(
            req_type=req_type,
            data=data,
            )
