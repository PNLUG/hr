**Steps to follow to use Service Planner**

**Set up**

 **Rules**
  * Rules and Rules Fields can not be modified by Users. Read what they do and how to use fields.

 **Select Rules → Profile**
  * Create a Profile
  * Add rule fields with values
  * Add profile to Employees: Employees → get one → fill Service Profile
  * Add profile to Vehicle: Fleet → get one → fill Service Profile
  * Add profile to Equipment: Maintenance → Equipments → get one → fill Service Profile

 **Employee**
  * Create desired Skills: get an Employee → Skill tab → add row → create

 **Maintenance → Configuration → Categories**
  * Create desired Categories

 **Fleet**
  * Create desired Types: get a Vehicle → Vehicle Type → create

 **Select Template → Container Service**
  * Create a list of Container Services to collect single services

 **Select Template → Service Template**
  * Create a Template Service

   * Name, Container Service and Duration are mandatory
   * Check if it is an Off Duty Service (normally used to track some informations, ie. rest shifts)
   * Add requested Features to be sure to not forget to assign Resources.
     (Minimum quantity if  zero will not be considered)
   * Optional, associate a Next Service: this will be automatically generated starting form the end of this one.
   * Optional, set resources of parent service locked by the next service

 **Select Template → Service Template → your template**
  * Clik on *Generate Services* button
  * Template is preselected
  * Select a Container
  * Select a start date-time 
  * Select a stop date-time
  * Set repetition interval (hours). If interval is inferior to the template duration, this one will be used
  * Set available days of week
  * Set to use work Calendar
  * Set to use holiday
  * Click on *Generate* button

 **Planning**
  * Select Services → List view*
  * Select a Service
  * Fill resources (eg. Employee, Equipments, Vehicles)
  * Check requirements (Template requestested Resources) fulfillment
  * Calendar/Timeline: overview / move services
