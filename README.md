## House-Hunting

This script finds homes in London from Rightmove, given a certain criteria.

It saves the properties into two separate CSVs and emails them: 
* Homes with Help-to-Buy initiative
* Homes without Help-to-Buy initiative

By separating them we can put different boundaries. Since homes with Help-To-Buy could mean an increase in budget.

`search_results('x','y','z','w','r',"c","h","t")`

* x = minimum number of rooms
* y = maximum price
* z = minimum price
* w = number of properties on Rightmove to check
* r = radius from London (miles to 1dp)
* c = cash buyer. Put "no" to avoid cash buyer only properties
* h = help to buy. Put "yes" to only get properties that mention help to buy
* t = good transport. Put "yes" to only get properties that either have an underground, overground or DLR close to them i.e. not rail.
