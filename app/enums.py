import enum


class QuerySortEnum(enum.Enum):
    """
    Enum values for performing sort on results
    """

    asc = "asc"
    desc = "desc"


class StatusEnum(enum.Enum):
    """
    Enum class for assigning status to objects
    """

    qualified = "qualified"
    unqualified = "unqualified"
    renewal = "renewal"
    new = "new"
    proposal = "proposal"
