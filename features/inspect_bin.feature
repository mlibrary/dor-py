Feature: Inspect Bin

  does the repository have a bin for an identifier?
  what files are in the bin?

  In order to confirm that a monnograph is in the repository
  As a Collection Manager
  I want to find an associated bin using my local identifier.

  In order to confirm all pages for a monograph are preserved
  As a Collection Manager
  I want to review the contents of its bin.

  Scenario: Revision summary
    Given a preserved monograph with an alternate identifier of "xyzzy:00000001"
    When the Collection Manager looks up the bin by "xyzzy:00000001"
    Then the Collection Manager sees the summary of the bin

  Scenario: Revision file sets
    Given a preserved monograph with an alternate identifier of "xyzzy:00000001"
    When the Collection Manager lists the contents of the bin for "xyzzy:00000001"
    Then the Collection Manager sees the file sets.
