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
from beltradar.api.schema import OreSchema, OreSchemaResponse
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

    @staticmethod
    def _normalize_integer_token(token: str, *, trim_decimal: bool = False) -> str:
        """
        Normalize a numeric token by removing whitespace/group separators.

        If trim_decimal is True, trailing decimal places are removed first
        (e.g. "24 200 000,00" -> "24200000").
        """
        normalized = re.sub(pattern=r"[\s\u00A0\u202F]+", repl="", string=token)

        if trim_decimal:
            # Strip trailing decimal part before removing separators.
            # If only '.' exists and 3 digits follow, treat it as a thousands group.
            if "," in normalized:
                normalized = re.sub(pattern=r",\d+$", repl="", string=normalized)
            elif "." in normalized:
                decimal_match = re.search(pattern=r"\.(\d+)$", string=normalized)

                if decimal_match and len(decimal_match.group(1)) != 3:
                    normalized = normalized[: decimal_match.start()]

        return normalized.replace(",", "").replace(".", "")

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

        form_errors = []
        for idx, line in enumerate(cleaned.splitlines(), start=1):
            line = line.strip()
            if not line:
                continue

            # Support both tab-separated and multi-space-separated exports.
            parts = [p.strip() for p in line.split("\t") if p.strip()]

            if len(parts) < 5:
                parts = [
                    p.strip()
                    for p in re.split(pattern=r"\s{2,}", string=line)
                    if p.strip()
                ]

            if len(parts) < 5:
                msg = f"Line {idx} is invalid with: {line}"
                form_errors.append(msg)
                continue  # skip lines that don't have enough columns, but don't fail the entire form

            # Parse numeric fields with error handling
            try:
                name = parts[0]
                units = int(self._normalize_integer_token(parts[1]))
                volume_m3 = int(self._normalize_integer_token(parts[2]))
                price_isk = int(
                    self._normalize_integer_token(parts[3], trim_decimal=True)
                )
            except Exception as e:  # pylint: disable=broad-except
                msg = f"Line {idx} has invalid numeric data: {e}"
                form_errors.append(msg)
                continue  # skip lines with invalid numeric data, but don't fail the entire form

            item = {
                "name": name,
                "units": units,
                "volume_m3": volume_m3,
                "price_isk": price_isk,
                "timestamp": timestamp,
                "snapshot": unique_hash,
            }
            items.append(OreSchema(**item))
        return OreSchemaResponse(erros=form_errors, entries=items)

    def clean(self):
        # Start with the default cleaning to populate cleaned_data
        cleaned_data = super().clean()

        if self.errors:
            return cleaned_data

        # Parse once and expose both compatibility attributes and cleaned_data values.
        parsed_result = self.parse_ore_data()
        self.parsed_items = parsed_result.entries
        self.parse_errors = parsed_result.erros
        cleaned_data["parsed_items"] = parsed_result.entries
        cleaned_data["parse_errors"] = parsed_result.erros
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
