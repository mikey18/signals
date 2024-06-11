from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from .managers import CustomUserManager
from .utils import generate_id


class TradingPair(models.TextChoices):
    # Major Currency Pairs
    EUR_USD = 'EUR/USD', 'Euro/US Dollar'
    USD_JPY = 'USD/JPY', 'US Dollar/Japanese Yen'
    GBP_USD = 'GBP/USD', 'British Pound/US Dollar'
    USD_CHF = 'USD/CHF', 'US Dollar/Swiss Franc'
    USD_CAD = 'USD/CAD', 'US Dollar/Canadian Dollar'
    AUD_USD = 'AUD/USD', 'Australian Dollar/US Dollar'
    NZD_USD = 'NZD/USD', 'New Zealand Dollar/US Dollar'

    # Minor Currency Pairs
    EUR_GBP = 'EUR/GBP', 'Euro/British Pound'
    EUR_JPY = 'EUR/JPY', 'Euro/Japanese Yen'
    GBP_JPY = 'GBP/JPY', 'British Pound/Japanese Yen'
    AUD_JPY = 'AUD/JPY', 'Australian Dollar/Japanese Yen'
    NZD_JPY = 'NZD/JPY', 'New Zealand Dollar/Japanese Yen'
    AUD_NZD = 'AUD/NZD', 'Australian Dollar/New Zealand Dollar'
    AUD_CAD = 'AUD/CAD', 'Australian Dollar/Canadian Dollar'
    GBP_AUD = 'GBP/AUD', 'British Pound/Australian Dollar'
    GBP_CAD = 'GBP/CAD', 'British Pound/Canadian Dollar'
    EUR_AUD = 'EUR/AUD', 'Euro/Australian Dollar'

    # Exotic Currency Pairs
    USD_SGD = 'USD/SGD', 'US Dollar/Singapore Dollar'
    USD_HKD = 'USD/HKD', 'US Dollar/Hong Kong Dollar'
    USD_TRY = 'USD/TRY', 'US Dollar/Turkish Lira'
    USD_MXN = 'USD/MXN', 'US Dollar/Mexican Peso'
    USD_ZAR = 'USD/ZAR', 'US Dollar/South African Rand'
    USD_SEK = 'USD/SEK', 'US Dollar/Swedish Krona'
    USD_DKK = 'USD/DKK', 'US Dollar/Danish Krone'
    USD_NOK = 'USD/NOK', 'US Dollar/Norwegian Krone'
    USD_INR = 'USD/INR', 'US Dollar/Indian Rupee'
    USD_THB = 'USD/THB', 'US Dollar/Thai Baht'

    # Regional Currency Pairs
    EUR_CHF = 'EUR/CHF', 'Euro/Swiss Franc'
    EUR_CAD = 'EUR/CAD', 'Euro/Canadian Dollar'
    EUR_NZD = 'EUR/NZD', 'Euro/New Zealand Dollar'
    GBP_CHF = 'GBP/CHF', 'British Pound/Swiss Franc'
    CAD_JPY = 'CAD/JPY', 'Canadian Dollar/Japanese Yen'
    NZD_CAD = 'NZD/CAD', 'New Zealand Dollar/Canadian Dollar'

    # Precious Metals
    XAU_USD = 'XAU/USD', 'Gold/US Dollar'
    XAG_USD = 'XAG/USD', 'Silver/US Dollar'
    XPT_USD = 'XPT/USD', 'Platinum/US Dollar'
    XPD_USD = 'XPD/USD', 'Palladium/US Dollar'

class TimeFrame(models.TextChoices):
    # TICK = 'tick', 'Tick'
    SECOND_1 = '1s', '1 Second'
    MINUTE_1 = '1m', '1 Minute'
    MINUTE_5 = '5m', '5 Minutes'
    MINUTE_15 = '15m', '15 Minutes'
    MINUTE_30 = '30m', '30 Minutes'
    HOUR_1 = '1h', '1 Hour'
    HOUR_4 = '4h', '4 Hours'
    DAY_1 = '1d', '1 Day'
    WEEK_1 = '1w', '1 Week'
    MONTH_1 = '1mo', '1 Month'

class User(AbstractUser):
    id  = models.CharField(primary_key=True, default=generate_id, max_length=64)
    email = models.EmailField(_("email address"), unique=True)
    fullname = models.CharField(max_length=150)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    pair = models.CharField(max_length=100, choices=TradingPair.choices, verbose_name='Trading Pair', blank=True)
    time_frame = models.CharField(max_length=50, choices=TimeFrame.choices, verbose_name='Time Frame', blank=True)

    username = None
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['fullname']

    objects = CustomUserManager()

    def __str__(self):
        return self.email