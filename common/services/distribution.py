from collections import defaultdict
from decimal import ROUND_DOWN, Decimal

from .domain import DistributionDict, OfferDict, OrderDict


def distribute(orders: list[OrderDict], offers: list[OfferDict]) -> list[DistributionDict]:
    """
    Recebe listas de Orders e Offers serializados.
    Retorna uma lista de propostas de distribuição (JSON serializável).
    """
    # Inicializa dicionários de controle
    orders_remaining = {order['id']: order['quantity'] for order in orders}
    offers_remaining = {offer['id']: offer['quantity'] for offer in offers}

    # Mapa de ofertas por cooperado e produto
    user_product_supply = {offer['cooperated_id']: defaultdict(Decimal) for offer in offers}
    for offer in offers:
        user_product_supply[offer['cooperated_id']][offer['product_id']] += offer[
            'quantity'
        ]

    # Agrupa ofertas por produto
    product_offers = defaultdict(list)
    for offer in offers:
        product_offers[offer['product_id']].append(offer['id'])

    # Agrupa pedidos por produto
    product_orders = defaultdict(list)
    for order in orders:
        product_orders[order['product_id']].append(order['id'])

    # Índices para lookup rápido
    offers_by_id = {o['id']: o for o in offers}
    orders_by_id = {o['id']: o for o in orders}

    # Lista final de distribuições
    distributions = []

    # Distribui para cada produto
    for product_id in product_orders:
        order_ids = product_orders[product_id]
        offer_ids = product_offers[product_id]
        product_demand_remaining = sum(orders_remaining[order_id] for order_id in order_ids)

        if not offer_ids or product_demand_remaining <= 0:
            continue

        product_allocations = {offer_id: Decimal(0) for offer_id in offer_ids}

        offers_for_fair = [
            {
                'cooperated_id': offers_by_id[offer_id]['cooperated_id'],
                'offer_id': offer_id,
                'remaining': offers_remaining[offer_id],
            }
            for offer_id in offer_ids
        ]

        # Ordena as ofertas por quantidade restante crescente
        offers_for_fair.sort(key=lambda o: o['remaining'])

        # Aloca as ofertas para o produto (fair share)
        while product_demand_remaining > 0 and offers_for_fair:
            n = len(offers_for_fair)
            if n == 0:
                break  # evita divisão por 0
            # Define a menor oferta entre as ofertas restantes
            min_offer = offers_for_fair[0]
            # Se todas as ofertas puderem contribuir com min_offer, aloca todas elas
            if min_offer['remaining'] * len(offers_for_fair) < product_demand_remaining:
                quantity = min_offer['remaining']
                for o in offers_for_fair:
                    o['remaining'] -= quantity
                    product_allocations[o['offer_id']] += quantity
                    product_demand_remaining -= quantity
                offers_for_fair.pop(0)
            # Se não, divide a alocação necessária entre as ofertas restantes
            else:
                quantity = (product_demand_remaining / Decimal(n)).quantize(
                    Decimal('.01'), rounding=ROUND_DOWN
                )
                for o in offers_for_fair:
                    o['remaining'] -= quantity
                    product_allocations[o['offer_id']] += quantity
                    product_demand_remaining -= quantity

        # Cria copia de orders_remaining apenas para o produto
        orders_remaining_copy = {
            order_id: orders_remaining[order_id] for order_id in order_ids
        }

        # Itera pelas ofertas que tiveram alocação no produto
        for offer_id, allocated in product_allocations.items():
            # Se nada foi alocado, continua (proxima oferta)
            if allocated <= 0:
                continue

            # Se a alocação é maior que 0, trabalha com a oferta
            offer = offers_by_id[offer_id]
            active_orders = [oid for oid in order_ids if orders_remaining_copy[oid] > 0]

            while allocated > 0 and active_orders:
                n = len(active_orders)
                share = (allocated / Decimal(n)).quantize(
                    Decimal('.01'), rounding=ROUND_DOWN
                )
                new_active_orders = []

                for order_id in active_orders:
                    need = orders_remaining_copy[order_id]
                    quantity = min(share, need)

                    if quantity > 0:
                        order = orders_by_id[order_id]
                        distributions.append(
                            {
                                'id': None,
                                'offer_id': offer_id,
                                'order_id': order_id,
                                'cooperated_id': offer['cooperated_id'],
                                'quantity': quantity,
                                'total_value': (quantity * order['unit_price']).quantize(
                                    Decimal('.01')
                                ),
                            }
                        )

                        allocated -= quantity
                        orders_remaining_copy[order_id] -= quantity
                        orders_remaining[order_id] -= quantity
                        offers_remaining[offer_id] -= quantity
                        user_product_supply[offer['cooperated_id']][product_id] -= quantity

                    if orders_remaining_copy[order_id] > 0:
                        new_active_orders.append(order_id)

                active_orders = new_active_orders
    return distributions


def redistribute(
    original_proposal_json_list: list[DistributionDict],
    altered_proposal_json_list: list[DistributionDict],
) -> list[DistributionDict]:
    """
    Recebe uma lista de propostas de distribuição (JSON serializável) alterada.
    Retorna uma nova lista com base em ajustes manuais da proposta inicial.
    """
    pass


def fairness(proposal_json_list: list[DistributionDict]) -> list[DistributionDict]:
    """
    Recebe uma lista de propostas de distribuição (JSON serializável).
    Retorna uma nova lista ajustada para garantir o máximo de equidade.
    """
    pass


def run_distribute(
    orders: list[OrderDict], offers: list[OfferDict]
) -> list[DistributionDict]:
    proposal = distribute(orders, offers)
    return fairness(proposal)


def run_redistribute(
    original_proposal_json_list: list[DistributionDict],
    altered_proposal_json_list: list[DistributionDict],
) -> list[DistributionDict]:
    proposal = redistribute(original_proposal_json_list, altered_proposal_json_list)
    return fairness(proposal)
