Feature: Adding Missing Files

  In order to remediate a monograph found to be missing page scans
  As a Collection Manager
  I want to update to the object with the missing assets and metadata

  A reader reported that a page was missing in a 19th-century textbook.
  Curator Sally forgot to include the scan of the book's appendix.

  Scenario: adding a single page and associated metadata for previewing
    Given an incomplete book in preservation
    When the Collection Manager submits a package with a single page and updated metadata
    Then the page and metadata are staged for preview

  Scenario: adding a single page and its metadata for immediate release
