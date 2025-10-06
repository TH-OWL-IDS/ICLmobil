import pytest

from .fixtures import api_url, django_client, ensure_superuser
from ..enum import OptionType, BookingState
from ..models import Booking, WalletEntry


@pytest.mark.django_db
def test_co2e_rrive(api_url, django_client):
    u1 = 'user1'
    user = ensure_superuser(u1, u1)
    # assert django_client.login(username=u1, password=u1)

    distance_m = 1234
    g_per_km = 166

    b = Booking.objects.create(
        user=user,
        trip_mode=OptionType.rriveUse.value,
        state=BookingState.finished.value,
        provider_id='rriveId12345',
        external_distance_m=distance_m,
    )
    b.update_wallet()
    wes = WalletEntry.objects.filter(
        wallet=WalletEntry.Wallets.CO2e,
        unit=WalletEntry.Units.g_CO2e,
        user=user,
        booking=b
    ).all()
    assert len(wes) == 1, [we for we in WalletEntry.objects.all()]
    we = wes[0]

    assert (we.quantity - (distance_m * g_per_km / 1000)) < 1, \
        f"Distance is {distance_m}m, {g_per_km}g/km; quantitiy is {we.quantity}"  # Car: 166 g CO2e/km
