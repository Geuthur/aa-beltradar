# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# Alliance Auth
from allianceauth.services.hooks import get_extension_logger

# AA Belt Radar
from beltradar import __title__
from beltradar.api import schema
from beltradar.models import BeltSurveySession
from beltradar.providers import AppLogger

logger = AppLogger(get_extension_logger(__name__), __title__)


def generate_apex_chart_mining_data(session: BeltSurveySession):
    """
    Generate data for an ApexCharts chart based on survey entries.

    Args:
        session (BeltSurveySession): The survey session containing entries.
    """
    first_snapshot = session.br_snapshots.order_by("timestamp").first()
    last_snapshot = session.br_snapshots.order_by("-timestamp").first()

    # If there are no snapshots, return an empty chart schema
    if not first_snapshot or not last_snapshot:
        return schema.ApexChartSchema()

    # Initialize dictionaries to hold ore categories and their corresponding volume left
    ore_dict = {}
    progress_bar_data: list[float] = []

    # Get the first snapshot data to determine the starting volume for each ore type
    first_data = first_snapshot.asteroids.all()
    # Get the distinct ore categories from the first snapshot
    ore_categories: list[str] = (
        first_data.values_list("eve_type__name", flat=True)
        .order_by("eve_type__name")
        .distinct()
    )
    # Loop through each ore category and calculate the volume left in the first snapshot
    for ore in ore_categories:
        volume_left = (
            first_data.filter(eve_type__name=ore)
            .order_by("eve_type__name")
            .aggregate(models.Sum("volume_left"))["volume_left__sum"]
            or 0
        )
        ore_dict[ore] = volume_left

    # Get the last snapshot data to calculate progress
    last_data = last_snapshot.asteroids.all()
    # Loop through each ore category and calculate the progress percentage based on the starting volume and the volume left in the last snapshot
    for ore in ore_categories:
        # Calculate the volume left for each ore type in the last snapshot
        volume_left = (
            last_data.filter(eve_type__name=ore)
            .order_by("eve_type__name")
            .aggregate(models.Sum("volume_left"))["volume_left__sum"]
            or 0
        )

        # Get the starting volume for the ore type from the first snapshot
        start_volume = ore_dict.get(ore, 0)

        # Calculate the progress percentage for the ore type
        if start_volume > 0:
            progress = round((start_volume - volume_left) / start_volume * 100, 2)
        else:
            progress = 0
        # Append the progress percentage to the progress_bar_data list
        progress_bar_data.append(progress)

    # Return the chart schema with categories and series
    return schema.ApexChartSchema(
        categories=ore_categories,
        series=[
            schema.ApexChartSeriesDataSchema(
                name=str(_("Mined %")),
                data=progress_bar_data,
            )
        ],
    )


def generate_apex_chart_traffic_data(session: BeltSurveySession):
    """
    Generate data for an ApexCharts chart based on survey entries.

    Args:
        session (BeltSurveySession): The survey session containing entries.
    """
    categories = []
    volume_left = []
    rate_per_s = []
    series: list[schema.ApexChartSeriesDataSchema] = []

    # Loop through each snapshot and collect data for the chart
    for snapshot in session.br_snapshots.order_by("timestamp"):
        # Append the timestamp of the snapshot to the categories list
        categories.append(snapshot.timestamp.strftime("%Y-%m-%d %H:%M:%S"))
        # Append the volume left
        volume_left.append(round(snapshot.belt_size_m3, 0))
        # Append the rate per second
        rate = round(session.br_snapshots.rate_per_s_for_snapshot(snapshot), 0)
        logger.debug(f"Rate for snapshot {snapshot.timestamp}: {rate}")
        rate_per_s.append(rate)

    # Create series data for the chart
    series.append(
        schema.ApexChartSeriesDataSchema(
            name=str(_("Volume Left (m³)")), data=volume_left, type="column"
        )
    )
    series.append(
        schema.ApexChartSeriesDataSchema(
            name=str(_("Speed (m³/s)")), data=rate_per_s, type="line"
        )
    )

    # Return the chart schema with categories and series
    return schema.ApexChartSchema(
        categories=categories,
        series=series,
    )
