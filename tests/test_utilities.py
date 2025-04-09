from dor.providers.utilities import sanitize_basename


def test_sanitize_basename_forces_lowercase_and_removes_spaces():
    assert r"tolowerlettersnumbers0-1.2_3+4plus+signhypens-underscores_and.dots..." == sanitize_basename(
        r"To Lower LeTtErS Numbers 0-1.2_3+4 Plus + Sign Hypens - Under Scores _ AND . Dots ...")


def test_sanitize_basename_removes_unwanted_characters():
    assert r"tolowerlettersnumbers0-1.2_3+4plus+signhypens-underscores_and.dots..." == sanitize_basename(
        r"To ~ L!ower @Le\T#t\"ErS; N$u'mbe%rs 0^-1.2_3&+4 P*lu:s + (Sign) Hyp=ens - U{nd}er [Sc]or?es/ _ A,ND . D<ot>s ...")
