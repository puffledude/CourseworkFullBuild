#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_phonevalidator
----------------------------------

Tests for `phonevalidator` module.
"""

import pytest
import os
from phonevalidator import Validator
from phonenumbers import PhoneNumberFormat


@pytest.fixture
def base_schema():
    return {'phone': {'type': 'phonenumber', 'region': 'US'}}

'''
def test_Validator_init():
    v = Validator(formatter='INTERNATIONAL', region='AS')
    assert v.formatter == PhoneNumberFormat.INTERNATIONAL
    assert v.region == 'AS'

    v = Validator()
    assert v.formatter is None
    assert v.region is None
'''


def test_Validator_default_region():
    v = Validator()
    assert v._default_region() == 'US'

    os.environ['DEFAULT_PHONE_REGION'] = 'AS'
    assert v._default_region() == 'AS'


def test_Validator_set_formatter():
    v = Validator()
    v._set_formatter('NOT_VALID')
    assert v.formatter == PhoneNumberFormat.NATIONAL
    v.formatter = None
    v._set_formatter()
    assert v.formatter == PhoneNumberFormat.NATIONAL


def test_Validator_set_default_formatter():
    v = Validator()
    v._set_default_formatter()
    assert v.formatter == PhoneNumberFormat.NATIONAL
    os.environ['DEFAULT_PHONE_FORMAT'] = 'INTERNATIONAL'
    v._set_default_formatter()
    assert v.formatter == PhoneNumberFormat.INTERNATIONAL


def test_Validator_is_valid_region():
    v = Validator()
    assert v._is_valid_region(None) is False
    assert v._is_valid_region('us') is True


def test_phonenumber_fail(base_schema):
    doc = {'phone': 'gibberish'}
    v = Validator(base_schema)
    assert v.validate(doc) is False

    doc['phone'] = '+41513555'
    assert v.validate(doc) is False


def test_phone_number_valid(base_schema):
    base_schema['phone']['region'] = 'US'
    doc = {'phone': '5135555555'}
    v = Validator(base_schema)
    assert v.validate(doc)
    assert v.document['phone'] == '5135555555'


def test_phoneNumberFormat_fail(base_schema):
    base_schema['phone'].update({
        'phoneNumberFormat': 'InvalidFormat',
        'formatPhoneNumber': True,
        'region': 'US',
    })
    doc = {'phone': '5135555555'}
    v = Validator(base_schema)
    assert v.validate(doc) is False


def test_region_fail(base_schema):
    # non valid region
    schema = {'phone': {'type': 'phonenumber', 'region': 'XYZ'}}
    doc = {'phone': '5135555555'}
    v = Validator(schema)
    assert v.validate(doc) is False


def test_phone_gets_formatted(base_schema):
    base_schema['phone'].update({
        'formatPhoneNumber': True,
        'phoneNumberFormat': 'NATIONAL',
        'region': 'US'})
    doc = {'phone': '5135555555'}
    v = Validator(base_schema)
    assert v.validate(doc)
    assert v.document['phone'] == '(513) 555-5555'
