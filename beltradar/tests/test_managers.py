# Standard Library
from decimal import Decimal

# Third Party
import pook
from evesde_factory.eve_sde import ItemTypeFactory

# Django
from django.utils import timezone

# AA Belt Radar
from beltradar.models import EveMarketPrice
from beltradar.tests import BeltRadarTestCase


class TestEveMarketPriceManagerUpdateFromEsi(BeltRadarTestCase):
    """Test EveMarketPrice.objects.update_from_esi against the ESI endpoint."""

    ESI_URL = "https://esi.evetech.net/markets/prices"

    @pook.on
    def test_should_create_price_without_adjusted_price(self):
        # given
        eve_type = ItemTypeFactory()
        pook.get(
            self.ESI_URL,
            reply=200,
            response_json=[{"average_price": 150.5, "type_id": eve_type.id}],
        )
        # when
        result = EveMarketPrice.objects.update_from_esi()
        # then
        self.assertEqual(result, 1)
        price = EveMarketPrice.objects.get(eve_type=eve_type)
        self.assertEqual(price.average_price, Decimal("150.50"))
        self.assertIsNone(price.adjusted_price)

    @pook.on
    def test_should_update_price_without_adjusted_price(self):
        # given
        eve_type = ItemTypeFactory()
        EveMarketPrice.objects.create(
            eve_type=eve_type,
            average_price=Decimal("100.00"),
            adjusted_price=Decimal("90.00"),
            updated_at=timezone.now(),
        )
        pook.get(
            self.ESI_URL,
            reply=200,
            response_json=[{"average_price": 150.5, "type_id": eve_type.id}],
        )
        # when
        result = EveMarketPrice.objects.update_from_esi()
        # then
        self.assertEqual(result, 1)
        price = EveMarketPrice.objects.get(eve_type=eve_type)
        self.assertEqual(price.average_price, Decimal("150.50"))
        self.assertIsNone(price.adjusted_price)

    @pook.on
    def test_should_skip_unknown_type_and_store_known_types(self):
        # given
        known_type = ItemTypeFactory()
        new_type = ItemTypeFactory()
        unknown_type_id = new_type.id + 1000
        EveMarketPrice.objects.create(
            eve_type=known_type,
            average_price=Decimal("100.00"),
            adjusted_price=Decimal("90.00"),
            updated_at=timezone.now(),
        )
        pook.get(
            self.ESI_URL,
            reply=200,
            response_json=[
                {
                    "adjusted_price": 190.0,
                    "average_price": 200.0,
                    "type_id": known_type.id,
                },
                {
                    "adjusted_price": 290.0,
                    "average_price": 300.0,
                    "type_id": unknown_type_id,
                },
                {
                    "adjusted_price": 390.0,
                    "average_price": 400.0,
                    "type_id": new_type.id,
                },
            ],
        )
        # when
        result = EveMarketPrice.objects.update_from_esi()
        # then
        self.assertEqual(result, 2)
        self.assertEqual(
            EveMarketPrice.objects.get(eve_type=known_type).average_price,
            Decimal("200.00"),
        )
        self.assertEqual(
            EveMarketPrice.objects.get(eve_type=new_type).average_price,
            Decimal("400.00"),
        )
        self.assertFalse(
            EveMarketPrice.objects.filter(eve_type_id=unknown_type_id).exists()
        )
