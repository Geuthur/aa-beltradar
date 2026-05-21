# Standard Library
import hashlib
import re

# Django
from django import forms
from django.utils import timezone

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__
from beltradar.api.schema import OreSchema
from beltradar.models import BeltSurveySession
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


class DeleteSnapshotForm(forms.Form):
    """
    Form to confirm snapshot deletion.
    """

    class Meta:
        fields = ["snapshot_id"]


class DeleteSurveyForm(forms.Form):
    """
    Form to confirm survey deletion.
    """

    class Meta:
        fields = ["public_id"]


class AddSurveyForm(forms.Form):
    raw_data = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 20, "cols": 80}),
        label="Mining Survey Result Data",
        help_text="Paste the 'Mining Survey Result' data here.",
        required=True,
    )

    # TODO: Optimize Performance Issues?
    def parse_ore_data(self):
        """
        Parses the raw data from the textarea into a list of OreSchema objects.

        Expects tab-separated values with at least the following columns:
            Name    Units   Volume (m3)    Price (ISK) (additional columns are ignored)
            Example:
            Mercoxit III-Grade*	6 500	260 000 m3	110 000 000,00 ISK	505 km
        """
        raw_data = self.cleaned_data.get("raw_data", "") or ""
        items = []

        # Remove non-data lines and clean up common formatting issues before parsing
        cleaned = re.sub(pattern=r"(?i)m3|m³|km|ISK|\*", repl="", string=raw_data)

        timestamp = timezone.now().replace(microsecond=0)

        # Generate a unique hash of the raw data to identify this snapshot
        unique_hash = hashlib.sha256(
            raw_data.encode("utf-8") + str(timestamp).encode("utf-8")
        ).hexdigest()

        for idx, line in enumerate(cleaned.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue

            # Split lines to parts
            parts = [p.strip() for p in line.split("\t") if p.strip()]

            # Remove extra spaces and commas from parts (e.g. "292 000,00" -> "292000")
            # We only want to remove spaces and commas from numeric fields, so we skip the first part (name) and any parts that are not expected to be numeric.
            parts = (
                [parts[0]]
                + [
                    re.sub(pattern=r"[ \t,]+", repl="", string=part)
                    for part in parts[1:-1]
                ]
                + [parts[-1]]
            )

            if len(parts) < 5:
                raise forms.ValidationError(
                    message=f"Line {idx} is invalid: expected at least 5 columns but got {len(parts)}"
                )

            # Parse numeric fields with error handling
            try:
                name = parts[0]
                units = int(parts[1])
                volume_m3 = int(parts[2])
                price_isk = int(parts[3])
            except Exception as e:  # pylint: disable=broad-except
                raise forms.ValidationError(
                    message=f"Line {idx} has invalid numeric data: {e}"
                )

            item = {
                "name": name,
                "units": units,
                "volume_m3": volume_m3,
                "price_isk": price_isk,
                "timestamp": timestamp,
                "snapshot": unique_hash,
            }
            items.append(OreSchema(**item))
        return items

    def clean_raw_data(self):
        return self.cleaned_data.get("raw_data", "")

    def clean(self):
        cleaned_data = super().clean()
        try:
            parsed = self.parse_ore_data()
        except forms.ValidationError:
            # propagate field-level parsing errors
            raise
        except Exception as e:
            logger.error(f"[Beltradar] Unexpected error parsing raw data: {e}")
            raise forms.ValidationError(
                message="Failed to parse the raw data. Please check the format and try again."
            )

        self.parsed_items = parsed
        if not parsed:
            raise forms.ValidationError("No valid rows found in pasted data.")
        cleaned_data["parsed_items"] = parsed
        return cleaned_data


class BeltSurveySessionForm(forms.ModelForm):
    class Meta:
        model = BeltSurveySession
        fields = ["name"]
        labels = {
            "name": "Session Name",
        }
        help_texts = {
            "name": "A name to identify this survey session.",
        }
