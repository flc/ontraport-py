ontraport-py
============

Python client for ONTRAPORT API.
http://ontraport.com/
http://ontraport.com/partners-api/

Important! This project is work in progress, probably with full of bugs and limited feature set.
Any kind of contribution is welcomed.


Usage
=====

Setting your API credentials
----------------------------
```python
import ontraport

ontraport.config.app_id = <YOUR APP ID>
ontraport.config.api_key = <YOUR API KEY>
```

Make sure the API Key has the needed permissions and the owner is set.
More info: https://support.ontraport.com/entries/26073705-Contacts-API#auth

Examples
--------
Create contact:

```python
contact = ontraport.Contact.create(
    first_name="John",
    last_name="Doe",
    email="john.doe@gmail.com",
    tags=["MyApp users"]
    )
```

Retrieve contact:

```python
contact = ontraport.Contact.retrieve(id=1)
print contact.email
```

Delete contact:

```python
c = ontraport.Contact(id=1)
c.delete()
```

Fetch sequences:

```python
>>> ontraport.Contact.fetch_sequences()
[(1, 'my sequence 1'), (2, 'my sequence 2'), (3, 'my sequence 3')]
```

Add sequences:

```python
>>> contact_id = 100
>>> contact = ontraport.Contact(id=contact_id)
>>> contact.add_sequences([1, 2])
```

Remove sequences:

```python
>>> contact_id = 100
>>> contact = ontraport.Contact.retrieve(contact_id)
>>> contact.remove_sequences([1, 2])
```

Pull tags:

```python
>>> contact = ontraport.Contact.pull_tags()
[(1, 'my tag 1'), (2, 'my tag 2'), (3, 'my tag 3')]
```

Fetch tags:

```python
>>> contact = ontraport.Contact.fetch_tags()
['my tag 1', 'my tag 2', 'my tag 3']
```

Add tags:

```python
>>> contact_id = 100
>>> contact = ontraport.Contact(id=contact_id)
>>> contact.add_tags(['my tag1', 'my tag 2'])
```

Remove tags:

```python
>>> contact_id = 100
>>> contact = ontraport.Contact(id=contact_id)
>>> contact.remove_tags(['my tag 2'])
```
