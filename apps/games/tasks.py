# Python
import random
from typing import Any
from datetime import date
from decimal import Decimal

# Django
from django.db.models import (
    F,
    query
)

# First party
from games.models import (
    Game,
    Subscribe
)
from settings.celery import app

@app.task(name='game-price-updater')
def game_price_updater(game_id: int, rate: float) -> None:
    """
    Воркер для авто-обновления цен по игре на основе рейтинга.
    """

    def random_value(rate: float) -> Decimal:
        discount_rate = Decimal('0.1') * Decimal(str(rate))
        return Decimal(random.randint(-20, 20)) - discount_rate

    current_date = date.today()
    game = Game.objects.get(id=game_id)
    discount = random_value(rate)

    # Добавление скидки на новый год и 11.11
    if current_date.month == 11 and current_date.day == 11:
        discount += Decimal('30')
    elif current_date.month == 12 and current_date.day == 31:
        discount += Decimal('20')

    new_price = game.price + discount

    if new_price < 0:
        print('Price for game {game.name} is less than 0.')
    else:
        game.price = new_price
        game.save(update_fields=('price',))
        print(f'Price for game {game.name} was updated !!!')



@app.task(
    name='games-price-updater'
)
def games_price_updater(rate: float) -> None:
    """
    Воркер для авто-обновления цен по играм на основе рейтинга.
    """

    def random_value(rate: float) -> Decimal:
        discount_rate = Decimal('0.1') * Decimal(str(rate))
        return Decimal(random.randint(-20, 20)) - discount_rate

    current_date = date.today()
    games = Game.objects.filter(is_hidden=False)
    for game in games:
        discount = random_value(rate)
        # Добавление скидки на новый год и 11.11
        if current_date.month == 11 and current_date.day == 11:
            discount += Decimal('30')
        elif current_date.month == 12 and current_date.day == 31:
            discount += Decimal('20')

        game.price += discount
        game.save(update_fields=('price',))

    print('All games prices were updated !!!')

@app.task(
    name='test-worker'
)
def test_worker(
    game_id: int,
    *args: Any,
    **kwargs: Any
):
    Game.objects.filter(
        id=game_id
    ).update(
        price=F('price') + 10
    )
    print(f'Game: {game_id} price was updated')


@app.task
def cancel_subcribe(
    subcribe_id: int,
    *args: Any,
    **kwargs: Any
) -> None:
    Subscribe.objects.filter(
        id=subcribe_id
    ).update(
        is_active=False
    )