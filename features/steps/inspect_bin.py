from behave import given, then, when

@given(u'a preserved monograph with an alternate identifier')
def step_impl(context):
    raise NotImplementedError(u'STEP: Given a preserved monograph with an alternate identifier')


@when(u'the Collection Manager looks up the bin by the identifier')
def step_impl(context):
    raise NotImplementedError(u'STEP: When the Collection Manager looks up the bin by the identifier')


@then(u'the Collection Manager sees the summary of the bin')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the Collection Manager sees the summary of the bin')


@when(u'the Collection Manager lists the contents of the bin')
def step_impl(context):
    raise NotImplementedError(u'STEP: When the Collection Manager lists the contents of the bin')


@then(u'the Collection Manager sees the file sets.')
def step_impl(context):
    raise NotImplementedError(u'STEP: Then the Collection Manager sees the file sets.')