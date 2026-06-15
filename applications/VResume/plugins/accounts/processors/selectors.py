from ..models import Branch as branchModel
from ..models import Corporate as corporateModel

# from ..models.schemas import Branch, Corporate
from .filters import BranchFilter, CorporateFilter


def get_filtered_branches(filters=None):
    """
    Selector to fetch Branch objects with applied filters.

    :param filters: A dictionary of filter criteria.
    :return: A list of serialized BranchSchema data.
    """
    # Ensure filters is a dictionary
    filters = filters.dict() if hasattr(filters, "dict") else filters or {}
    queryset = branchModel.objects.all()

    return BranchFilter(filters, queryset=queryset).qs


def get_filtered_corporates(filters=None):
    """
    Selector to fetch corporates based on filters.

    :param filters: A dictionary of filter criteria.
    :return: A list of serialized CorporateSchema data.
    """
    filters = filters.dict() if hasattr(filters, "dict") else filters or {}
    queryset = corporateModel.objects.all()
    return CorporateFilter(filters, queryset=queryset).qs
