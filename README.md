## House-Hunting

This script finds homes in **London** from Rightmove, given a certain criteria.

It saves the properties into two separate CSVs and emails them: 
* Homes with Help-to-Buy initiative
* Homes without Help-to-Buy initiative

Rightmove sometimes seems to only show the top 1050 results even if it has found more. Therefore, instead of doing one search with our criteria, we do multiple searches to maximise the number of properties to check. It goes through every single station in London and checks for properties within a half a mile radius. Soon we would be able to filter by station, by line, zone and borough. 

### Criteria

* Min_Bed = The minimum number of bedrooms.
* Min_Price = The minimum price of the property.
* Max_Price = The maximum price for properties with Help to Buy initiative.
* lower_price = The maximum price for properties without Help to Buy
* Cash = Cash only properties. Put "no" to filter out cash-only properties.

### Extra

Eventually an option would be added to filter for certain houses depending on their images too. Work in progress.



