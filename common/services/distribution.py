from decimal import Decimal  # noqa: F401

from operations.models import Offer, Order


def run_distribution(orders: list[Order], offers: list[Offer]) -> list[dict]:
    """
    Recebe listas de Orders e Offers.
    Retorna uma lista de propostas de distribuição (JSON serializável).
    """
    pass


def redistribute(proposal_json_list: list[dict]) -> list[dict]:
    """
    Recebe uma lista de propostas de distribuição (JSON serializável).
    Retorna uma nova lista com base em ajustes manuais da proposta inicial.
    """
    pass
