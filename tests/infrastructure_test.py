# -*- coding: utf-8 -*-

import unittest
from mopa import create_app
from mopa.infrastructure import (snake_case, remove_accents, Location)


class LocationsTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app = create_app()
        app.testing = True
        self.client = app.test_client()

    def test_gets_notified_people(self):
        people = Location.i().get_notified_companies_phones('Magoanine B', '04')
        self.assertTrue(len(people) >= 1)

        people = Location.i().get_notified_companies_phones('25 de Junho A', '04')
        self.assertTrue(len(people) >= 1)

        people = Location.i().get_notified_companies_phones('Luis Cabral', '04')
        self.assertTrue(len(people) >= 1)

        people = Location.i().get_notified_companies_phones('Nsalane', '04')
        self.assertTrue(len(people) == 0)

        people = Location.i().get_notified_companies_phones('Malhazine', '04')
        self.assertTrue(len(people) >= 1)

        people = Location.i().get_notified_companies_phones('Magoanine C', '04')
        self.assertTrue(len(people) >= 1)


class UtilsTestCase(unittest.TestCase):

    def test_snake_case(self):
        self.assertEqual('snake_case', snake_case('SnakeCase'))

    def test_remove_accents(self):
        self.assertEqual('uo', remove_accents(u'úõ'))
