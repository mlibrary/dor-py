"""Update Resource feature tests."""
from functools import partial


from pytest_bdd import (
    given,
    scenario,
    then,
    when,
)

scenario = partial(scenario, '../update_resource.feature')

@scenario('Updating a resource for immediate release')
def test_updating_a_resource_for_immediate_release():
    """Updating a resource for immediate release."""


@given('a package containing all the scanned pages, OCR, and metadata')
def _():
    """a package containing all the scanned pages, OCR, and metadata."""
    raise NotImplementedError


@when('the Collection Manager places the packaged resource in the incoming location')
def _():
    """the Collection Manager places the packaged resource in the incoming location."""
    raise NotImplementedError


@then('the Collection Manager can see that it was revised.')
def _():
    """the Collection Manager can see that it was revised.."""
    raise NotImplementedError
