# Database Documentation

## Overview
Brief introduction about the database's purpose and general architecture.

## Tables

**Purpose**: Brief description of what this table is used for.

#### Columns
- `column_1` (type): explanation. Any specific values or constraints
- `column_2` (type): explanation. Any specific values or constraints

#### Common Use Cases
1. Use Case 1 : Description
2. Use Case 2 : Description




**accounts**: Manages the chart of accounts for financial accounting, supporting a hierarchical structure with parent-child relationships and financial statement categorization.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the account
- `name` (varchar(50)): Name of the account
- `code` (varchar(50)): Account code identifier
- `details` (varchar(50)): Additional details about the account
- `parent_account` (int): Reference to parent account ID, creates hierarchical structure
- `date_col` (timestamp): Timestamp of account creation, defaults to current timestamp
- `type_col` (varchar(25)): Type of account, defaults to 'normal', also takes the value 'final'
- `final_account` (int): Reference to a final account ID
- `financial_statement` (int): Reference to associated financial statement ID
- `financial_statement_block` (int): Reference to financial statement block ID
- `force_cost_center` (boolean): Flag indicating if cost center is mandatory, defaults to FALSE
- `default_cost_center` (int): Reference to default cost center ID

#### Common Use Cases:
1. Financial Transaction Tracking: Tracking monetary movements between accounts.
2. Invoices Management: Linking invoice's discounts, additions, gifts, added values... to specific accounts, Managing client billing accounts.
3. Manufacturing Tracking: Recording production costs, Managing raw material accounts, Tracking work-in-progress accounts.
4. Inventory Management:Stock account tracking, Warehouse accounting.
5. Financial Reporting: Generating balance sheets and income statements by tracking account movements and balances, monitoring cash flows between accounts, and producing comprehensive financial reports.


**units**: Manages measurement units used in the system for inventory, manufacturing, and other quantity-based operations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the unit
- `name` (varchar(50)): Unique name of the measurement unit

#### Common Use Cases:
1. Inventory Management: Defining base units for stock items
2. Manufacturing: Specifying production units and measurements
3. Purchase/Sales: Recording quantities in appropriate measurement units


**units_conversion**: Manages conversion ratios between different measurement units, enabling automatic conversion between related units.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the conversion record
- `unit1` (int): Reference to the first unit ID
- `unit2` (int): Reference to the second unit ID
- `value_col` (double): Conversion ratio between units, defaults to 1
- `unit1_ordered` (int): Computed column containing the smaller of unit1 and unit2 IDs
- `unit2_ordered` (int): Computed column containing the larger of unit1 and unit2 IDs

#### Common Use Cases:
1. Automatic Unit Conversion: Converting quantities between different units of measurement
2. Inventory Management: Standardizing quantities across different unit specifications
3. Manufacturing: Converting between raw material units and finished product units
4. Reporting: Providing consistent unit measurements across reports


**clients**: Central repository for customers/suppliers information management, storing essential contact details and classification data for business relationships.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the client
- `name` (varchar(50)): Client's business or individual name
- `governorate` (varchar(50)): Administrative region or state of the client's location
- `address` (varchar(50)): Physical location or mailing address
- `email` (varchar(50)): Primary email contact address
- `phone1` (varchar(50)): Primary contact number
- `phone2` (varchar(50)): Secondary contact number
- `phone3` (varchar(50)): Additional contact number
- `phone4` (varchar(50)): Emergency or alternative contact number
- `client_type` (varchar(50)): The type of client, takes values ('customer' or 'supplier')

#### Common Use Cases:
1. Financial Relationship Tracking: Link clients to their accounts, track client balances and manage client payments.


**clients_accounts**: Manages client-specific financial configurations and payment terms, linking clients to various accounting aspects of the business.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the client account configuration
- `used_price` (int): Reference to applicable price tier or list
- `discount` (double): Standard discount rate for the client
- `payment_method` (varchar(50)): Preferred or agreed payment method
- `days_count` (int): Payment terms in days
- `day_col` (varchar(50)): Specific day preferences for payments/processing
- `payment_date` (date): Scheduled or recurring payment date
- `client_account_id` (int): Reference to main account in accounts table
- `discount_account_id` (int): Reference to discount handling account
- `tax_account_id` (int): Reference to tax processing account
- `vat_account_id` (int): Reference to VAT handling account
- `tax_exempt` (boolean): Tax exemption status flag, defaults to false
- `client_id` (int): Unique reference to client record
- `extra_account_id` (int): Reference to additional charges account

#### Common Use Cases:
1. Financial Configuration: Client-specific pricing setup, Custom payment terms management and Tax handling preferences.
2. Accounting Integration: Automated transaction posting, Financial statement preparation and Tax compliance management.
3. Business Operations: Credit terms monitoring, Payment scheduling and Discount policy implementation.


**financial_statement**: Defines the hierarchy and structure of financial statements, enabling the organization of accounts into standardized financial reporting formats.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the financial statement
- `name` (varchar(50)): Name of the financial statement (e.g., "Balance Sheet", "Income Statement")
- `final_financial_statement` (int): Optional self-referential link to parent financial statement, enabling hierarchical statement structures

#### Common Use Cases:
1. Financial Report Organization: Structuring standard financial statements, Creating hierarchical reporting relationships, Organizing consolidated financial reports.
2. Regulatory Compliance: Maintaining standardized reporting formats, Supporting multiple reporting frameworks, Ensuring consistent financial presentation.
3. Account Classification: Grouping accounts by statement type, Managing reporting hierarchies and Supporting multi-level financial analysis.


**financial_statement_block**: Manages subdivisions within financial statements, providing granular organization of financial data into logical sections or blocks.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the statement block
- `name` (varchar(50)): Name of the block (e.g., "Current Assets", "Operating Expenses")
- `financial_statement_id` (int): Reference to parent financial statement, establishing block categorization

#### Common Use Cases:
1. Statement Structure Management: Organizing statement subsections, Creating logical groupings of accounts, Maintaining reporting hierarchies.
2. Financial Analysis: Ratio analysis by statement block, Trend analysis within statement sections, Performance monitoring by business area.
3. Report Generation: Structured financial reporting, Subtotal calculation by block and Comparative analysis between blocks.


**cost_centers**: Manages the organizational cost structure through a hierarchical system of cost allocation business units, enabling detailed cost tracking and analysis across the business for each point.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the cost center
- `name` (varchar(50)): Name of the cost center
- `notes` (varchar(500)): Optional detailed description or additional information
- `type_col` (varchar(50)): Classification of the cost center type, takes values ('normal', 'distribution', 'aggregation')
- `parent` (int): Reference to parent cost center, enabling hierarchical structure
- `changable_division_factors` (boolean): Flag indicating whether distribution factors can be modified, defaults to false
- `date_col` (datetime): Timestamp of cost center creation, defaults to current timestamp

#### Common Use Cases:
1. Cost Allocation Management: Hierarchical cost center structuring, used for organizational accounting and cost allocation.
2. Financial Control: Budget allocation by cost center, Expense tracking and control, Performance measurement by unit.
3. Management Reporting: Cost center profitability analysis, Overhead allocation tracking and Resource utilization monitoring.


**cost_centers_aggregations_distributives**: Manages the distribution and aggregation rules between related/independent cost centers, defining how costs are allocated across the organizational structure.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the distribution rule
- `master_cost_center` (int): Reference to the primary cost center managing the distribution
- `cost_center` (int): Reference to the receiving cost center
- `division_factor` (double): Allocation factor determining the distribution ratio

#### Common Use Cases:
1. Cost Center Relationship Management: Defining hierarchical connections between cost centers for automated cost flows.
2. Allocation Factor Configuration: Managing distribution ratios and allocation rules between linked cost centers.
3. Flexible Allocation Rules: Allowing dynamic adjustment of distribution percentages to reflect organizational changes and support accurate financial reporting and analysis.


**invoice_types**: Manages different types of invoices in the system, categorizing invoices based on their business purpose and type.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the invoice type
- `name` (varchar(50)): Name identifier for the invoice type, take main six values ('buy', 'sell', 'buy_return', 'sell_return', 'input', 'output'), and then user can add more types.
- `type_col` (varchar(50)): Classification of the invoice type, takes values ('input', 'output')

#### Common Use Cases:
1. Invoice Classification: Categorizing different types of invoices (e.g., buy, sell...).
2. Business Process Management: Organizing invoices based on their purpose and workflow (Invoices/Manufacturing/Inventory).
3. Reporting: Filtering and analyzing invoices by type for financial reporting.
4. Invoice Effects: Defining Invoice effects and behaviors for each invoice type. 


**payment_conditions**: Manages payment terms and discount options for client accounts, enabling flexible payment scheduling and incentive structures.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the payment condition
- `client_account_id` (int): Foreign key reference to the client account this payment condition applies to
- `day_number` (int): Number of days for the payment term
- `discount_percent` (int): Optional percentage discount if paid within term, nullable
- `discount_value` (int): Optional fixed discount amount if paid within term, nullable 
- `discount_account_id` (int): Foreign key reference to the account where discounts are recorded, nullable

#### Common Use Cases:
1. Payment Term Management: Setting up customized payment schedules for different clients and accounts
2. Discount Configuration: Defining payment incentives through percentage or fixed amount discounts
3. Financial Planning: Tracking payment terms and potential discounts through 


**receipt_docs**: Manages receipt documents for material transfers between warehouses, tracking quantities, units, and related invoice items.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the receipt document
- `target_warehouse_id` (int): Foreign key reference to the receiving warehouse
- `rejection_warehouse_id` (int): Foreign key reference to the sending warehouse
- `date_col` (date): Date when the receipt was created
- `material_id` (int): Foreign key reference to the transferred material
- `quantity` (double): Amount of material transferred
- `unit_id` (int): Foreign key reference to the unit of measurement
- `invoice_item_id` (int): Optional reference to related invoice item, nullable
- `factory_id` (int): Optional reference to associated factory, nullable

#### Common Use Cases:
1. Inventory Transfer Management: Tracking material movements between warehouses
2. Receipt Documentation: Recording and validating material receipts and transfers
3. Invoice Reconciliation: Linking material receipts to invoice items for accounting purposes


**hr_additional_costs**: Manages additional cost entries related to HR operations, tracking various financial transactions and costs associated with human resources.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the additional cost entry
- `statement_col` (varchar(500)): Detailed description or statement of the additional cost
- `account_id` (int): Reference to the main account where the cost is recorded
- `department_id` (int): Optional reference to the HR department associated with the cost
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting
- `value_col` (double): Monetary value of the additional cost
- `currency_id` (int): Reference to the currency used for the cost
- `date_col` (date): Date when the additional cost was incurred
- `state_col` (varchar(10)): Status of the cost entry, defaults to 'active'

#### Common Use Cases:
1. HR Cost Tracking: Recording and monitoring additional expenses related to human resources
2. Departmental Cost Allocation: Assigning and tracking costs specific to different HR departments
3. Financial Reporting: Including HR-related costs in financial statements and reports


**hr_courses**: Manages training and development courses for employees, tracking course details, providers, costs, and associated financial accounts.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the course entry
- `title` (varchar(250)): Name or title of the training course
- `providor` (varchar(250)): Name of the training provider or institution
- `account_id` (int): Reference to the account for course expense tracking, nullable
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting, nullable
- `cost` (double): Monetary value of the course
- `currency_id` (int): Reference to the currency used for the course cost
- `date_col` (timestamp): Timestamp of course creation, defaults to current timestamp
- `location` (varchar(250)): Physical or virtual location where the course is conducted

#### Common Use Cases:
1. Training Management: Recording and tracking employee training programs and professional development courses
2. Budget Control: Managing training expenses and allocating costs to appropriate accounts


**hr_course_employees**: Manages the relationship between employees and their assigned training courses, tracking course participation and performance metrics.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the course-employee relationship
- `course_id` (int): Foreign key reference to the training course in hr_courses table
- `employee_id` (int): Foreign key reference to the employee in hr_employees table
- `gpa` (double): Optional grade point average or performance score for the course, nullable

#### Common Use Cases:
1. Course Enrollment Management: Tracking which employees are enrolled in specific training courses
2. Performance Tracking: Recording and monitoring employee performance in training programs


**hr_departments**: Manages organizational department structures with their working schedules and associated financial accounts.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the department
- `name` (varchar(250)): Name of the department
- `day_hours` (double): Standard working hours per day for the department
- `account_id` (int): Reference to the main financial account for the department
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting
- `notes` (varchar(250)): Optional additional information about the department
- `work_day_monday` (tinyint(1)): Flag indicating if Monday is a working day, defaults to 0
- `work_day_tuesday` (tinyint(1)): Flag indicating if Tuesday is a working day, defaults to 0
- `work_day_wednesday` (tinyint(1)): Flag indicating if Wednesday is a working day, defaults to 0
- `work_day_thursday` (tinyint(1)): Flag indicating if Thursday is a working day, defaults to 0
- `work_day_friday` (tinyint(1)): Flag indicating if Friday is a working day, defaults to 0
- `work_day_saturday` (tinyint(1)): Flag indicating if Saturday is a working day, defaults to 0
- `work_day_sunday` (tinyint(1)): Flag indicating if Sunday is a working day, defaults to 0

#### Common Use Cases:
1. Department Management: Creating and maintaining organizational structure
2. Schedule Configuration: Setting up department-specific working days and hours
3. Financial Tracking: Managing department-specific accounting and financial records, including salary calculations and payroll processing


**hr_departments_finance**: Tracks financial transactions and records specific to each department.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the financial record
- `department_id` (int): Reference to the associated department
- `statement_col` (varchar(500)): Description or purpose of the financial transaction
- `type_col` (varchar(11)): Type classification of the financial transaction, takes values ('addition', 'discount')
- `value_col` (double): Monetary value of the transaction
- `currency_id` (int): Reference to the currency used
- `start_date` (date): Start date of the financial record
- `end_date` (date): Optional end date for the financial record
- `account_id` (int): Reference to the main account for the transaction
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting
- `date_col` (timestamp): Timestamp of record creation, defaults to current timestamp

#### Common Use Cases:
1. Budget Management: Tracking department-specific budgets and expenses
2. Financial Planning: Managing department financial allocations and forecasts
3. Cost Analysis: Monitoring and analyzing departmental costs over time


**hr_departments_leaves**: Manages department-wide leave periods and holiday schedules.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the leave record
- `department_id` (int): Reference to the associated department
- `statement_col` (varchar(250)): Optional description of the leave period
- `duration_in_hours` (double): Duration of the leave in hours
- `duration_in_days` (double): Duration of the leave in days
- `start_date` (date): Start date of the leave period
- `date_col` (timestamp): Timestamp of record creation, defaults to current timestamp

#### Common Use Cases:
1. Leave Management: Recording department-wide holidays and closures
2. Schedule Planning: Managing department-specific time-off periods
3. Salary Effects: Defining effects of each leave type on generated salaries


**hr_employment_requests**: Manages job application and candidate information for potential employees.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the employment request
- `name` (varchar(255)): Full name of the job applicant
- `national_id` (varchar(255)): National identification number, optional
- `phone` (varchar(255)): Contact phone number, optional
- `address` (varchar(255)): Residential address, optional
- `email` (varchar(255)): Email address, optional
- `birthdate` (date): Date of birth, optional
- `date_col` (timestamp): Timestamp of request creation, defaults to current timestamp

#### Common Use Cases:
1. Recruitment Management: Processing and tracking job applications
2. Candidate Database: Maintaining records of potential employees


**hr_employees**: Stores comprehensive employee information and tracks their employment lifecycle.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the employee
- `employment_request_id` (int): Unique reference to the original employment request
- `name` (varchar(255)): Full name of the employee, optional
- `national_id` (varchar(255)): National identification number, optional
- `phone` (varchar(255)): Contact phone number, optional
- `address` (varchar(255)): Residential address, optional
- `email` (varchar(255)): Email address, optional
- `birthdate` (date): Date of birth, optional
- `start_date` (date): Employment start date
- `resignation_date` (date): Employment end date, optional
- `bank` (varchar(250)): Banking institution name, optional
- `bank_account_number` (varchar(250)): Bank account number, optional
- `bank_notes` (varchar(250)): Additional banking information, optional
- `photo` (mediumblob): Employee photograph, optional

#### Common Use Cases:
1. Employee Records: Maintaining comprehensive employee information


**hr_employment_request_certificates**: Records educational qualifications and certifications of job applicants.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the certificate record
- `employment_request_id` (int): Reference to the associated employment request
- `university_name` (varchar(255)): Name of the educational institution
- `university_specialty` (varchar(255)): Field of study or specialization
- `university_year` (varchar(4)): Year of graduation
- `university_certificate` (varchar(255)): Certificate type or name, optional
- `university_gpa` (float): Grade Point Average, optional

#### Common Use Cases:
1. Skills Assessment: Evaluating candidate qualifications and matching them to positions based on qualifications
2. Compliance: Maintaining records of required certifications and degrees


**hr_employees_certificates**: Tracks educational qualifications and certifications of current employees.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the certificate record
- `employee_id` (int): Reference to the associated employee
- `university_name` (varchar(255)): Name of the educational institution
- `university_specialty` (varchar(255)): Field of study or specialization
- `university_year` (varchar(4)): Year of graduation
- `university_certificate` (varchar(255)): Certificate type or name, optional
- `university_gpa` (float): Grade Point Average, optional

#### Common Use Cases:
1. Tracking employee educational achievements and maintaining current employee qualification records


**hr_employees_salaries_additions_discounts**: Manages employee salary adjustments, bonuses, and deductions.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the salary adjustment
- `employee_id` (int): Reference to the associated employee
- `type_col` (varchar(50)): Type of adjustment (addition or discount)
- `start_date` (date): Start date of the adjustment
- `repeatition` (int): Number of times the adjustment repeats
- `end_date` (int): End date or period for the adjustment
- `value_col` (double): Monetary value of the adjustment
- `account_id` (int): Reference to the main account for the transaction
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting
- `statement_col` (varchar(500)): Description of the adjustment, optional
- `currency_id` (int): Reference to the currency used, optional
- `state_col` (varchar(11)): Status of the adjustment, defaults to 'active'

#### Common Use Cases:
1. Payroll Management: Processing regular salary adjustments and bonuses
4. Financial Reporting: Tracking salary-related expenses and adjustments


**hr_employees_salaries_additions_discounts_payments**: Records the payment history of salary adjustments.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the payment record
- `salaries_additions_discounts` (int): Reference to the associated salary adjustment
- `date_col` (date): Date when the payment was processed

#### Common Use Cases:
1. Payment Tracking: Recording when salary adjustments are paid


**hr_employees_transfers**: Tracks employee movements between departments and positions within the organization.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the transfer record
- `employee_id` (int): Reference to the transferred employee
- `department_id` (int): Reference to the new department
- `position_id` (int): Reference to the new position
- `date_col` (timestamp): Timestamp when the transfer was recorded, defaults to current timestamp

#### Common Use Cases:
1. Tracking employee promotions and role changes and managing departmental staffing and structure


**hr_employee_received_items**: Manages inventory items assigned to or received by employees.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the received item record
- `employee_id` (int): Reference to the employee receiving the item
- `warehouse_id` (int): Reference to the source warehouse, optional
- `material_id` (int): Reference to the material/item being received, optional
- `quantity` (double): Amount of material received, optional
- `unit_id` (int): Reference to the unit of measurement, optional
- `received_date` (date): Date when the item was received, optional
- `received` (tinyint(1)): Flag indicating if the item has been received, defaults to 0

#### Common Use Cases:
1. Asset Management: Tracking company equipment assigned to employees


**hr_extra**: Manages additional work hours and related compensation for employees.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the extra work record
- `employee_id` (int): Reference to the employee performing extra work
- `department_id` (int): Reference to the department where work was performed
- `start_date` (date): Start date of the extra work period
- `value_col` (double): Monetary value of the extra work
- `duration_in_hours` (double): Duration of extra work in hours
- `duration_in_days` (double): Duration of extra work in days
- `currency_id` (int): Reference to the currency used for payment
- `statement_col` (varchar(500)): Description of the extra work, optional
- `account_id` (int): Reference to the main account for the transaction
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting
- `state_col` (varchar(11)): Status of the extra work record, defaults to 'active'

#### Common Use Cases:
1. Tracking additional work hours and compensation and monitoring extra work costs by department
2. Payroll Processing: Calculating additional payments for extra work


**hr_finance**: Manages recurring financial transactions and periodic payments for employees.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the finance record
- `employee_id` (int): Reference to the associated employee
- `type_col` (varchar(50)): Type of financial transaction, takes values ('salary', 'insurance')
- `value_col` (double): Monetary value of the transaction
- `currency_id` (int): Reference to the currency used
- `start_date` (date): Start date of the financial record
- `end_date` (date): End date of the financial record, optional
- `account_id` (int): Reference to the main account for the transaction
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting
- `cycle` (varchar(50)): Payment cycle frequency, defaults to 'month', and can take the following values:
    - 'month'
    - 'week'
    - 'day'
    - 'hour'
- `date_col` (timestamp): Timestamp of record creation, defaults to current timestamp

#### Common Use Cases:
1. Recording employee base salary and insurance information with start/end dates and payment cycles
2. Maintaining proper accounting records by linking salary/insurance payments to appropriate accounts
3. Payroll Processing: Calculating employee salaries based on base pay, insurance, payment cycles, and effective dates


**hr_insurance_blocks**: Manages time periods for employee insurance coverage and processing.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the insurance block
- `from_date` (date): Start date of the insurance coverage period
- `to_date` (date): End date of the insurance coverage period
- `date_col` (timestamp): Timestamp of block creation, defaults to current timestamp

#### Common Use Cases:
1. Insurance Period Management: Defining insurance coverage timeframes


**hr_insurance_block_entries**: Records individual employee insurance entries within insurance blocks.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the entry
- `insurance_block_id` (int): Reference to the associated insurance block
- `employee_id` (int): Reference to the insured employee
- `cycles` (double): Number of insurance payment cycles
- `value_col` (double): Monetary value of the insurance
- `currency` (int): Reference to the currency used, optional

#### Common Use Cases:
1. Insurance Records: Tracking individual employee insurance details
2. Payroll Processing: Calculating insurance payments based on cycles and value


**hr_leave_types**: Defines different categories of employee leave with their specific rules.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the leave type
- `name` (varchar(255)): Name of the leave type
- `days` (int): Standard number of days allowed, optional
- `days_in_year` (int): Annual leave day allocation, optional
- `period` (varchar(50)): Time period for leave renewal, optional
- `date_added` (datetime): Creation timestamp, defaults to current timestamp
- `paid` (boolean): Indicates if the leave type is paid, defaults to false

#### Common Use Cases:
1. Leave Policy Management: Defining different types of leave (vacation, sick, etc.), entitlements, and payment rules


**hr_leaves**: Records individual employee leave requests and their details.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the leave record
- `employee_id` (int): Reference to the employee taking leave
- `leave_type_id` (int): Reference to the type of leave being taken
- `alternative_id` (int): Reference to the employee covering during leave
- `duration_in_hours` (double): Duration of leave in hours
- `duration_in_days` (double): Duration of leave in days
- `start_date` (date): Start date of the leave period
- `date_col` (timestamp): Timestamp of record creation, defaults to current timestamp
- `state_col` (varchar(11)): Status of the leave request, defaults to 'active'

#### Common Use Cases:
1. Leave Request Management: Processing and tracking employee time-off requests
2. Coverage Planning: Managing work coverage during employee absences
3. Payroll Processing: Calculating leave-related deductions from employee salaries


**hr_loans**: Manages employee loans and their repayment configurations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the loan record
- `employee_id` (int): Reference to the employee receiving the loan
- `value_col` (double): Total loan amount
- `currency` (int): Reference to the currency of the loan
- `date_col` (date): Date when the loan was issued
- `account_id` (int): Reference to the main account for the loan transaction
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting
- `periodically_subtract_from_salary` (tinyint(1)): Flag indicating if loan is repaid through salary deductions, defaults to 0
- `subtract_currency` (int): Reference to the currency for repayment, optional
- `subtract_cycle` (varchar(50)): Frequency of repayment deductions, optional and takes the following values:
    - 'month'
    - 'week'
    - 'day'
    - 'hour'
- `subtract_value` (double): Amount to deduct per cycle, optional

#### Common Use Cases:
1. Loan Management: Recording and tracking employee loans
2. Repayment Planning: Configuring automatic salary deductions for loan repayment


**hr_loans_payment**: Records individual loan repayment transactions.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the payment record
- `loan_id` (int): Reference to the associated loan
- `value_col` (int): Amount of the payment
- `currency` (int): Reference to the currency of the payment
- `source` (varchar(15)): Source or method of payment
- `date_col` (date): Date when the payment was made

#### Common Use Cases:
1. Payment Tracking: Recording loan repayment transactions and maintaining complete loan payment records


**hr_positions**: Defines job positions within the organization and their base compensation details.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the position
- `position_name` (varchar(255)): Title or name of the position, optional
- `salary` (double): Base salary for the position, optional
- `currency_id` (int): Reference to the currency for the salary, optional
- `notes` (varchar(255)): Additional information about the position, optional

#### Common Use Cases:
1. Position Management: Defining and maintaining job positions
2. Salary Structure: Setting standard base salary for the employee working in the position


**hr_positions_finance**: Manages financial aspects and transactions specific to job positions.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the financial record
- `position_id` (int): Reference to the associated position
- `statement_col` (varchar(250)): Description of the financial transaction
- `type_col` (varchar(50)): Type classification of the financial transaction, takes values ('addition', 'discount')
- `value_col` (double): Monetary value of the transaction
- `currency_id` (int): Reference to the currency used
- `start_date` (date): Start date of the financial record
- `end_date` (date): Optional end date for the financial record
- `account_id` (int): Reference to the main account for the transaction
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting
- `date_col` (timestamp): Timestamp of record creation, defaults to current timestamp

#### Common Use Cases:
1. Position Budgeting: Managing financial allocations for positions
2. Payroll Salary Adjustments: Calculating employee salary considering the financial transactions related to the position


**hr_positions_leaves**: Manages leave entitlements and schedules specific to job positions.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the leave record
- `position_id` (int): Reference to the associated position
- `statement_col` (varchar(250)): Optional description of the leave arrangement
- `duration_in_hours` (double): Duration of leave in hours
- `duration_in_days` (double): Duration of leave in days
- `start_date` (date): Start date of the leave period
- `date_col` (timestamp): Timestamp of record creation, defaults to current timestamp

#### Common Use Cases:
1. Leave Entitlement: Defining position-specific leave benefits
2. Payroll Processing: Calculating leave-related deductions from employee salaries


**hr_salary_blocks**: Manages payroll periods and their associated accounting configurations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the salary block
- `from_date` (date): Start date of the payroll period
- `to_date` (date): End date of the payroll period
- `date_col` (timestamp): Timestamp of block creation, defaults to current timestamp
- `account_id` (int): Reference to the account for salary payments, optional

#### Common Use Cases:
1. Payroll Period Management: Defining pay periods for salary processing
2. Accounting Integration: Linking salary payments to specific accounts


**hr_salary_block_entries**: Records individual salary entries within payroll periods.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the salary entry
- `salary_block_id` (int): Reference to the associated salary block
- `employee_id` (int): Reference to the employee receiving payment
- `statement_col` (varchar(500)): Description or purpose of the salary payment
- `value_col` (double): Monetary value of the salary payment
- `currency` (int): Reference to the currency used

#### Common Use Cases:
1. Salary Processing: Recording individual employee salary payments
2. Payment Tracking: Managing salary disbursements by pay period


**hr_settings**: Manages system-wide HR configuration settings and default values.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the setting
- `name` (varchar(50)): Unique identifier for the setting
- `value_col` (varchar(11)): Setting value, optional
- `last_update` (timestamp): Last modification timestamp, automatically updated

#### Common Use Cases:
1. Work Schedule Configuration: Setting up working days, hours and week configuration
2. Financial Account Mapping: Managing salary, department and special transaction accounts
3. HR Policy Settings: Configuring leave management, work rates and period definitions
4. System Defaults: Account assignments for various HR transactions, default opposite accounts for double-entry accounting, resource and cost center configurations
5. Multi-currency Support: Handling salary payments in different currencies


**expenses_types**: Defines categories of expenses and their accounting configurations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the expense type
- `name` (varchar(25)): Name of the expense category
- `account_id` (int): Reference to the main account for this expense type, optional
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting, optional
- `calculated_in_manufacture` (int): Flag indicating if this expense type is included in manufacturing costs, defaults to 0

#### Common Use Cases:
1. Expense Classification: Categorizing different types of business expenses
2. Manufacturing Cost Analysis: Identifying expenses that affect production costs


**expenses**: Records periodic expense transactions with their types and values.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the expense record
- `time_slot` (varchar(25)): Time period type for the expense, defaults to 'month'
- `value_col` (double): Monetary value of the expense
- `year_col` (varchar(50)): Year of the expense
- `month_col` (varchar(50)): Month of the expense, defaults to '1'
- `expense_type` (int): Reference to the type of expense
- `currency` (int): Reference to the currency used

#### Common Use Cases:
1. Expense Tracking: Recording and monitoring periodic expenses

Note: The table enforces uniqueness on the combination of year, month, and expense type.


**invoices**: Manages comprehensive invoice records with their associated accounts and financial configurations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the invoice
- `type_col` (int): Reference to invoice type (buy, sell, etc.)
- `number` (int): Unique invoice number
- `client` (int): Reference to the associated client, optional
- `client_account` (int): Reference to the client's account, optional
- `payment` (varchar(50)): Payment method or terms, takes values ('cash', 'postponed')
- `paid` (tinyint(1)): Payment status flag, takes values (0, 1)
- `currency` (int): Reference to the transaction currency, optional
- `cost_center` (int): Reference to the associated cost center, optional
- `warehouse` (int): Reference to the related warehouse, optional
- `cost_account` (int): Reference to the cost tracking account, optional
- `gifts_account` (int): Reference to the gifts handling account, optional
- `added_value_account` (int): Reference to the value-added account, optional
- `monetary_account` (int): Reference to the cash/bank account 
- `materials_account` (int): Reference to the materials account
- `stock_account` (int): Reference to the inventory account
- `gifts_opposite_account` (int): Reference to the contra account for gifts, optional
- `statement_col` (varchar(500)): Additional notes or description, optional
- `date_col` (date): Date of the invoice

#### Common Use Cases:
1. Transaction Recording: Managing sales, purchases, and other business transactions
2. Inventory Management: Tracking stock movements through invoices, where manufactured processes and materials movements between warehouses are generating input/outout invoices
3. Cost Allocation: Assigning costs to appropriate centers and accounts


**invoices_discounts_additions**: Manages discounts and additional charges applied to invoices.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the adjustment
- `invoice_id` (int): Reference to the associated invoice
- `type_col` (varchar(50)): Type of adjustment takes values ('discount' or 'addition')
- `account` (int): Reference to the main account for the adjustment
- `cost_center` (int): Reference to the associated cost center, optional
- `currency` (int): Reference to the currency used, optional
- `exchange` (int): Reference to the exchange rate price
- `opposite_account` (int): Reference to the contra account for double-entry accounting, optional
- `equilivance` (double): Value or amount of the adjustment in the currency of the invoice
- `percent` (tinyint): Flag indicating if the adjustment is percentage-based, defaults to 0

#### Common Use Cases:
1. Discount Management: Recording and tracking invoice discounts
2. Additional Charges: Managing extra fees and surcharges
3. Cost Distribution: Allocating adjustments to appropriate cost centers


**invoice_items**: Stores individual items within each invoice, tracking produced materials details, quantities, pricing, discounts and other financial calculations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the item entry
- `invoice_id` (int): Reference to the parent invoice
- `material_id` (int): Reference to the product or material
- `quantity1` (double): Primary quantity amount, optional
- `unit1_id` (int): Reference to primary unit of measurement, optional
- `quantity2` (double): Secondary quantity amount, optional
- `unit2_id` (int): Reference to secondary unit of measurement, optional
- `quantity3` (float): Tertiary quantity amount, optional
- `unit3_id` (int): Reference to tertiary unit of measurement, optional
- `price_type_id` (int): Reference to the price category or type (wholesale, retail, etc.)
- `unit_price` (double): Price per unit
- `currency_id` (int): Reference to the transaction currency
- `equilivance_price` (double): Converted price value in the currency of the invoice
- `exchange_id` (int): Reference to the exchange rate record
- `discount` (double): Fixed discount amount, optional
- `discount_percent` (double): Percentage-based discount, optional
- `addition` (double): Fixed additional charge amount, optional
- `addition_percent` (double): Percentage-based additional charge, optional
- `added_value` (double): Value-added amount, optional
- `gifts` (double): Gift quantity, optional
- `gifts_value` (double): Monetary value of gifts, optional
- `gifts_discount` (double): Discount applied to gifts, optional
- `warehouse_id` (int): Reference to the source/destination warehouse, optional
- `cost_center_id` (int): Reference to the associated cost center, optional
- `notes` (varchar(500)): Additional item-specific notes, optional
- `deal_id` (int): Unique reference to associated deal or promotion, optional
- `item_discount_account` (int): Reference to item-specific discount account, optional
- `item_addition_account` (int): Reference to item-specific addition account, optional
- `receipt_doc_id` (int): Reference to associated receipt document, optional
- `production_date` (date): Manufacturing date of the item, optional
- `expire_date` (date): Expiration date of the item, optional

#### Common Use Cases:
1. Invoice Item Recording: Capturing detailed information about materials, manufactured materials, quantities, and pricing within invoice documents
2. Inventory Control: Tracking warehouse movements and stock dates
3. Price History and Analysis: Gets the most recent/last/average transactions price for a material, including any discounts or additions applied, with filtering options for currency, unit, time period and invoice type (buy, sell, etc.)
4. Sales Analysis and Reporting: Retrieves sales invoice data for analysis, compares actual sales against targets and analyzes monthly sales data per client/region.


**journal_entries**: Manages the header information for accounting journal entries, providing a centralized record of financial transactions.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the journal entry
- `currency` (int): Reference to the currency used for the entry
- `date_col` (date): Date when the transaction occurred
- `entry_date` (date): Date when the entry was recorded in the system
- `origin_type` (varchar(250)): Source or type of the transaction, takes values:
      - 'transfer': a transfer transaction
      - 'invoice_payment': an invoice payment transaction  
      - 'invoice': an invoice transaction
      - 'extra_payment': client extra payment transaction
      - 'course': a course transaction
      - 'department_addition': a department addition transaction
      - 'department_discount': a department discount transaction
      - 'position_addition': a position addition transaction
      - 'position_discount': a position discount transaction
      - 'extra_work': an extra work transaction
      - 'journal': a manual entered journal entry
      - 'manufacture': a manufactured material entry
      - 'pullout_material': a material pullout transaction
      - 'period_start': a period start entry
      - 'period_start_material': a period start material entry
      - 'base_salary': employee's base salary transaction
      - 'salary_permenant_addition': a salary permenant addition transaction
      - 'salary_temporary_addition': a salary temporary addition transaction
      - 'salary_permenant_discount': a salary permenant discount transaction
      - 'salary_temporary_discount': a salary temporary discount transaction
      - 'loan_payment': a loan payment transaction
      - 'employee_loan_payment': a employee loan payment transaction
- `origin_id` (int): Reference to the source transaction's ID, like if the origin_type is 'invoice', the origin_id is the invoice id.

#### Common Use Cases:
1. Financial Record Keeping: Recording all financial transactions in chronological order
2. Financial Reporting: Supporting the generation of financial statements and reports


**journal_entries_items**: Records the detailed line items within journal entries, capturing the double-entry accounting transactions.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the entry item
- `journal_entry_id` (int): Reference to the parent journal entry
- `account_id` (int): Reference to the main account involved in the transaction
- `statement_col` (varchar(2500)): Description or explanation of the transaction
- `currency` (int): Reference to the currency used for the transaction
- `opposite_account_id` (int): Reference to the contra account for double-entry accounting, optional
- `type_col` (varchar(50)): Type of entry takes values ('debit', 'credit'), this type is related the account, for example, if the type is 'debit' then the `account` type is debit and `opposite account` type is credit.
- `value_col` (double): Monetary value of the transaction
- `cost_center_id` (int): Reference to the associated cost center, optional

#### Common Use Cases:
1. Double-Entry Accounting: Recording both debit and credit sides of each transaction
2. Cost Center Tracking: Allocating transactions to specific cost centers for detailed financial analysis
3. Financial Analysis: Supporting detailed transaction analysis and reconciliation
4. Reporting: Generating trial balances, income statements, and balance sheets
5. Invoice Payments Tracking: Allocating payments to postponed invoices, with any extra payments from/to clients.


**groups**: Manages hierarchical organizational groupings, enabling a flexible structure for categorizing and organizing various business entities.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the group
- `name` (varchar(50)): Name of the group
- `code` (varchar(50)): Automatically generated hierarchical code that reflects the group's position in the tree structure
- `parent_group` (int): Reference to parent group ID, enables hierarchical structure
- `date_col` (timestamp): Timestamp of group creation, defaults to current timestamp

#### Common Use Cases:
1. Organizational Structure: Creating hierarchical groupings for departments, divisions, or business units
2. Category Management: Organizing items, accounts, or entities in a tree-like structure
3. Access Control: Defining permission boundaries and organizational scopes
4. Reporting: Generating hierarchical reports and analyzing data at different organizational levels
5. Resource Management: Grouping and managing resources in a structured manner


**materials**: Manages comprehensive inventory item information, including specifications, units, pricing, and stock management details.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the material
- `code` (varchar(50)): Unique identifier code for the material
- `name` (varchar(50)): Name of the material
- `group_col` (int): Reference to group ID for categorization
- `specs` (varchar(500)): Detailed specifications of the material
- `size_col` (varchar(50)): Size specifications
- `manufacturer` (varchar(50)): Manufacturer name
- `color` (varchar(50)): Color specification
- `origin` (varchar(50)): Country or place of origin
- `quality` (varchar(50)): Quality grade or specification
- `type_col` (varchar(50)): Material type classification
- `model` (varchar(50)): Model number or identifier
- `unit1`, `unit2`, `unit3` (int): References to up to three different units of measurement
- `default_unit` (int): Reference to the default unit of measurement
- `current_quantity` (double): Current stock level
- `max_quantity` (double): Maximum stock level threshold
- `min_quantity` (double): Minimum stock level threshold
- `request_limit` (double): Reorder point quantity
- `gift` (double): Gift quantity
- `gift_for` (double): Quantity threshold for gift eligibility
- `price1_desc` to `price6_desc` (int): References to price descriptions
- `price1_1` to `price6_3` (double): Different price points for various scenarios
- `price1_1_unit` to `price6_3_unit` (varchar(50)): Units associated with each price point
- `expiray` (int): Expiration period
- `groupped` (tinyint(1)): Flag indicating if the material is a composite item, takes values (0 or 1)
- `yearly_required` (double): Annual demand quantity
- `work_hours` (double): Standard work hours for production
- `standard_unit1_quantity` to `standard_unit3_quantity` (double): Standard quantities in different units
- `manufacture_hall` (int): Reference to manufacturing location
- `discount_account` (int): Reference to discount accounting entry
- `addition_account` (int): Reference to additional charges accounting entry

#### Common Use Cases:
1. Inventory Management: Store materials and their associated information, and sending alerts in case the stock is low.
2. Pricing Management: Store multiple price tiers for the same material, and managing unit-specific pricing.
3. Manufacturing Support: Store the manufacturing information for the materials, and the standard quantities in different units.


**currencies**: Manages currency definitions and their subdivisions, supporting multi-currency transactions throughout the system.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the currency
- `name` (varchar(50)): Unique name of the currency
- `symbol` (varchar(50)): Currency symbol representation
- `parts` (varchar(50)): Name of currency subdivision (e.g., "cents" for dollars)
- `parts_relation` (double): Conversion ratio between main unit and subdivision (e.g., 100 for dollars to cents)

#### Common Use Cases:
1. Financial Operations: Supporting multi-currency transactions, currency conversion calculations, and formatting monetary values for display.
2. Currency Management: Store the currency information and the subdivisions, and the conversion ratio between the main unit and the subdivision.


**material_moves**: Tracks movement of materials between warehouses.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the movement
- `source_warehouse` (int): Reference to source warehouse
- `source_warehouse_entry_id` (int): Reference to source warehouse entry
- `destination_warehouse` (int): Reference to destination warehouse
- `destination_warehouse_entry_id` (int): Reference to destination warehouse entry
- `quantity` (double): Quantity of the material moved
- `unit` (int): Reference to unit of measurement
- `origin` (varchar(50)): Origin of the movement ,used to define the cause of the material move , takes values (manufacture, invoice, transfer)
- `origin_id` (varchar(50)): Id of the origin of the movement (store the manufacture id or invoice depending on the origin field)
- `date_col` (timestamp): Date of the movement

#### Common Use Cases:
1. Material Movement Tracking: Records and tracks material movements between warehouses, thses movements are generated due to invoices, manufacture processes and transfers between warehouses.
2. Inventory Control: Maintains accurate stock levels by updating warehouse inventory after material moves
3. Reporting: Provides data for inventory turnover analysis and material flow reports


**period_start_materials**: Manages initial inventory stock for materials at the start of accounting periods, supporting multi-unit quantities and pricing information.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the period start record
- `material_id` (int): Reference to the material being recorded
- `quantity1` (double): Primary quantity of the material
- `unit1_id` (int): Reference to the primary unit of measurement
- `quantity2` (double): Secondary quantity of the material, optional
- `unit2_id` (int): Reference to the secondary unit of measurement, optional
- `quantity3` (double): Tertiary quantity of the material, optional
- `unit3_id` (int): Reference to the tertiary unit of measurement, optional
- `unit_price` (int): Price per unit of the material
- `currency` (int): Reference to the currency used for pricing
- `warehouse_id` (int): Reference to the warehouse location
- `notes` (varchar(500)): Additional information or remarks
- `date_col` (date): Date of the period start record

#### Common Use Cases:
1. Initial Inventory Recording: Records starting inventory levels and valuations for materials when beginning new accounting periods, with support for multiple units of measurement and cost details.


**exchange_prices**: Manages currency exchange rates between different currencies over time, supporting bi-directional currency conversion.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the exchange rate record
- `currency1` (int): Reference to the first currency in the exchange pair
- `currency2` (int): Reference to the second currency in the exchange pair
- `exchange` (double): Exchange rate value between the currencies, defaults to 1
- `date_col` (date): Date when the exchange rate is effective
- `currency1_ordered` (int): Computed column containing the smaller of currency1 and currency2 IDs
- `currency2_ordered` (int): Computed column containing the larger of currency1 and currency2 IDs

#### Common Use Cases:
1. Currency Conversion: Can be used to store/fetch the exchange rates between different currencies over time, and fetching the exchange date according to a certain date.


**warehouseslist**: Manages warehouse information and hierarchy, supporting complex storage location management with associated accounting and capacity tracking.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the warehouse
- `code` (varchar(50)): Warehouse identification code
- `name` (varchar(50)): Unique name of the warehouse
- `codename` (varchar(50)): Unique system identifier used for warehouse-specific database table names
- `date_col` (datetime): Timestamp of warehouse creation, defaults to current timestamp
- `parent_warehouse` (int): Reference to parent warehouse, enabling hierarchical structure
- `account` (int): Reference to associated accounting entry
- `address` (varchar(100)): Physical location of the warehouse
- `manager` (varchar(50)): Name of warehouse manager
- `notes` (varchar(200)): Additional information or remarks
- `capacity` (double): Storage capacity of the warehouse
- `capacity_unit` (int): Reference to unit used for capacity measurement

#### Common Use Cases:
1. Warehouse Structure Management: Can be used to store warehouses and their associated information, with the ability to create a hierarchy of warehouses.
2. Warehouse Capacity Management: Can be used to store the capacity of the warehouse and the unit used to measure it, with respect to the fact that different materials might have different units of measurement, with sending alerts in case the warehouse is close to be full.


**warehouse.{codename}**: Manages material inventory and batch tracking for each warehouse.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the inventory record
- `material_id` (int): Reference to the associated material, foreign key to materials table
- `quantity` (double): Current quantity of the material, defaults to 0
- `unit` (varchar(50)): Unit of measurement for the quantity
- `production_batch_id` (int): Reference to production batch if material was produced internally
- `receipt_doc_id` (int): Reference to receipt document if material was received externally
- `batch_number` (int): Batch identification number
- `batch_mfg` (date): Manufacturing date of the batch
- `batch_exp` (date): Expiration date of the batch
- `material_move_id` (int): Reference to material movement record, foreign key to material_moves table
- `production_date` (date): Date when the material was produced
- `expire_date` (date): Expiration date of the material

#### Common Use Cases:
1. Inventory Management: Tracks material quantities and batch information within each warehouse
2. Manufacture Tracking: Stores produced materials info in case the material is manufactured internally
3. Material Movement: Links to material movement records for tracking inventory changes
4. Output items: Prioritize which stock to reduce first, defaults to FIFO, but can be changed to LIFO, expire date or production date (which depend on the columns `batch_mfg` and `batch_exp`)
5. Alerts: Issues alerts in case the warehouse is close to be full, through calculating the total amount of materials entries in it and comparing it to the warehouse capacity.


**media**: Manages binary file storage within the database, providing centralized storage for various media assets used throughout the system.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the media record
- `name` (varchar(255)): Unique identifier name for the stored media file
- `file` (mediumblob): Binary storage of the actual file content

#### Common Use Cases:
1. Asset Management: Users can upload images and documents to be used in the system.
2. Can be used to store templates for reports and invoices, or headers/footers for exported reports.


**machines**: Manages equipment and machinery assets, tracking their financial details, depreciation, and associated accounting entries.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the machine
- `name` (varchar(250)): Name or identifier of the machine
- `years_age` (double): Expected lifespan or age of the machine in years
- `estimated_waste_value` (double): Estimated salvage or residual value
- `estimated_waste_currency` (int): Reference to currency for waste value
- `estimated_waste_account` (int): Reference to account for depreciation/waste tracking
- `invoice_item_id` (int): Reference to purchase invoice item
- `notes` (varchar(500)): Additional information or remarks
- `account` (int): Reference to main accounting entry
- `opposite_account` (int): Reference to contra account for double-entry accounting

#### Common Use Cases:
1. Asset Management: Comprehensive tracking and documentation of machine inventory and equipment details, with consumption/usage tracking.
2. Financial Tracking: Recording and managing purchase costs, depreciation calculations and salvage values of each machine
3. Reporting: Generating asset valuation and financial impact reports


**machine_maintenance**: Manages maintenance records and operations for machines, including costs, scheduling, and accounting details.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the maintenance record
- `machine_id` (int): Reference to the machine being maintained
- `name` (varchar(250)): Name or description of the maintenance operation
- `start_date` (datetime): Start date/time of maintenance operation
- `end_date` (datetime): End date/time of maintenance operation
- `maintenance_type` (varchar(50)): Type or category of maintenance (only 2 values regular/urgent)
- `cost` (double): Cost of maintenance operation
- `statment_col` (varchar(500)): Detailed description or notes that will appear in the journal entry created for this maintenance operation
- `account` (int): Reference to main accounting entry
- `opposite_account` (int): Reference to contra account for double-entry accounting

#### Common Use Cases:
1. Maintenance Tracking: Recording and scheduling machine maintenance operations
2. Cost Management: Tracking maintenance expenses and accounting entries
3. Maintenance History: Maintaining detailed maintenance records per machine


**machine_modes**: Manages different operational modes or states for machines, supporting various operational configurations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the mode
- `machine_id` (int): Reference to the associated machine
- `name` (varchar(250)): Name of the operational mode
- `date_col` (timestamp): Creation timestamp of the mode record

#### Common Use Cases:
1. Operation Configuration: Defining different operational states for machines
2. Manufacture Planning: Supporting multiple machine configurations for manufacturing operations.
3. Resource Management: Managing machine-specific operational costs based on the mode and the machine's usage duration


**production_lines**: Manages manufacturing production lines.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the production line
- `name` (varchar(250)): Name of the production line
- `notes` (varchar(500)): Additional information or remarks

#### Common Use Cases:
1. Production Line Setup: Organizing production processes and associating it with a name to be linked with the machines that will be used in this production line.


**machine_production_lines**: Links machines to production lines, managing machine assignments and configurations within production processes.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the assignment
- `machine_id` (int): Reference to the machine
- `production_line_id` (int): Reference to the production line
- `machine_notes` (varchar(500)): Additional notes about the machine's role

#### Common Use Cases:
1. Production Setup: Organizing machines into production lines
2. Process Management: Tracking machine assignments and configurations
3. Resource Planning: Managing machine allocation across production lines


**maintenance_materials**: Manages inventory of materials used in maintenance operations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the material
- `name` (varchar(250)): Name of the maintenance material

#### Common Use Cases:
1. Inventory Management: Tracking maintenance supplies and materials that will go in the maintenance operations.


**maintenance_operation_materials**: Tracks specific materials used in maintenance operations, including quantities and units.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the material usage record
- `name` (varchar(250)): Name of the material usage entry
- `maintenance_operation` (int): Reference to the maintenance operation
- `quantity` (double): Amount of material used
- `unit` (int): Reference to unit of measurement
- `maintenance_material_id` (int): Reference to the maintenance material

#### Common Use Cases:
1. Material Usage Tracking: Recording materials consumed during maintenance
2. Inventory Control: Managing maintenance material stock levels


**maintenance_workers**: Manages assignments of employees to maintenance operations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the assignment
- `employee_id` (int): Reference to the assigned employee
- `maintenance_id` (int): Reference to the maintenance operation

#### Common Use Cases:
1. Resource Assignment: Managing maintenance staff assignments
2. Work Tracking: Recording employee involvement in maintenance tasks


**manufacture**: Manages manufacturing operations, including costs, materials, and accounting configurations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the manufacturing operation
- `pullout_date` (date): Date when materials are withdrawn from their warehouses
- `date_col` (date): Operation date
- `expenses_type` (varchar(50)): Type of expenses classification (only one of 3 values month/year/real)
- `material_pricing_method` (varchar(50)): Method used for material cost calculation (only one of these static values material_last_purchase/material_invoices_average_till_pollout/material_invoices_average/material_explicit_value/material_exact_invoice)
- `currency` (int): Reference to currency used
- `expenses_cost` (decimal): Total expenses cost
- `machines_operation_cost` (decimal): Cost of using the machines in the manufacturing operation
- `salaries_cost` (decimal): Salaries cost of the employees working in the manufacturing operation
- `warehouse` (int): Reference to warehouse
- `mid_account` (int): Reference to the account that will be used as a middle output account for the manufacturing operation
- `mid_account_input` (int): Reference to the account that will be used as a middle input account for the manufacturing operation
- `account` (int): Reference to main manufacturing account
- `composition_materials_cost` (decimal): Cost of component materials that make the final product
- `quantity_unit_expenses` (int): Reference to unit for quantity expenses
- `expenses_distribution` (varchar(50)): Method of expenses distribution (only 2 values hours_expenses/no_expenses/quantity_expenses)
- `state_col` (varchar(20)): Status of the manufacturing operation takes one of the following values:
    - 'active'
    - 'cancelled'
- `ingredients_pullout_method` (varchar(50)): Method for withdrawing ingredients (only 2 values FIFO/LIFO)
- `ingredients_pullout_account` (int): Account for ingredients withdrawal
- `working_hours` (decimal): Total working hours

#### Common Use Cases:
1. Production Management: Tracking manufacturing operations and costs
2. Cost Accounting: Managing production expenses and materials and recording them in the accounting system
3. Resource Planning: Coordinating manufacturing resources and materials for each manufacturing operation according to variables like pullout methods and labor/machine costs.


**manufacture_halls**: Manages manufacturing locations and their warehouse associations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the hall
- `warehouse_id` (int): Reference to associated warehouse
- `date_col` (timestamp): Creation timestamp

#### Common Use Cases:
1. Location Management: Organizing manufacturing spaces
2. Warehouse Integration: Linking production areas to warehouses


**manufacture_machines**: Tracks machine usage in manufacturing operations, including operational modes and durations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the machine usage record
- `manufacture_id` (int): Reference to manufacturing operation
- `machine_id` (int): Reference to machine
- `mode_id` (int): Reference to machine operation mode
- `duration` (double): Operation duration (in minutes)
- `exclusive` (tinyint): Flag indicating exclusive machine use
- `exclusive_percent` (int): Percentage of exclusive usage

#### Common Use Cases:
1. Production and Resource Planning: Managing machine allocation to each manufacturing operation and calculating the cost of using the machines according to the mode and the machine's usage duration.
2. Machine allocation: Managing machine allocation to each manufacturing operation whether its exclusive or not to the manufacturing operation.


**manufacture_materials**: Manages raw materials used in manufacturing processes, including quantities and costs.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the material usage
- `manufacture_id` (int): Reference to manufacturing operation
- `composition_item_id` (int): Reference to composition item
- `standard_quantity` (double): Standard required quantity
- `required_quantity` (double): Actual required quantity of the raw material
- `unit` (int): Reference to unit of measurement
- `unit_cost` (int): Cost per unit
- `row_type` (varchar(10)): Type classification of the row, the material could be consisting of other materials takes one of the following values:
    - 'parent'
    - 'child'
- `warehouse_id` (int): Reference to warehouse where the raw material is stored
- `warehouse_account_id` (int): Reference to warehouse account
- `pulled_quantity` (double): Quantity pulled from stock in warehouse
- `shortage` (double): Quantity shortage (if exists)
- `currency` (int): Reference to currency of the raw material cost
- `warehouse_quantity` (double): Current available quantity in warehouse

#### Common Use Cases:
1. Material Requirements: Managing manufacturing requirements of the raw materials the produced material is made of.
2. Inventory Control: Tracking material usage and stock levels to make sure the manufacturing operation can be done with no shortages.
3. Cost Tracking: Managing material costs in manufacturing operations.


**manufacture_produced_materials**: Records produced materials from manufacturing operations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the produced material
- `manufacture_id` (int): Reference to manufacturing operation that produced the material
- `material_id` (int): Reference to produced material
- `quantity1` (double): Primary quantity produced
- `unit1` (int): Primary unit of measurement
- `quantity2` (double): Secondary quantity produced
- `unit2` (int): Secondary unit of measurement
- `quantity3` (double): Tertiary quantity produced
- `unit3` (int): Tertiary unit of measurement
- `working_hours` (double): Hours worked to produce the product
- `batch` (int): Batch number
- `referential_quantity1` (double): Reference quantity 1 (standard quantity of the produced material in the batch)
- `referential_quantity2` (double): Reference quantity 2 (standard quantity of the produced material in the batch)
- `referential_quantity3` (double): Reference quantity 3 (standard quantity of the produced material in the batch)
- `referential_working_hours` (double): Reference working hours (standard working hours to produce the batch)
- `production_date` (date): Date of production (can be set to match the manufacture date of set manually by the user)

#### Common Use Cases:
1. Production Tracking: Recording manufacturing output (the quantity of the produced material in the batch)
2. Quality Control: Monitoring production quantities and updating it if needed.


**materials_machines**: Links materials to machines, defining production relationships and requirements.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the link
- `material_id` (int): Reference to material
- `machine_id` (int): Reference to machine used in the process of making this material
- `mode_id` (int): Reference to machine mode used to make this material
- `usage_duration` (double): Duration of machine usage to make this material
- `exclusive` (tinyint): Flag indicating exclusive machine use (if this machine is used exclusively for this material or not)

#### Common Use Cases:
1. Production Planning: Defining material-machine relationships, and knowing the machine and the mode used to make the material.
2. Resource Allocation: Managing machine time for materials
3. Cost Calculation: Can be used to calculate the cost of making the material according to the machine/mode and duration of usage for the material.


**resources**: Tracks resources used in manufacturing operations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the resource
- `name` (varchar(200)): Name of the resource
- `account_id` (int): Reference to account this resource belongs to
- `notes` (varchar(500)): Additional notes about the resource

#### Common Use Cases:
1. Resource Management: Tracking resources to be consumed by machines during their usage
2. Cost Tracking Reports: Tracking the cost of the resources used in the manufacturing operations, through tracking the account it belongs to


**resources_costs**: Tracks historical cost records for resources used in manufacturing operations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the cost record
- `resource_id` (int): Reference to the resource being costed
- `value_col` (double): Cost value of the resource
- `currency_id` (int): Reference to the currency used for the cost
- `unit_id` (int): Reference to the unit of measurement
- `notes` (varchar(500)): Additional notes or details about the cost record
- `date_col` (timestamp): Timestamp when the cost record was created, defaults to current timestamp

#### Common Use Cases:
1. Cost Tracking: Recording resource costs over time consumed by machines
2. Manufacturing Cost Analysis: Calculating production costs based on resource usage
3. Financial Planning: Supporting budgeting and cost projections for manufacturing operations through linking with the resource table and generating reports based on the resource account


**mode_resources**: Manages resource consumption for different machine operational modes.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the resource usage
- `mode_id` (int): Reference to machine mode
- `resource_id` (int): Reference to resource
- `consumption_per_minute` (double): Resource consumption rate per minute
- `unit` (int): Reference to unit of measurement

#### Common Use Cases:
1. Resource Planning/Consumption: Managing resource requirements and costs for each machine in different modes.
2. Efficiency Monitoring: Tracking resource consumption rates for each machine mode.


**aggregator**: Manages material aggregation needs for each produced material and how much is needed to be aggregated.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the aggregation record
- `material` (int): Reference to the material being selected
- `ammount` (int): Quantity or amount we want to manufacture of the material

#### Common Use Cases:
1. Production Planning: Aggregating material requirements for manufacturing operations with respect to the quantity stored in warehouses.


**compositions**: Tracks material composition relationships and quantities.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the composition
- `material` (int): Reference to the material
- `quantity` (double): Quantity in the composition

#### Common Use Cases:
1. Bill of Materials: Defining material compositions
2. Recipe Management: Tracking material formulations
3. Production Planning: Managing material requirements


**criteria**: Defines system-wide criteria for permissions and access control.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the criterion
- `name` (varchar(200)): English name of the criterion

#### Common Use Cases:
1. Access Control: Defining permission criteria
2. System Configuration: Managing features access.
3. User Administration: Managing users and their associated permissions.


**groupped_materials_composition**: Manages composite materials and their component relationships.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the composition
- `groupped_material_id` (int): Reference to the composite material
- `composition_material_id` (int): Reference to the component material
- `quantity` (double): Quantity of component material
- `unit` (int): Reference to unit of measurement

#### Common Use Cases:
1. Material Composition: Managing material compositions
2. Manufacturing Planning: Defining material requirements
3. Inventory Management: Tracking component relationships


#### Common Use Cases:
1. Inventory Tracking: Managing material transfers between warehouses and in/out of the system.
2. Warehouse Management: Can be used to track the movement of materials in a specific warehouse during a time period.


**loans**: Manages loan records between accounts.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the loan
- `currency` (int): Reference to the currency used for the loan
- `interest` (double): Interest rate for the loan
- `cycle` (varchar(50)): Payment cycle information, takes the following values:
    - 'year'
    - 'month'
    - 'week'
    - 'day'
- `name` (varchar(100)): Optional name/description of the loan
- `amount` (double): Amount of the loan
- `account_id` (int): Reference to the account receiving the loan
- `opposite_account_id` (int): Reference to the account providing the loan
- `date_col` (timestamp): Date and time when the loan was created

#### Common Use Cases:
1. Loan Management: Recording and tracking loans between accounts
2. Financial Tracking: Managing loan amounts, interest rates and payment cycles
3. Account Relationships: Tracking lending relationships between accounts


**loan_payments**: Manages loan payment records between accounts.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the payment
- `loan_id` (int): Reference to the loan, foreign key to loans table
- `amount` (double): Amount of the payment
- `currency` (int): Reference to the currency used for the payment
- `date_col` (date): Date when the payment was made

#### Common Use Cases:
1. Payment Tracking: Recording individual payments made against loans
2. Loan Management: Tracking payment history and outstanding balances


**plans**: Manages planning records for materials and manufacturing operations.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the plan
- `material` (int): Reference to the material
- `priority` (int): Priority level, defaults to 999999
- `percent` (double): Percentage value, defaults to 0

#### Common Use Cases:
1. Manufacture Planning: Managing material production plans, and settings priorities for the production of each material batch.


**percent_plans**: Manages percentage-based planning for materials.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the plan
- `material` (int): Reference to the material
- `priority` (int): Priority level, defaults to 999999
- `percent` (double): Percentage value, defaults to 0

#### Common Use Cases:
1. Production Planning: The ability to separate the production of each material batch into different percentages to be manufactured.
2. Priority Management: Prioritizing materials to be manufactured.


**permissions**: Manages user access rights and permissions.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the permission
- `criteria_id` (int): Reference to the criterion
- `user_id` (int): Reference to the user
- `type_col` (varchar(2)): Type of permission

#### Common Use Cases:
1. Access Control: Managing user permissions
2. Security Management: Controlling feature access
3. User Administration: Setting up user rights and permissions


**sales_targets**: Manages sales goals and targets for materials.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the target
- `material` (int): Reference to the material
- `year_col` (int): Target year
- `month_col` (int): Target month
- `location` (varchar(50)): Location for the target
- `target` (int): Target value

#### Common Use Cases:
1. Sales Planning: Setting and Tracking sales goals and projections for produced materials across different locations and different dates 
2. Generating Reports: Exporting the data into excel format


**users**: Manages user accounts and their associated information.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the user
- `name` (varchar(50)): Name of the user
- `password` (varchar(50)): Password of the user
- `email` (varchar(50)): Email of the user
- `group_id` (int): Reference to the group of the user
- `date_col` (timestamp): Date of the user creation

#### Common Use Cases:
1. User Management: Managing user accounts and their associated information
2. Authentication: Authenticating user credentials
3. Authorization: Controlling user access and permissions


**user_settings**: Manages user-specific configuration settings.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the setting
- `name` (varchar(50)): Name of the setting
- `value_col` (varchar(50)): Value of the setting (predefined strings the user's can't set manually)
- `user_id` (int): Reference to the user

#### Common Use Cases:
1. User Preferences: Storing user-specific settings
2. Interface Customization: Managing user display preferences to show shortcuts to actions the user uses the most
3. Application Configuration: Maintaining user-specific parameters


**settings**: Manages system-wide configuration values and preferences, providing a centralized storage for application settings.

#### Columns
- `id` (int): Primary key, auto-incrementing identifier for the setting record
- `name` (varchar(50)): Unique identifier name for the setting
- `value_col` (varchar(50)): Stored setting value

#### Common Use Cases:
1. Accounting and Financial Settings:
    - Configuration of opposite accounts for various transactions (buy, sell, return, input, output).
    - Monetary account assignments for different transaction types.
    - Cost price and invoice price tracking for various transactions.
    - Control over how discounts, additions, and cost values affect financial records.
2. Inventory Management
    - Defining how invoice types affect warehouse stock (add/reduce inventory).
    - Assigning warehouses for different invoice types.
    - Warehouse-based tracking for custom invoice types.
3. Gift and Promotional Item Handling
    - Configuration of separate accounts for handling gift transactions.
    - Opposite accounts for gift purchases, sales, and returns.
    - Specific price values for gift items in various transactions.
4. Transaction Price Calculations
    - Price settings for invoices, costs, and gifts in different transaction types.
    - Control over whether return transactions affect last recorded prices.
    - Discounts and additions affecting cost price and profit calculations.
5. Currency and Cost Center Management
    - Defining currencies for different transaction types.
    - Associating transactions with specific cost centers.
    - Handling cost allocations for return transactions.
6. System Configuration
    - Database connection settings (server, port, username, password).
    - Floating point precision settings for price calculations.
    - Inventory valuation method selection (periodic inventory type).
7. Custom Invoice Types
    - Configuration for special invoice types (e.g., raw_out, ready_in).
    - Warehouse, account, and pricing settings specific to custom invoice categories.
This table is mainly used to configure an ERP or accounting system, ensuring proper financial and inventory management.
