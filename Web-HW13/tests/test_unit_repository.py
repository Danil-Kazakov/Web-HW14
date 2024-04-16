import unittest
from unittest.mock import MagicMock

from sqlalchemy import Session

from models import User, Contacts
from schemas import ContactResponse, ContactBase
from repository import (
    get_contacts,
    get_contact,
    create_contact,
    update_contact,
    delete_contact,
)

class TestContacts(unittest.IsolatedAsyncioTestCase):
    def SetUp(self):
        self.session = MagicMock(spec=Session)
        self.user = User(id=1)

    async def test_get_contacts(self):
        contacts = [Contacts(), Contacts(), Contacts()]
        self.session.query().offset().limit().all.return_value = contacts
        result = await get_contacts(skip=0, limit=10, db=self.session)
        self.assertEqual(result, contacts)

    async def test_get_contact_found(self):
        contact = Contacts()
        self.session.query().filter().first.return_value = contact
        result = await get_contact(contact_id=1, db=self.session)
        self.assertEqual(result, contact)

    async def test_get_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await get_contact(contact_id=1, db=self.session)
        self.assertIsNone(result)

    async def test_create_contact(self):
        body = ContactResponse(first_name="TestName", last_name="TestSurname", id=1000, email="test@email", phone_number="00000000")
        expected_result = Contacts(**body.dict())
        result = await create_contact(body, db=self.session)
        self.assertEqual(result.first_name, body.first_name)
        self.assertEqual(result.last_name, body.last_name)
        self.assertEqual(result.id, body.id)
        self.assertEqual(result.email, body.email)
        self.assertEqual(result.phone_number, body.phone_number)
        self.assertTrue(hasattr(result, "id"))

    async def test_update_contact_found(self):
        body = ContactResponse(first_name="TestName", last_name="TestSurname", id=1000, email="test@email", phone_number="00000000")
        contact = Contacts()
        self.session.query().filter().first.return_value = contact
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1000, body=body, db=self.session)
        self.assertEqual(result, contact)

    async def test_update_contact_not_found(self):
        body = ContactResponse(first_name="TestName", last_name="TestSurname", id=1000, email="test@email", phone_number="00000000")
        self.session.query().filter().first.return_value = None
        self.session.commit.return_value = None
        result = await update_contact(contact_id=1000, body=body, db=self.session)
        self.assertEqual(result)

    async def test_delete_contact_found(self):
        contact = Contacts()
        self.session.query().filter().first.return_value = contact
        result = await delete_contact(contact_id=1000, db=self.session)
        self.assertEqual(result, contact)

    async def test_delete_contact_not_found(self):
        self.session.query().filter().first.return_value = None
        result = await delete_contact(contact_id=1000, db=self.session)
        self.assertIsNone(result)




