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
        raw_data = "Mercoxit III-Grade*\t1433\t57320 m3\t24200000 ISK\t488 km"
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.parsed_items), 1)
        self.assertEqual(form.parsed_items[0].name, "Mercoxit III-Grade")
        self.assertEqual(form.parsed_items[0].units, 1433)
        self.assertEqual(form.parsed_items[0].volume_m3, 57320)
        self.assertEqual(form.parsed_items[0].price_isk, 24200000)

    def test_parse_ore_data_multiple_rows(self):
        raw_data = (
            "Mercoxit III-Grade*	1 433	57 320 m3	24 200 000,00 ISK	488 km\n"
            "Mercoxit III-Grade*	1 505	60 200 m3	25 400 000,00 ISK	489 km"
        )
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertTrue(form.is_valid())
        self.assertEqual(len(form.parsed_items), 2)

    def test_parse_ore_data_price_decimal_comma(self):
        raw_data = "Mercoxit III-Grade*\t1 433\t57 320 m3\t24 200 000,00 ISK\t488 km"
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.parsed_items[0].price_isk, 24200000)

    def test_parse_ore_data_invalid_columns(self):
        raw_data = "Mercoxit III-Grade*	1 433	57 320 m3	24 200 000,00 ISK"
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_parse_ore_data_invalid_numeric(self):
        raw_data = "Mercoxit III-Grade*	1 433	invalid_volume	24 200 000,00 ISK	488 km"
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_parse_ore_data_empty(self):
        form = AddSurveyForm(data={"raw_data": ""})
        self.assertFalse(form.is_valid())

    def test_parse_ore_data_only_whitespace(self):
        raw_data = "\n\n   \n"
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertFalse(form.is_valid())
        self.assertIn("raw_data", form.errors)

    def test_parse_ore_data_removes_formatting(self):
        raw_data = "Mercoxit III-Grade*	1 433	57 320 m3	24 200 000,00 ISK	488 km"
        form = AddSurveyForm(data={"raw_data": raw_data})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.parsed_items[0].units, 1433)
        self.assertEqual(form.parsed_items[0].volume_m3, 57320)
        self.assertEqual(form.parsed_items[0].price_isk, 24200000)


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
