Feature: Store Resource

  In order to preserve a monograph from the Toledo War Diaries
  As a Collection Manager
  I want to store and release the scanned pages, OCR, and metadata.

  We are using resource as a term for the thing we are preserving, i.e. representation, digital object, etc.

  Scenario: Storing a new resource for immediate release
    Given a package containing the scanned pages, OCR, and metadata
    When the Collection Manager places the packaged resource in the incoming location
    Then the Collection Manager can see that it was preserved.

