# COVID-19 Corona Virus tracking
Tracking and visualizition tool for the outbreak of Coronavirus COVID-19.

This is a Vizual Dashboard for the Coronavirus COVID-19 (former Novel Corona Virus nCoV-2019) based on data provided by the Johns Hopkins University Center for Systems Science and Engineering (JHU CCSE). The data is being downloaded on request in real-time from the time-series spredsheets they share publicly.
The dashboard reports cases at the province level in China, city level in the US, Australia and Canada, and at the country level otherwise.

 Data Sources JHU CCSE used:

    World Health Organization (WHO): https://www.who.int/
    Centers for Disease Control and Prevention (CDC): https://www.cdc.gov/
    European Centre for Disease Prevention and Control (ECDC): https://www.ecdc.europa.eu/en/home
    DXY: https://ncov.dxy.cn/ncovh5/view/pneumonia
    National Health Commission of the People's Republic of China (NHC): http://www.nhc.gov.cn/wjw/index.shtml

I started building this dashboard almost from the time JHU began collecting and sharing the data. Over a course of about 2 weeks they changed the method/format of delivery about 4 times, which is understandable giving the curcumstances. However because of that I had to change my algorithms of retrievng the data a few times, starting with web scraping technique. Hopefully they are settled now with the current format of spreadsheets, and with sharing them via GitHub.

I set up a VPS server with Flask running this dashboard. I use Folium for mapping, and Plotly.js for interactive line plots.
You may check the results at http://seedsfrom.space:5000/virus-ncov2019 .

# To Do:
- interactive change of geographical map to reflect spread of the virus;
- mapping air travel connections?
- adding more statistics.
