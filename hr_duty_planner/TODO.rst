ToDo list


**Models**
    * service template
        * DEV limit to 1 Container Service for off_duty type service
        * DEV management of working/holiday calendar
    * service allocate
        * DEV method to update all employees name list
    * service rule
        * DEV complete rule method management
    * calendar
        * DEV check module

**Views**
    * service template form
        * FIX custom css loading
        * FIX on deploy off_duty set to readonly
        * FIX layout
    * service allocate tree
        * FIX check rule button position
    * service allocate calendar
        * DEV text format
        * DEV lock action on empty cells
        * DEV check/alert template expected fulfillment
        * FIX employee name display (newline separated)
        * FIX element dedicated color (web_calendar)
    * service allocate timeline
        * DEV try add another level of group (ie. locality)
        * DEV check UIX
        * DEV check/alert template expected fulfillment
        * FIX element dedicated color (web_timeline)
    * service rule
        * DEV add profile reference to employee, equipment, vehicle
        * FIX on deploy lock edit option
        * FIX optimize double_assign method
    * service profile
        * FIX filter available fields for selected rule
        * DEV create check for rule-field assignment (association, mandatory)
    * reporting
        * DEV basic report


**Security**
    * FIX model authorizations


**Readme**
oca-gen-addon-readme --repo-name hr --branch 12.0 --addon-dir ~/odoo-dev/odoo12/OCA/addons-custom-sp/hr_duty_planner/
