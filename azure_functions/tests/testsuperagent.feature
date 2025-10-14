Feature: Test Super Agent

  # Scenario: Processing Tariffas metadata
  #   Given I have a valid container path for Tariffas
  #   Given I have blob content for Tariffas
  #   When I process the metadata for Tariffas
  #   Then I should get a valid response for Tariffas

  # Scenario: Processing Pages Library metadata
  #   Given I have a valid container path for Pages Library
  #   Given I have blob content for Pages Library
  #   When I process the metadata for Pages Library
  #   Then I should get a valid response for Pages Library

  # Scenario: Processing Tariffas
  #   Given I have blob content for Tariffas
  #   When I process the Tariffas
  #   Then I should get a valid response for Tariffas

  # Scenario: Processing Pages
  #   Given I have blob content for Pages
  #   When I process the Pages
  #   Then I should get a valid response for Pages Library

  Scenario: Processing Equipments
    Given I have blob content for Equipments
    When I process the Equipments
    Then I should get a valid response for Equipments

 Scenario: Processing Notice
    Given I have blob content for Notice
    When I process the Notice
    Then I should get a valid response for Notice

