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
        },
        'Partner Data': {
            'paypal_address': 'Paypal Address',
            'number_of_sales': 'Number of Sales',
            'first_referrer': 'First Referrer',
            'last_referrer': 'Last Referrer',
            'partner_program': 'Partner Program',
        },
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

    @staticmethod
    def _root_el_from_id(id):
        root = etree.Element('contact')
        root.attrib['id'] = str(id)
        return root

    @staticmethod
    def _els_from_ids(ids):
        els = []
        for id in ids:
            el = etree.Element('contact_id')
            el.text = str(id)
            els.append(el)
        return els

    def fetch_notes(self):
        els = self._els_from_ids([self.id])
        req_type = "fetch_notes"
        data = etree.tostring(els[0])
        return self.request(
                req_type=req_type,
                data=data,
                )

    @classmethod
    def fetch_all_notes(cls, ids):
        els = cls._els_from_ids(ids)
        req_type = "fetch_notes"
        data = "".join([etree.tostring(el) for el in els])
        obj = cls()
        return obj.request(
                req_type=req_type,
                data=data,
                )

    @classmethod
    def fetch_sequences(cls):
        """
        List of sequence names in the account with corresponding ids

        :return: list of (sequence id, sequence name) tuples
        """
        # XXX full param doesn't work
        req_type = "fetch_sequences"
        obj = cls()
        response = obj.request(
                req_type=req_type,
                )
        result = obj.response_result_tag
        ret = []
        for seq_el in result.findall("sequence"):
            id = seq_el.attrib['id']
            name = seq_el.text
            ret.append((id, name))
        return ret

    def _update_sequences(self, action, sequences):
        """
        Adds/removes sequences to/from a contact.

        :param action: 'add' or 'remove'
        :param sequences: list of sequence ids
        """
        root = self._root_el_from_id(self.id)

        group_el = etree.Element('Group_Tag')
        group_el.attrib['name'] = 'Sequences and Tags'
        root.append(group_el)

        field_el = etree.Element('field')
        field_el.attrib['name'] = 'Sequences'
        if action == 'remove':
            field_el.attrib['action'] = 'remove'
        field_el.text = self.list_item_separator.join(
            [str(seq)for seq in sequences]
            )
        group_el.append(field_el)

        req_type = "update"
        data = etree.tostring(root)
        return self.request(
                req_type=req_type,
                data=data,
                )

    def add_sequences(self, sequences):
        """
        Adds the sequences to a contact.

        :param sequences: list of sequence ids
        """
        return self._update_sequences('add', sequences)

    def remove_sequences(self, sequences):
        """
        Removes the sequences from a contact.

        :param sequences: list of sequence ids
        """
        return self._update_sequences('remove', sequences)

    @classmethod
    def pull_tags(cls):
        """
        List of tag names in the account with corresponding ids

        :return: list of (tag id, tag name) tuples
        """
        req_type = "pull_tag"
        obj = cls()
        response = obj.request(
                req_type=req_type,
                )
        result = obj.response_result_tag
        ret = []
        for tag_el in result.findall("tag"):
            id = tag_el.attrib['id']
            name = tag_el.text
            ret.append((id, name))
        return ret

    @classmethod
    def fetch_tags(cls):
        """List of tag names in the account

        :return: list of tag names
        """
        req_type = "fetch_tag"
        obj = cls()
        response = obj.request(
                req_type=req_type,
                )
        result = obj.response_result_tag
        raw_tags = result.find("tags").text
        tags = [
            tag for tag in
            raw_tags.split(cls.list_item_separator)
            if tag
            ]
        return tags

    def _update_tags(self, req_type, tags):
        root = self._root_el_from_id(self.id)
        for tag in tags:
            tag_el = etree.Element('tag')
            tag_el.text = tag
            root.append(tag_el)
        data = etree.tostring(root)
        return self.request(
                req_type=req_type,
                data=data,
                )

    def add_tags(self, tags):
        """
        Adds the tags to a contact.
        If a tag doesn't exist yet it will be created.

        :param tags: list of tag names
        """
        return self._update_tags("add_tag", tags)

    def remove_tags(self, tags):
        """
        Removes the tags from a contact.

        :param tags: list of tag names
        """
        return self._update_tags("remove_tag", tags)

    @classmethod
    def get_deleted_contacts(cls, start, end):
        """
        Contact details of contacts deleted within the given timeframe

        :param start:
            timeframe start (datetime)
        :param end:
            timeframe end (datetime)
        """
        req_type = 'get_deletedcontacts'
        el_start = etree.Element('dateStart')
        el_start.text = str(cls.convert_to_timestamp(start))
        el_end = etree.Element('dateEnd')
        el_end.text = str(cls.convert_to_timestamp(end))
        data = "".join([etree.tostring(el_start), etree.tostring(el_end)])
        return cls().request(
            req_type=req_type,
            data=data,
            )
