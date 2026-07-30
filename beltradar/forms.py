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
from beltradar.models import BeltSurveySession, BeltTimer
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


class DeleteBeltTimerForm(forms.Form):
    """
    Form to confirm belt timer deletion.
    """

    class Meta:
        fields = ["timer_id"]


class AddSurveyForm(forms.Form):
    raw_data = forms.CharField(
        widget=forms.Textarea(attrs={"rows": 20, "cols": 80}),
        label="Mining Survey Result Data",
        help_text="Paste the 'Mining Survey Result' data here.",
        required=True,
    )

    def sanatize_raw_data(self, raw_data: str) -> str:
        """Sanatize and parse the raw data input, returning a structured list of OreSchema items."""
        if not raw_data:
            return ""

        timestamp = timezone.now().replace(microsecond=0)

        # Generate a unique hash of the raw data to identify this snapshot
        unique_hash = hashlib.sha256(
            raw_data.encode("utf-8") + str(timestamp).encode("utf-8")
        ).hexdigest()

        processed_lines = []
        unit_pattern = r"(?i)\b(isk|km|m3|m³|m)\b|[\s\u00A0\u202F.,-]+"
        form_errors = []

        for line in raw_data.splitlines():
            line = line.strip()

            if not line:
                form_errors.append("Empty line skipped.")
                continue

            # Skip informational lines like: "Nocxite III-Grade [3] 156 ISK / m³"
            if re.search(
                pattern=r"\[\d+\]\s+\d+\s+ISK\s*/\s*m[³3]",
                string=line,
                flags=re.IGNORECASE,
            ):
                form_errors.append(f"Unknown line skipped: {line}")
                continue

            parts = [p.strip() for p in line.split("\t") if p.strip()]
            if len(parts) < 4:
                parts = [
                    p.strip()
                    for p in re.split(pattern=r"\s{2,}", string=line)
                    if p.strip()
                ]

            if len(parts) < 4:
                form_errors.append(f"Line skipped due to insufficient columns: {line}")
                continue

            name = parts[0].replace("*", "").strip()
            units = re.sub(pattern=unit_pattern, repl="", string=parts[1]).strip()
            volume = re.sub(pattern=unit_pattern, repl="", string=parts[2]).strip()
            # price = re.sub(pattern=unit_pattern, repl="", string=parts[3]).strip() # Original line
            price = "0"

            if not (name and units and volume and price):
                form_errors.append(f"Line skipped due to missing data: {line}")
                continue

            item = {
                "name": name,
                "units": units,
                "volume_m3": volume,
                "price_isk": price,
                "timestamp": timestamp,
                "snapshot": unique_hash,
            }

            processed_lines.append(OreSchema(**item))
        return OreSchemaResponse(erros=form_errors, entries=processed_lines)

    def clean_raw_data(self):
        """
        Clean and parse the raw data input, returning a structured list of OreSchema items.
        """
        return self.sanatize_raw_data(raw_data=self.cleaned_data["raw_data"])


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


class BeltTimerForm(forms.ModelForm):
    class Meta:
        model = BeltTimer
        fields = ["belt_id", "belt_name", "belt_type", "belt_size"]
        labels = {
            "belt_id": "Belt ID",
            "belt_name": "Belt Name",
            "belt_type": "Belt Type",
            "belt_size": "Belt Size",
        }
        help_texts = {
            "belt_id": "The unique identifier for this belt timer. (This is usually the belt's ID in the game.)",
            "belt_name": "The name of the belt.",
            "belt_type": "The type of belt.",
            "belt_size": "The size of the belt.",
        }
