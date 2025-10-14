Feature: Test Super Search

  Scenario: Ingest articles for SuperSearch
    Given we get a list of articles from SpeedPerform
    When we get current document metadata
    Then we compare the differences between the list 

  Scenario: Add articles to index
    Given we have a set of articles
    When we add them to the search index
    Then they exist in the metadata

  Scenario: Update articles to index
    Given we have a set of articles
    When we update them to the search index
    Then they exist in the metadata
  
  Scenario: Delete articles in index
    Given we have a set of articles
    When we delete them to the search index
    Then they exist in the metadata

  # Scenario: Call OpenAI API and get generated question
  #   Given a QuestionGenerator instance
  #   And a system message, user message, and context
  #   When the OpenAI API is called
  #   Then the result should be the generated question

  # Scenario: Generate a question based on the context
  #   Given a QuestionGenerator instance
  #   And a content message
  #   When the generate method is called
  #   Then the result should be the generated question

  # Scenario: Get a list of all article metadata
  #   Given a SpeedPerformAPI instance
  #   When the list method is called
  #   Then the result should be a list of articles

  # Scenario: Get details of an article by ID
  #   Given a SpeedPerformAPI instance
  #   And an article ID
  #   When the get method is called
  #   Then the result should be the article details    