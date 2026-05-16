# Standard Library
import hashlib
import re
from decimal import Decimal, InvalidOperation

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


class OreBatchImportForm(forms.Form):
    raw_data = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 20, "cols": 80}),
        label="Mining Survey Result Data",
        help_text="Paste the 'Mining Survey Result' data here.",
    )

    def parse_ore_data(self):
        """
        Parse the `raw_data` textarea and return a list of items.

        Handles lines separated by CR/LF, tabs or multiple spaces and normalises
        German-style numbers like "292 000,00 ISK".
        """
        raw_data = self.cleaned_data.get("raw_data", "") or ""
        items = []

        # normalize NBSP and strip trailing ISK markers
        raw_data = raw_data.replace("\xa0", " ")

        # Generate a unique hash of the raw data to identify this snapshot
        unique_hash = hashlib.sha256(raw_data.encode("utf-8")).hexdigest()

        for idx, line in enumerate(raw_data.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue

            # Prefer tab-separated columns if present
            if "\t" in line:
                parts = [p.strip() for p in line.split("\t") if p.strip()]
            else:
                # Fallback: split on 2+ spaces
                parts = [p.strip() for p in re.split(r"\s{2,}", line) if p.strip()]

            if len(parts) < 5:
                raise forms.ValidationError(
                    message=f"Line {idx} is invalid: expected at least 5 columns but got {len(parts)}"
                )

            name = parts[0].replace("*", "").strip()  # remove * from ores if present

            def to_int(s):
                s = s.replace("\xa0", " ")
                # remove common unit suffixes that may contain digits (eg. 'm3')
                s = re.sub(r"(?i)m3|m³|km", "", s)
                digits = re.sub(r"[^0-9]", "", s)
                return int(digits) if digits else 0

            def to_decimal_isk(s):
                # remove currency label and thousand separators, convert comma->dot
                s = s.upper().replace("ISK", "").strip()
                s = s.replace(" ", "")
                # remove dots used as thousand separators as well
                s = s.replace(".", "")
                s = s.replace(",", ".")
                try:
                    return Decimal(s)
                except (InvalidOperation, ValueError):
                    return Decimal(0)

            try:
                units = to_int(parts[1])
                volume_m3 = to_int(parts[2])
                price_isk = to_decimal_isk(parts[3])
            except Exception as e:  # pylint: disable=broad-except
                logger.debug(
                    f"[Beltradar] Error parsing numeric fields on line {idx}: {e}"
                )
                continue

            item = {
                "name": name,
                "units": units,
                "volume_m3": volume_m3,
                "price_isk": price_isk,
                "timestamp": timezone.now(),
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
