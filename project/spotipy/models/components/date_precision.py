import enum

from spotipy.models import base


class DatePrecision(str, enum.Enum):
    """
    Precision with which a date is known.
    """

    YEAR  = "year"
    MONTH = "month"
    DAY   = "day"


class DatePrecisionItem(base.SpotifyBaseItem[DatePrecision]):
    """
    Represents a `date_precision`
    object.
    """

    @base.validator("value")
    def validate_precion(cls, value):
        return DatePrecision(value)
