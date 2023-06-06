import enum


class SortResultEnum(enum.Enum):
    """
    Enum values for performing sort on results
    """

    asc = "asc"
    desc = "desc"


class StatusEnum(enum.Enum):
    """
    Enum class for assigning status to objects
    """

    active = "active"
    inactive = "inactive"
    blocked = "blocked"
    disabled = "disabled"


class RegularExpression(enum.Enum):
    phone_number = r"((\+?233)((2)[03467]|(5)[045679])\d{7}$)|(((02)[03467]|(05)[045679])\d{7}$)"  # noqa
    pin = r"([0-9]{4}$)"
    token = r"([0-9]{6}$)"
