Feature: Test Metadata

  # Scenario: Test a document that has access rights
  #   Given we have an article with access rights
  #   When add the article with access rights
  #   Then delete the document and access rights

  Scenario: Test a document that has no access rights
    Given we have a document with no access rights
    When add the document without access rights
    Then delete the document without access rights

  Scenario: Retire a document
    Given we have a document that needs to be retired
    When retire the document
    Then verify the document status is updated to retired

  Scenario: List all documents
    Given we have multiple documents stored
    When list all documents
    Then verify the documents are listed

  Scenario: Retrieve a specific document by ID
    Given we have a specific document to retrieve
    When retrieve the document by id
    Then verify the correct document is retrieved

  # Scenario: Get details of a document by ID
  #   Given a DocumentManager instance
  #   And a document ID
  #   When the get method is called in metadata
  #   Then the result should be the document details

  # Scenario: Get a list of all documents
  #   Given a DocumentManager instance
  #   When the list method is called in metadata
  #   Then the result should be a list of documents

  # Scenario: Save a new document
  #   Given a DocumentManager instance
  #   And a new document
  #   When the save method is called for a new document in metadata
  #   Then the document should be added to the session