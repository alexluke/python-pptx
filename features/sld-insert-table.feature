Feature: Insert a table in a slide placeholder
  In order to display well-placed tabular content
  As a presentation developer
  I need the ability to place a table inside a table placeholder

  Scenario: Insert a table into a placeholder
     Given I have a reference to a slide with a table placeholder
       And a table placeholder shape
      When I insert a table into the placeholder
       And I save the presentation
      Then the table appears in the slide

