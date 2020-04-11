# PROJECT 2: Texas Wind Energy

<p align="center"> <img src= "https://media.giphy.com/media/4sw6pWhQQBN5K/giphy.gif" </p>

From the Hill Country to the Great Plains and Mountains, Texas makes up approximately 7% of the total water and land area of the US, an area only second to Alaska. With the varying topography and climate, it's no wonder Texas leads the nation in Energy production from oil and natural gas, to coal, wind and solar. According to the US Energy Information Administation (US EIA), Texas makes up 20% of US domestically produced Energy and is the leading producer of wind generated electricity.

As the leading producer of wind energy, you might wonder how that plays a role in the cost of energy. Well, due to the varying nature of wind, the cost of energy tends to fluctuate radically throughout the day. Generally speaking, when the wind blows, costs of energy might drop, and when the wind isn't blowing, and energy is dependant on more traditional sources, the costs then to go up. But by how much? Is there a way to predict the cost of energy at a certain point in time? Our project will try and figure that out by taking a deeper look into the publicly available data.

## Data Source & Database

The **Electric Reliability Council of Texas (ERCOT)** manages the flow of electric power to more than 26 million Texas customers -- representing about 90 percent of the state’s electric load. It also performs financial settlement for the competitive wholesale bulk-power market and administers retail switching for 8 million premises in competitive choice areas. 

ERCOT Real-Time Market:

During real-time, ERCOT dispatches resources based on economics and reliability to meet the system demand while observing resource and transmission constraints. Security Constrained Economic Dispatch (SCED) is the real-time market evaluation of offers to produce a least-cost dispatch of online resources. SCED calculates Locational Marginal Prices (LMPs) using a two-step methodology that applies mitigation to resolve non-competitive constraints.

ERCOT Real-Time Data Sources:

- **[SCED System Lambda](http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13114&reportTitle=SCED%20System%20Lambda&showHTMLView=&mimicKey):** The system wide price of energy (System Lambda) at five minute intervals.
- **[Wind Power Production](http://mis.ercot.com/misapp/GetReports.do?reportTypeId=13071&reportTitle=Wind%20Power%20Production%20-%20Actual%205-Minute%20Averaged%20Values&showHTMLView=&mimicKey):** This report is posted every 5 minutes and includes System-wide and Regional actual 5-min averaged wind power production for a rolling historical 60-minute period.

The data is scraped using from the csv zip files on the ERCOT webpage using requests and beautiful soup and placed into a **JAWS DB** database with the data from both sources merged on the SCEDTimeStamp column.

## Plots

### Time Series Plot

#### Wind Generation and System Lambda vs. Time

The time series plot looks at wind generation and the system wide price of energy (System Lambda) at 5 minute time intervals throughout the day. This plot helps to understand the nature of how the data changes each passing moment.

<img src= "/static/images/timeseries.png">

### Correlation Plot

#### Wind Generation vs. System Lambda

The correlation plot looks at the relationship *between* the System Lambda and wind generation. By including each quantity on a different axis, this plot allows the user to visualize the overall effect of wind on energy prices in ERCOT.

<img src= "/static/images/correlation.png">

## Heroku Deployment

The Texas Wind Energy web app is deployed via **Heroku**. It can be found [here](https://yeeaa-project-2.herokuapp.com/)!

## Final Thoughts

### Results

Based on the energy data we have gathered up until April 11th, 2020, it appears that **as wind generation increases, the price of energy decreases.** Our time series plot shows that spikes in the price of energy tend to occur at times when wind generation has fallen, and the trendline on the correlation plot shows a steady decrease in price with wind generation.

### Difficulties

Although the correlation plot seems to show a clear correlation on this trendline, there are some imperfections in the way this is was obtained. Namely, the price axis must be logarithmic to easily visualize the trend; however, *some of the prices are negative* and thus have no logarithmic value. Therefore, the logarithmic adjustment of price has no mathematical basis and is only a convenient way to find a visual correlation. Despite this drawback, there are only a few data points with negative prices, so our correlation plot validates the idea that such a relationship could be uncovered after the underlying market and physical phenomena are more appropriately accounted for.