Feature: Update Resource

  In order to update a preserved monograph from the Toledo War Diaries
  As a Collection Manager
  I want to update and release the modified scanned pages, OCR, and metadata.

  We are using resource as a term for the thing we are preserving, i.e. representation, digital object, etc.

  Scenario: Updating a resource for immediate release
    Given a package containing all the scanned pages, OCR, and metadata
    When the Collection Manager places the packaged resource in the incoming location
    Then the Collection Manager can see that it was revised.

  Scenario: Updating only metadata of a resource for immediate release
    Given a package containing updated resource metadata
    When the Collection Manager places the metadata packaged resource in the incoming location
    Then the Collection Manager can see that it was revised.
