Feature: Order Registry

Scenario: Succesfully registering a valid digital order
    Given Active registry is empty
    And History registry is empty
    When I create a digital order for "I see red" with email "test@example.com"
    Then The order should be present in active registry
    And The order should have a unique ID assigned
    And The order status should be pending
    And Number of orders in active registry should be 1
    And Number of orders in history registry should be 0

Scenario: Succesfully registering a valid physical order
    Given Active registry is empty
    And History registry is empty
    When I create a physical order for "I see red" with email "test@example.com" and address:
    | field       | value        |
    | housenumber | 57           |
    | flatnumber  | None         |
    | street      | Wita Stwosza |
    | postcode    | 80-308       |
    | city        | Gdańsk       |
    | country     | Polska       |
    Then The order should be present in active registry
    And The order should have a unique ID assigned
    And The order status should be pending
    And The order address should be:
    | field       | value        |
    | housenumber | 57           |
    | flatnumber  | None         |
    | street      | Wita Stwosza |
    | postcode    | 80-308       |
    | city        | Gdańsk       |
    | country     | Polska       |
    And Number of orders in active registry should be 1
    And Number of orders in history registry should be 0

Scenario: Succesfully registering an invalid digital order
    Given Active registry is empty
    And History registry is empty
    When I create a digital order for "I see red" with email "test@test"
    Then The order should be present in history registry
    And The order should have a unique ID assigned
    And The order status should be cancelled
    And Number of orders in active registry should be 0
    And Number of orders in history registry should be 1

Scenario: Succesfully registering an invalid physical order
    Given Active registry is empty
    And History registry is empty
    When I create a physical order for "I see red" with email "test@example.com" and address:
    | field       | value        |
    | housenumber | 10a          |
    | flatnumber  | 7            |
    | street      | Rakietowa    |
    | postcode    | 11-111       |
    | city        | Mars         |
    | country     | Polska       |
    Then The order should be present in history registry
    And The order status should be cancelled
    And The order address should be:
    | field       | value        |
    | housenumber | 57           |
    | flatnumber  | None         |
    | street      | Wita Stwosza |
    | postcode    | 80-308       |
    | city        | Gdańsk       |
    | country     | Polska       |
    And Number of orders in active registry should be 0
    And Number of orders in history registry should be 1

Scenario: Changing email of digital order to valid
    Given Active registry is empty
    And History registry is empty
    And I create a digital order for "I see red" with email "test@example.com"
    When I change the order email to "test2@example.com"
    Then The order email should be "test2@example.com"
    And The order status should be pending

Scenario: Changing email of digital order to invalid
    Given Active registry is empty
    And History registry is empty
    And I create a digital order for "I see red" with email "test@example.com"
    When I change the order email to "test2@example"
    Then The order email should be "test@example.com"
    And The order status should be pending

Scenario: Changing address of physical order to valid
    Given Active registry is empty
    And History registry is empty
    And I create a physical order for "I see red" with email "test@example.com" and address:
    | field       | value        |
    | housenumber | 57           |
    | flatnumber  | None         |
    | street      | Wita Stwosza |
    | postcode    | 80-308       |
    | city        | Gdańsk       |
    | country     | Polska       |
    When I change the order address to:
    | field       | value        |
    | housenumber | 57           |
    | flatnumber  | 2.16         |
    | street      | Wita Stwosza |
    | postcode    | 80-308       |
    | city        | Gdańsk       |
    | country     | Polska       |
    Then The order address should be:
    | field       | value        |
    | housenumber | 57           |
    | flatnumber  | 2.16         |
    | street      | Wita Stwosza |
    | postcode    | 80-308       |
    | city        | Gdańsk       |
    | country     | Polska       |
    And The order status should be pending

Scenario: Changing address of physical order to invalid
    Given Active registry is empty
    And History registry is empty
    And I create a physical order for "I see red" with email "test@example.com" and address:
    | field       | value        |
    | housenumber | 57           |
    | flatnumber  | None         |
    | street      | Wita Stwosza |
    | postcode    | 80-308       |
    | city        | Gdańsk       |
    | country     | Polska       |
    When I change the order address to:
    | field       | value        |
    | housenumber | 10a          |
    | flatnumber  | 7            |
    | street      | Rakietowa    |
    | postcode    | 11-111       |
    | city        | Mars         |
    | country     | Polska       |
    Then The order address should be:
    | field       | value        |
    | housenumber | 57           |
    | flatnumber  | None         |
    | street      | Wita Stwosza |
    | postcode    | 80-308       |
    | city        | Gdańsk       |
    | country     | Polska       |
    And The order status should be pending

Scenario: Cancelling an order
    Given The active registry has 1 digital order
    And History registry is empty
    And The order status should be pending
    When I cancel the order
    Then The order should be present in history registry
    And The order status should be cancelled
    And Number of orders in active registry should be 0
    And Number of orders in history registry should be 1

Scenario: Full life cycle of a digital order
    Given The active registry has 1 digital order
    And History registry is empty
    And The order status should be pending
    When I advance the order status 3 times
    Then The order status should be collected
    And The order should be present in history registry
    And Number of orders in active registry should be 0
    And Number of orders in history registry should be 1

Scenario: Filing a return
    Given History registry has 1 digital order
    And Active registry is empty
    When I file a return
    Then The order status should be returning
    And The order should be present in active registry  
    And Number of orders in active registry should be 1
    And Number of orders in history registry should be 0
    When I advance the order status 1 times
    Then The order status should be returned
    And The order should be present in history registry
    And Number of orders in active registry should be 0
    And Number of orders in history registry should be 1

Scenario: Searching for orders by email
    Given There are orders in the registry:
      | product    | email            | type    |
      | I see red  | user@example.com | digital |
      | Blue Moon  | user@example.com | physical|
      | Green Day  | other@test.com   | digital |
    When I get orders for email "user@example.com"
    Then I should see 2 orders in the results
    And The results should contain products:
      | product    |
      | I see red  |
      | Blue Moon  |