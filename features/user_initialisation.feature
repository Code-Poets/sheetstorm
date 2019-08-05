Feature: Sign up

  Scenario: Employee
    When the user signs up
    Then the user should have 'Employee' status

  Scenario: Manager
    Given an admin exists in database
    When the user signs up
    And admin changes user's employee type to 'Manager'
    Then the user should have 'Manager' status
    And the user should have access to 'Projects' page

  Scenario: Admin
    Given an admin exists in database
    When the user signs up
    And admin changes user's employee type to 'Admin'
    Then the user should have 'Admin' status
    And the user should have access to 'Employees' page
