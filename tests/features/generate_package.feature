Feature: Generate Package

  The BHL Image Bank metadata dump is a FileMaker export.
  DCS will transforms this into a packager unit of work file (JSONL) using DCS-PREP tooling.

  In order to process an item from a BHL Image Bank metadata dump,
  As a Collection Manager
  I want to generate a submission package based on
  some package metadata.

  Scenario: Generate submission information package
    Given package metadata and file sets in pending
    When the Collection Manager invokes the package generator
    Then the submission package is generated in the inbox
    And the Collection Manager gets notified upon completion
