Feature: Generate Packages

  The BHL Image Bank metadata dump is a FileMaker export.
  DCS will transforms this into a packager unit of work file (JSONL) using DCS-PREP tooling.

  In order to process a BHL Image Bank metadata dump,
  As a Collection Manager
  I want to generate submission packages based on
  this dump (JSONL format)

  Scenario: Generate submission information packages
    Given a JSONL dump file and file sets in pending
    When the Collection Manager invokes the packager
    Then the submission packages are generated in the inbox
    And the Collection Manager gets notified upon completion of the batch
