import time
import xmlrpc.client
import argparse
from db import Session, Contact

url = 'https://chift.odoo.com/'
login = password = 'a.kyrychenko@digiscorp.com'
db = 'chift'

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Sleep for a specified number of minutes.")
    parser.add_argument("minutes", type=int, help="Number of minutes to sleep")

    args = parser.parse_args()

    minutes = args.minutes

    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url))
    uid = common.authenticate(db, login, password, {})

    none_if_false = lambda x: None if x is False else str(x).strip()

    while True:
        models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))

        contact_ids = models.execute_kw(db, uid, password, 'res.partner', 'search', [[]])
        contacts = models.execute_kw(db, uid, password, 'res.partner', 'read', [contact_ids], {'fields': ['name', 'email']})
        with Session.begin() as session:
            for contact in contacts:
                desired_contact = session.query(Contact).filter(Contact.oodo_id == contact['id']).first()
                if not desired_contact:
                    new_contact = Contact(
                        oodo_id = contact['id'],
                        name = none_if_false(contact['name']),
                        email = none_if_false(contact['email'])
                    )
                    session.add(new_contact)
                else:
                    changed_fields = {
                        field: contact[field]
                        for field in Contact.fields(ignored=['id', 'oodo_id'])
                        if contact[field] != getattr(desired_contact, field)
                    }
                    if changed_fields:
                        for field, value in changed_fields.items():
                            setattr(desired_contact, field, value)
            
            db_contacts = session.query(Contact).all()
            for db_contact in db_contacts:
                if db_contact.oodo_id not in [c['id'] for c in contacts]:
                    session.delete(db_contact)
            session.commit()
        
        time.sleep(minutes * 60)