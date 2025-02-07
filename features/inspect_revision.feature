Feature: Inspect Revision

  does the repository have a revision for an identifier?
  what files are in the revision?

  In order to confirm that a monnograph is in the repository
  As a Collection Manager
  I want to find an associated revision using my local identifier.

  In order to confirm all pages for a monograph are preserved
  As a Collection Manager
  I want to review the contents of its revision.

  Scenario: Revision summary
    Given a preserved monograph with an alternate identifier of "xyzzy:00000001"
    When the Collection Manager looks up the revision by "xyzzy:00000001"
    Then the Collection Manager sees the summary of the revision.

  Scenario: Revision file sets
    Given a preserved monograph with an alternate identifier of "xyzzy:00000001"
    When the Collection Manager lists the contents of the revision for "xyzzy:00000001"
    Then the Collection Manager sees the file sets.
