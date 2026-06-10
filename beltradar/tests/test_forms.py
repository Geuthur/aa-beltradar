# Django
from django import forms

# AA Belt Radar
from beltradar.forms import (
    AddSurveyForm,
    BeltSurveySessionForm,
)
from beltradar.tests import NoSocketsTestCase


class TestAddSurveyForm(NoSocketsTestCase):
    """Test AddSurveyForm"""

    def test_form_has_raw_data_field(self):
        form = AddSurveyForm()
        self.assertIn("raw_data", form.fields)

    def test_raw_data_field_is_textarea(self):
        form = AddSurveyForm()
        self.assertIsInstance(form.fields["raw_data"].widget, forms.Textarea)

    def test_raw_data_required(self):
        form = AddSurveyForm(data={"raw_data": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("raw_data", form.errors)

    def test_parse_ore_data_valid(self):
        raw_data = "Mercoxit III-Grade*	1 433	57 320	m3 24 200 000 ISK	488 km"
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertTrue(form.is_valid())
        parsed_entries = form.cleaned_data["raw_data"].entries
        self.assertEqual(len(parsed_entries), 1)
        self.assertEqual(parsed_entries[0].name, "Mercoxit III-Grade")
        self.assertEqual(parsed_entries[0].units, 1433)
        self.assertEqual(parsed_entries[0].volume_m3, 57320)
        self.assertEqual(parsed_entries[0].price_isk, 0.0)  # TODO Make Price Test

    def test_parse_ore_data_multiple_rows(self):
        raw_data = (
            "Mercoxit III-Grade*	1 433	57 320 m3	24 200 000,00 ISK	488 km\n"
            "Mercoxit III-Grade*	1 505	60 200 m3	25 400 000,00 ISK	489 km"
        )
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.cleaned_data["raw_data"].entries), 2)

    def test_parse_ore_data_price_decimal_comma(self):
        raw_data = "Mercoxit III-Grade*	1 433	57 320 m3	24 200 000,00 ISK	488 km"
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertTrue(form.is_valid())
        self.assertEqual(
            form.cleaned_data["raw_data"].entries[0].price_isk, 0.0
        )  # TODO Make Price Test

    def test_parse_ore_data_empty(self):
        form = AddSurveyForm(data={"raw_data": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("raw_data", form.errors)

    def test_parse_ore_data_only_whitespace(self):
        raw_data = "\n\n   \n"
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertFalse(form.is_valid())
        self.assertIn("raw_data", form.errors)

    def test_parse_ore_data_removes_formatting(self):
        raw_data = "Mercoxit III-Grade*	1 433	57 320 m3	24 200 000,00 ISK	488 km"
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertTrue(form.is_valid())
        parsed_entries = form.cleaned_data["raw_data"].entries
        self.assertEqual(parsed_entries[0].units, 1433)
        self.assertEqual(parsed_entries[0].volume_m3, 57320)
        self.assertEqual(parsed_entries[0].price_isk, 0.0)  # TODO Make Price Test

    def test_parse_ore_data_space_separated_german_format(self):
        raw_data = (
            "Dark Ochre III-Grade    371    2.968 m3    1.540.000,00 ISK    2.484 m"
        )
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertTrue(form.is_valid())
        parsed_entries = form.cleaned_data["raw_data"].entries
        self.assertEqual(parsed_entries[0].name, "Dark Ochre III-Grade")
        self.assertEqual(parsed_entries[0].units, 371)
        self.assertEqual(parsed_entries[0].volume_m3, 2968)
        self.assertEqual(parsed_entries[0].price_isk, 0.0)  # TODO Make Price Test

    def test_parse_ore_data_ignores_non_data_info_lines(self):
        raw_data = (
            "Nocxite III-Grade [3] 156 ISK / m³\n"
            "Nocxite III-Grade    45.806    183.224 m3    52.800.000,00 ISK    4.101 m\n"
            "Nocxite IV-Grade [2] 163 ISK / m³\n"
            "Nocxite IV-Grade    67.345    269.380 m3    30.300.000,00 ISK    6.879 m"
        )
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertTrue(form.is_valid())
        parsed_entries = form.cleaned_data["raw_data"].entries
        self.assertEqual(len(parsed_entries), 2)
        self.assertEqual(parsed_entries[0].name, "Nocxite III-Grade")
        self.assertEqual(parsed_entries[0].units, 45806)
        self.assertEqual(parsed_entries[0].volume_m3, 183224)
        self.assertEqual(parsed_entries[0].price_isk, 0.0)  # TODO Make Price Test
        self.assertEqual(parsed_entries[1].name, "Nocxite IV-Grade")
        self.assertEqual(parsed_entries[1].units, 67345)
        self.assertEqual(parsed_entries[1].volume_m3, 269380)
        self.assertEqual(parsed_entries[1].price_isk, 0.0)  # TODO Make Price Test


class TestBeltSurveySessionForm(NoSocketsTestCase):
    """Test BeltSurveySessionForm"""

    def test_form_has_name_field(self):
        form = BeltSurveySessionForm()
        self.assertIn("name", form.fields)

    def test_form_label(self):
        form = BeltSurveySessionForm()
        self.assertEqual(form.fields["name"].label, "Session Name")

    def test_form_help_text(self):
        form = BeltSurveySessionForm()
        self.assertEqual(
            form.fields["name"].help_text,
            "A name to identify this survey session.",
        )

    def test_create_survey_session(self):
        form = BeltSurveySessionForm(data={"name": "Test Session"})
        self.assertTrue(form.is_valid())

    def test_create_survey_session_empty_name(self):
        form = BeltSurveySessionForm(data={"name": ""})
        self.assertFalse(form.is_valid())
