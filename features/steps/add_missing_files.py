from behave import given

@given(u'an incomplete book in preservation')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given an incomplete object in preservation')

@when(u'the Collection Manager submits a package with a single page and updated metadata')
def step_impl(context):
    raise NotImplementedError(u'STEP: When the Collection Manager submits a package with a single page and updated metadata')

@then(u'the page and metadata are staged for preview')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the page and metadata are staged for preview')
