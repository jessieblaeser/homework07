#!/usr/bin/env python
# coding: utf-8

# ### Do your imports!

# In[718]:


import pandas as pd
import numpy as np

#pd.set_option("display.max_colwidth", None)
pd.set_option("display.max_columns", None)


# # 311 data analysis
# 
# ## Read in `subset.csv` and review the first few rows
# 
# Even though it's a giant file – gigs and gigs! – it's a subset of the [entire dataset](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9). It covers plenty of years, but not all of the columns.
# 
# If your computer is struggling (which it will!) or you are impatient, feel free to use `nrows=` when reading it in to speed up the process by only reading in a subset of columns. Pull in at least a few million, or a couple years back.

# In[719]:


pd.read_csv("subset.csv", nrows=5000000)
df = pd.read_csv("subset.csv", nrows=5000000)

df.head()


# ### Where the subset came from
# 
# If you're curious, I took the [original data](https://data.cityofnewyork.us/Social-Services/311-Service-Requests-from-2010-to-Present/erm2-nwe9/data) and clipped out a subset by using the command-line tool [csvkit](https://csvkit.readthedocs.io/en/latest/).
# 
# First I inspected the column headers:
# 
# ```bash
# $ csvcut -n 311_Service_Requests_from_2010_to_Present.csv 
# ```
# 
# Then I selected the columns I was interested in and saved it to a file.
# 
# ```bash
# $ csvcut -c 1,2,3,4,5,6,7,8,9,10,16,17,20,26,29 311_Service_Requests_from_2010_to_Present.csv > subset.csv
# ```
# 
# This was much much much much faster than doing it in Python.

# ## We want more columns!
# 
# **Right now we don't see all of the columns.** For example, mine has `...` between the **Incident Address** column and the **City** column. Go up to the top where you imported pandas, and add a `pd.set_option` line that will allow you to view all of the columns of the dataset.

# In[720]:


df.columns


# ## We hate those column names!
# 
# Change the column names to be tab- and period-friendly, like `df.created_date` instead of `df['Created Date']`

# In[721]:


df.columns
df.columns.str.lower().str.replace(' ',"_")
df.columns = df.columns.str.lower().str.replace(' ',"_")
#df.columns


# # Dates and times
# 
# ## Are the datetimes actually datetimes?
# 
# We're going to be doing some datetime-y things, so let's see if the columns that look like dates are actually dates.

# In[722]:


df.created_date
df.closed_date


# ## In they aren't datetimes, convert them
# 
# The ones we're interested in are as follows:
# 
# * Created Date
# * Closed Date
# 
# You have two options to convert them:
# 
# 1. Do it like we did in class, but **overwrite the existing string columns with the new datetime versions**
# 2. Find an option with `read_csv` to automatically read certain columns as dates! Use the shift+tab trick to read the `read_csv` docs to uncover it. Once you find it, you'll set it to be the **list of date-y columns**.
# 
# They're both going to take forever if you do them wrong, but can be faster with a few tricks. For example, using `pd.to_datetime` can be sped up significantly be specifying the format of the datestring.
# 
# For example, if your datetime was formatted as `YYYY-MM-DD HH:MM:SS AM`, you could use the following:
# 
# ```
# df.my_datetime = pd.to_datetime(df.my_datetime, format="%Y-%m-%d %I:%M:%S %p")
# ```
# 
# It's unfortunately much much much faster than the `read_csv` technique. And yes, [that's `%I` and not `%H`](https://strftime.org/).
# 
# > *Tip: What should happen if it encounters an error or missing data?*

# In[723]:


pd.to_datetime(df.created_date, errors="coerce", format="%m/%d/%Y %I:%M:%S %p")
#QUESTION: where did my 'PM' go? %p should account for it? 
df.created_date = pd.to_datetime(df.created_date, errors="coerce", format="%m/%d/%Y %I:%M:%S %p")
#df.created_date


# In[724]:


pd.to_datetime(df.closed_date, errors="coerce", format="%m/%d/%Y %I:%M:%S %p")
#QUESTION: why did my AM/PM leave me :'( 
df.closed_date = pd.to_datetime(df.closed_date, errors="coerce", format="%m/%d/%Y %I:%M:%S %p")
#df.closed_date


# ## According to the dataset, which month of the year has the most 311 calls?
# 
# The kind of answer we're looking for is "January," not "January 2021"

# In[725]:


#df.head()
#df['month_created'] = pd.to_datetime(df.created_date, errors="coerce", format="%m").dt.strftime('%B')
#df.month_created.value_counts()
#NOTE: At first, I thought maybe I should be doing a str.extract here, but that would have do be done
    # before I converted the created_date column to DT format. 
    # Instead, I chose to create a new column and run value_counts().
    #QUESTION: still feeling like there's another way to do this one....
        #df['day_of_month'] = df.full_flowering_date.str.extract("\d\d\d\d/\d\d/\d\d)", expand=False)
        #df.date_of_incident.str.extract("(\d\d\d\d)", expand=False)
        #df.created_date.str.extract("(\d\d\)", expand=False)
            #and now have learned that I can create a variable, i don't have to create a full column

month = df.created_date.dt.strftime('%B')
month.value_counts()

#instead, if you want to put things in groups based on a column, use groupby
#if you want to put things into groups temporally, use resample
#df.resample('M', on='created_date').size().sort_values()


# ## According to the dataset, which month has had the most 311 calls?
# 
# The kind of answer we're looking for is "January 2021," not "January" (although _techniucally_ it will say `2021-01-31`, not `January 2021`)

# In[726]:


#df.created_date.value_counts()
#QUESTION: based on the sub instructions above, is this all we need to do for this? 

# year = df.created_date.dt.strftime('%Y')
# #year.value_counts()
# month_year = month + ' ' + year
# month_year.value_counts()

df.resample('M', on='created_date').size().sort_values(ascending=False)


# ## Plot the 311 call frequency over our dataset on a _weekly_ basis
# 
# To make your y axis start at zero, use `ylim=(0,100000)` when doing `.plot`. But replace the `1000` with a large enough value to actually see your data nicely!

# In[728]:


df = df.dropna(subset=['created_date'])

#df.rolling(7, on='year', min_periods=7)['created_date'].mean()
#df.rolling(7, on='created_date', min_periods=7).mean()
df.rolling(7, on='created_date', min_periods=7).mean().plot


# ## What time of day (by hour) is the most least for 311 complains? The most common?
# 

# In[729]:


# # Answer for least-common hours to make complaints
# hour = df.created_date.dt.strftime('%H')
# hour.value_counts().tail()
# hour.value_counts().head()
# #....this was so much easier than I thought (unless I'm still doing it wrong!)


# In[730]:


df.created_date.dt.hour.value_counts().sort_index()


# ### Make a graph of the results
# 
# * Make sure the hours are in the correct order
# * Be sure to set the y-axis to start at 0
# * Give your plot a descriptive title

# In[731]:


#hour.value_counts()
hour.value_counts().sort_index().plot()

    


# # Agencies
# 
# ## What agencies field the most complaints in the dataset? Get the top 5.
# 
# Use the `agency` column for this one.

# In[732]:


df.agency.value_counts().head()


# ## What are each of those agencies?
# 
# Define the following five acronyms:
# 
# * NYPD
# * HPD
# * DOT
# * DSNY
# * DEP

# In[733]:


# NYPD: New York Police Dept.
# HPD: Housing Preservation & Development
# DOT: Department of Transportation
# DSNY: Department of Sanitation New York
# DEP: Department of Environmental Protection 

df[df.agency == 'NYPD'].agency_name.head(1)
df[df.agency == 'HPD'].agency_name.head(1)
df[df.agency == 'DOT'].agency_name.head(1)
df[df.agency == 'DSNY'].agency_name.head(1)
df[df.agency == 'DEP'].agency_name.head(1)

#NOTE/QUESTION: possibly could use a lambda here??


# ## What is the most common complaint to HPD?

# In[734]:


df.complaint_type.value_counts().head(1)


# ## What are the top 3 complaints to each agency?
# 
# You'll want to use the weird confusing `.groupby(level=...` thing we learned when reviewing the homework.

# In[735]:


df.groupby(by='agency').complaint_type.value_counts()
df.groupby(by='agency').complaint_type.value_counts().groupby(level=0, group_keys=False).head(3)
#df.groupby(['Borough']).Neighborhood.value_counts().groupby(level=0, group_keys=False).head(5)
#https://stackoverflow.com/questions/35364601/group-by-and-find-top-n-value-counts-pandas

#NOTE: from reading the documentation, I still don't quite understand what "level" does in groupby clauses


# In[736]:


#Here is all of my work trying things that did not work for the above question before finding the right answer 
    #(or at least what i think is the right answer)
#df.agency.value_counts().head(3).groupby(by='agency', level=0).complaint_type.value_counts()
    #df.groupby(by='Style').ABV.median().plot(kind='hist')
#df.agency.value_counts().groupby(by='complaint_type', level=0).sum()
    # this gives me the number of complaints per agency in no particular order
    
#df.groupby(by='agency', level=0).complaint_type.value_counts()
#df.groupby(by='agency', level=0)['complaint_type'].value_counts(ascending=False)
#df.groupby(by='agency')['complaint_type'].value_counts(ascending=False)
#df.groupby(by =='NYPD').complaint_type.value_counts()


df[df.agency == 'NYPD'].complaint_type.value_counts().head(3)
df[df.agency == 'HPD'].complaint_type.value_counts().head(3)
df[df.agency == 'DSNY'].complaint_type.value_counts().head(3)
df[df.agency == 'DOT'].complaint_type.value_counts().head(3)
df[df.agency == 'DEP'].complaint_type.value_counts().head(3)


#how could i do this in a single line of code??


# ## What is the most common kind of residential noise complaint?
# 
# The NYPD seems to deal with a lot of noise complaints at homes. What is the most common subtype?

# In[737]:


#df.complaint_type.value_counts()
#Noise - Residential                      2821
#df.head()

# Searching via text how many complaints contain the word "Noise"
#df.complaint_type.str.contains("Noise", na=False).value_counts()
    #4985 contain "Noise"

#df.complaint_type.str.contains("noise", na=False).value_counts()
    # Just to check, no complaints contain "noise"

# Looking into all noise-type compliants: 
#df[df.complaint_type.str.contains("Noise")]

df[df.complaint_type.str.contains("Noise")].descriptor.value_counts().head(1)
#HALLELUJAH


# ## What time of day do "Loud Music/Party" complaints come in? Make it a chart!

# In[738]:


# #df[df.descriptor == 'Loud Music/Party']
df['hour'] = df.created_date.dt.strftime('%H')
# df[df.descriptor == 'Loud Music/Party'].hour.value_counts().sort_index()
df[df.descriptor == 'Loud Music/Party'].created_date.dt.hour.value_counts().sort_index()


# In[739]:


#df[df.descriptor == 'Loud Music/Party'].hour.value_counts().sort_index().plot(title='Time of day for Loud Music/Party Noise complaints')

df[df.descriptor == 'Loud Music/Party'].created_date.dt.hour.value_counts().sort_index().plot(title='Time of day for Loud Music/Party Noise complaints')


# ## When do people party hard?
# 
# Make a monthly chart of Loud Music/Party complaints since the beginning of the dataset. Make it count them on a biweekly basis (every two weeks).

# In[740]:


df['month'] = df.created_date.dt.strftime('%B')

#df[df.descriptor == 'Loud Music/Party'].month.value_counts().sort_index().plot(title='Time of year for Loud Music/Party Noise complaints')

df[df.descriptor == 'Loud Music/Party'].resample('2W', on='created_date').size().plot()


# ## People and their bees
# 
# Sometimes people complain about bees! Why they'd do that, I have no idea. It's somewhere in "complaint_type" – can you find all of the bee-related complaints?

# In[742]:


# Checking out how many bee complaints we are dealing with within the rows read in above
df.complaint_type.str.contains("Bee", na=False).value_counts()

# Looking into all bee-type compliants: 
df[df.complaint_type.str.contains("Bee")]
#'Harboring Bees/Wasps'


# ### What month do most of the complaints happen in? I'd like to see a graph.

# In[748]:


df[df.complaint_type.str.contains("Bee")].month.value_counts().plot(kind='bar', title='Bee complaints in NYC by month', color='yellow')

#JESSIE: does this work too?
#df[df.complaint_type.str.contains("Bee")].resample('M', on='created_date').size().plot()


# ### Are the people getting in trouble usually beekeepers or not beekeepers?

# In[749]:


df[df.complaint_type.str.contains("Bee")]
#df[df.descriptor.str.contains("beekeper")]
    #why does this give me an error about non-boolean arrays? --> OH NAN
    
#df = df.dropna(subset=['descriptor'])
df.descriptor.value_counts()
df.descriptor.str.contains("beekeper", na=False).value_counts()
#would really need to turn first line into a column in order to do the above? 

# WHY DID THEY MISSPELL 'BEEKEEPER' EVERY SINGLE TIME


# # Math with datetimes
# 
# ## How long does it normally take to resolve a 311 complaint?
# 
# Even if we didn't cover this in class, I have faith that you can guess how to calculate it.

# In[750]:


df.columns

(df.closed_date - df.created_date).median()


# Save it as a new column called `time_to_fix`

# In[751]:


df['time_to_fix'] = df.closed_date - df.created_date
df.time_to_fix


# ## Which agency has the best time-to-fix time?

# In[752]:


df = df.dropna(subset=['time_to_fix'])

df.groupby(by='agency').time_to_fix.median().groupby(level=0, group_keys=False).head(1).sort_values()

# Applied the same logic as in the question about Top 3 Complaints for each agency
# Decided to drop NaN values bc we already dropped for created_date
    # And NaN values seemed to be interfering with my .mean()

#QUESITON: mean or meadian for this set of Q's? 


# ## Maybe we need some more information...
# 
# I might want to know how big our sample size is for each of those, maybe the high performers only have one or two instances of having requests filed!
# 
# ### First, try using `.describe()` on the time to fix column after your `groupby`.

# In[754]:


df.groupby(by='agency').describe()


# ### Now, an alternative
# 
# Seems a little busy, yeah? **You can also do smaller, custom aggregations.**
# 
# Try something like this:
# 
# ```python
# # Multiple aggregations of one column
# df.groupby('agency').time_to_fix.agg(['median', 'size'])
# 
# # You can also do something like this to reach multiple columns
# df.groupby('agency').agg({
#     'time_to_fix': ['median', 'size']
# })
# ```

# In[757]:


df.groupby('agency').time_to_fix.agg(['median', 'size'])


# In[758]:


df.groupby('agency').agg({
    'time_to_fix': ['median', 'size']
})


# ## Seems weird that NYPD time-to-close is so fast. Can we break that down by complaint type?
# 
# Remember the order: 
# 
# 1. Filter
# 2. Group
# 3. Grab a column
# 4. Do something with it
# 5. Sort

# In[759]:


# # Filter
# df[df.agency == 'NYPD']

# # Group + grab a column

# df[df.agency == 'NYPD'].groupby(by='agency').complaint_type

# # Do something with it! 

# df[df.agency == 'NYPD'].groupby(by='agency').complaint_type.value_counts()

# # Sort

df[df.agency == 'NYPD'].groupby(by='agency').complaint_type.value_counts().sort_values(ascending=False)


# ## Back to median fix time for all agencies: do these values change based on the borough?
# 
# First, use `groupby` to get the median time to fix per agency in each borough. You can use something like `pd.set_option("display.max_rows", 200)` if you can't see all of the results by default!

# In[760]:


df.groupby(['agency', 'borough']).time_to_fix.agg(['median', 'size'])
#df.borough.value_counts()
#df.groupby(by='agency').borough.value_counts()
#df.groupby(by='agency').borough.value_counts().time_to_fix.median().groupby(level=0, group_keys=False)
#df.groupby(by='agency').time_to_fix.median().groupby(level=0, group_keys=False).borough.value_counts()


# In[761]:


#df.groupby(by='agency').borough.value_counts().time_to_fix.agg(['median', 'size'])


# ### Or, use another technique!

# We talked about pivot table for a hot second in class, but it's (potentially) a good fit for this situation:
# 
# ```python
# df.pivot_table(
#     columns='what will show up as your columns',
#     index='what will show up as your rows',
#     values='the column that will show up in each cell',
#     aggfunc='the calculation(s) you want dont'
# )
# ```

# In[762]:


# Back to median fix time for all agencies: do these values change based on the borough?
# First, use groupby to get the median time to fix per agency in each borough.

#we want median time-to-fix in each borough 
#in a graph, that would be a bar chart 
#in a table, columns would be time-to-fix
#rows would be each boro (but could be reversed, doesnt really matter )

df.pivot_table(
    columns='borough',
    index='agency',
    values='time_to_fix',
    aggfunc=['median', 'size'],
)


# ### Use the pivot table result to find the worst-performing agency in the Bronx, then compare with Staten Island
# 
# Since it's a dataframe, you can use the power of `.sort_values` (twice!). Do any of the agencies have a large difference between the two?

# In[763]:


df_pivot = df.pivot_table(
    columns='borough',
    index='agency',
    values='time_to_fix',
    aggfunc='median',
)

df_pivot.sort_values(by='BRONX')


# In[764]:


df_pivot.sort_values(by='STATEN ISLAND')


# In[ ]:





# ## What were the top ten 311 types of complaints on Thanksgiving 2020? Are they different than the day before Thanksgiving?
# 
# **Finding exact dates is awful, honestly.** While you can do something like this to ask for rows after a specific date:
# 
# ```python
# df[df.date_column >= '2020-01-01']
# ```
# 
# You, for some reason, can't ask for an **exact match** unless you're really looking for exactly at midnight. For example, this won't give you what you want:
# 
# ```python
# df[df.date_column == '2020-01-01']
# ```
# 
# Instead, the thing you need to do is this:
# 
# ```python
# df[(df.date_column >= '2020-01-01') & (df.date_column < '2020-01-02']
# ```
# 
# Everything that starts at midnight on the 1st but *is still less than midnight on the 2nd**.

# In[768]:


df[(df.created_date >= '2020-11-26') & (df.created_date < '2020-11-27')].complaint_type.sort_values().head(10)
#only two complaints for Thanksgiving Day 2020 in the 5,000,000 rows read in


# In[770]:


df[(df.created_date >= '2020-11-25') & (df.created_date < '2020-11-26')].complaint_type.sort_values().head(10)
#There were more complaints for the day before Thanksgiving, but they matched one of the two for Thanksgiving Day


# ## What is the most common 311 complaint types on Christmas day?
# 
# And I mean *all Christmas days*, not just in certain years)
# 
# * Tip: `dt.` and `&` are going to be your friend here
# * Tip: If you want to get fancy you can look up `strftime`
# * Tip: One of those is much much faster than the other

# In[771]:


#i think you could use strftime to convert all 12/25 values to "christmas day "
df['month_day'] = df.created_date.dt.strftime('%m/%d')
df.month_day.head()
#christmas_complaints = df[df.month_day == "12/25"]


# In[804]:


christmas_df = df[df.month_day == 12/25 ]
christmas_df.complaint_type.value_counts(ascending=False)
# Not sure what is going wrong here! 


# # Stories
# 
# Let's approach this from the idea of **having stories and wanting to investigate them.** Fun facts:
# 
# * Not all of these are reasonably answered with what our data is
# * We only have certain skills about how to analyzing the data
# * There are about six hundred approaches for each question
# 
# But: **for most of these prompts there are at least a few ways you can get something interesting out of the dataset.**

# ## Fireworks and BLM
# 
# You're writing a story about the anecdotal idea that the summer of the BLM protests there were an incredible number of fireworks being set off. Does the data support this?
# 
# What assumptions is your analysis making? What could make your analysis fall apart?

# In[777]:


# Checking out how many firework complaints we are dealing with within the rows read in above
df.complaint_type.str.contains("Firework", na=False).value_counts()

# Looking into all firework compliants: 
df[df.complaint_type.str.contains("Firework")]
# 'Illegal Fireworks'

# To start this story, I would plot the number of firework complaints by year.
    # Then, I would try to isolate summer-ish months firework complainst, so I might only plot by the months of May-Aug. for each year

    #I'm going to make a month_year column for ease

df['month_year'] = df.created_date.dt.strftime('%m/%Y')


# In[801]:


df[df.complaint_type.str.contains("Firework")].month_year.value_counts().sort_values(ascending=False).plot(kind='bar')
#Ideally this would be chronological, not sure why sorting values is going to Firework counts, rather than month_year values


# ## Sanitation and work slowdowns
# 
# The Dept of Sanitation recently had a work slowdown to protest the vaccine mandate. You'd like to write about past work slowdowns that have caused garbage to pile up in the street, streets to not be swept, etc, and compare them to the current slowdown. You've also heard rumors that it was worse in Staten Island and a few Brooklyn neighborhoods - Marine Park and Canarsie - than everywhere else.
# 
# Use the data to find timeframes worth researching, and note how this slowdown might compare. Also, is there anything behind the geographic issue?
# 
# What assumptions is your analysis making? What could make your analysis fall apart?

# In[781]:


# Want to ask df for times where there have been a lot of sanitation complaints 
# First, isolate Dept of Sanitation complints     
df[df.agency == 'DSNY']

# Now, I want to take a look at the kinds of complainst DSNY usually gets
df[df.agency == 'DSNY'].complaint_type.value_counts()

# Could look for top 3 complaints for DSNY across month_year
df[df.agency == 'DSNY'].groupby(by='month_year').complaint_type.value_counts().sort_values(ascending=False).head(3)
    # This will give me the top 3 complaints to the DSNY for every month_year it recieved complaints


# In[800]:


#Now I want to plot the number of total complaints to the NYDS by month_year to look for general upticks and dips
df[df.agency == 'DSNY'].month_year.value_counts().sort_values(ascending=False).plot()

# This graph is not the way I want it to be! 

# I would then look at the month_years with the dips in the plot below and look for correspondning top 3 complaints based on function above
# These would be my timeframes worth researching + insight on what ppl were complaining abt during those months


# In[783]:


# Now I want to bring neighborhood into the mix 
df[df.agency == 'DSNY'].borough.value_counts()
    #This shows me the number of DSNY complaints in each borough

# I want to know how this number changes based off the months worth researching above 

df[df.agency == 'DSNY'].groupby(by='month_year').borough.value_counts()
# To get down to the specific neighborhood within each borough, I think I'd have to join neighborhood data based on zipcode
    # Or I could do some sort of geolocation based on icident address? 


# In[784]:


#"What assumptions is your analysis making? What could make your analysis fall apart?"

# This analysis assumes complaints to NYSD are consistent/not impacted by any other outside factors other than more reasons to complain 


# ## Gentrification and whining to the government
# 
# It's said that when a neighborhood gentrifies, the people who move in are quick to report things to authorities that would previously have been ignored or dealt with on a personal basis. Use the data to investigate the concept (two techniques for finding gentrifying area are using census data and using Google).
# 
# What assumptions is your analysis making? What could make your analysis fall apart? Be sure to cite your sources. 

# In[787]:


df.head()
# https://patch.com/new-york/new-york-city/these-nyc-neighborhoods-are-among-nations-most-gentrified
# according to this article, zip codes to investigate for years leading up to 2018 are: 
    #10039
    #10026
    #11211
    #11222
    #11216
# In the real world, I would prereport the above much more and get a definitive list of zips to investigate after talking to experts and locals + researching economic data 
# For the purposes of this exercise, I'm going to take a look at the first two zips 

df[df.incident_zip == '10039'].resample('Y', on='created_date').size().sort_values(ascending=False).plot(title='Complaints count in 10039 over time')
# NOTE: complaints do seem to have increased after 2018, but I'd need to investigate other reasons why that might be before assuming it's a result of gentrification


# In[788]:


df[df.incident_zip == '10026'].resample('Y', on='created_date').size().sort_values(ascending=False).plot(title='Complaints count in 10026 over time')
# NOTE: same as above


# In[789]:


#For further investigation: 
    # I could also take a look at most common complaints over time to see if they changed 


# In[790]:


#"What assumptions is your analysis making? What could make your analysis fall apart?"

    # Does not account for outside factors changing complaint rate in certain zipcodes
    # Does not account for specific new problems in zip codes 


# ## 311 quirks
# 
# Our editor tried to submit a 311 request using the app the other day, but it didn't go through. As we all know, news is what happens to your editor! Has the 311 mobile app ever actually stopped working?
# 
# If that's a dead end, maybe you can talk about the differences between the different submission avenues: could a mobile outage disproportionately impact a certain kind of complaint or agency? How about if the phone lines stopped working?
# 
# What assumptions is your analysis making? What could make your analysis fall apart?

# In[791]:


#looking for hours where complaints coming in are zero 
df.resample('Y', on='created_date').size().sort_values(ascending=False).plot()
    #NOTE: I'm doing 'year' here bc I worry by 'hour' will overload my computer


# In[792]:


# Now, looking at the most common channels for making complaints 
df.open_data_channel_type.value_counts()

# Need to combine these two concepts, first by isolating mobile-type complaints

#Experimenting with mobile-type complaints
df[df.open_data_channel_type == 'MOBILE'].complaint_type.value_counts()

mobile_df = df[df.open_data_channel_type == 'MOBILE']

mobile_df.resample('Y', on='created_date').size().sort_values(ascending=False).plot()
#NOTE: again wanting to break this down by week, isolate peaks, and then look by hour
    #I'm very worried about my computer's capacity to that, so I'm just sharing my intention for now :/ 


# In[793]:


#"could a mobile outage disproportionately impact a certain kind of complaint or agency?"
    #"How about if the phone lines stopped working?"

# The following will show the top 3 agencies that recieve complaints via app,
    # which would show the agencies most likely to be affected by 311 app outage
mobile_df.agency.value_counts().head(3)

# The following will show the top 3 complaint types submitted via mobile app,
    # which would show the complaints most likely to dip in the event of an app outage 
mobile_df.complaint_type.value_counts().head(3)


# In[794]:


#"How about if the phone lines stopped working?"

#The following will show top complaint types and agencies for complaints by phone
    #This could provide a contrast to the mobile submissions above 
df[df.open_data_channel_type == 'PHONE'].complaint_type.value_counts().head(3)
df[df.open_data_channel_type == 'PHONE'].agency.value_counts().head(3)


# In[795]:


#"What assumptions is your analysis making? What could make your analysis fall apart?""

#In this particular analysis, we are assuming that a dip in mobile submissions means the app crashed
    # which is not necessarily true 


# ## NYCHA and public funds
# 
# NYC's public housing infrastructure is failing, and one reason is lack of federal funds. While the recent spending bills passed through Congress might be able to help, the feeling is that things have really fallen apart in the past however-many years – as time goes on it gets more and more difficult for the agency in control of things to address issues in a timely manner.
# 
# If you were tasked with finding information to help a reporter writing on this topic, you will **not** reasonably be able to find much in the dataset to support or refute this. Why not? 
# 
# If you wanted to squeeze something out of this dataset anyway, what could an option be? (You might need to bring in another dataset.)

# In[796]:


#"If you were tasked with finding information to help a reporter writing on this topic, 
    # you will **not** reasonably be able to find much in the dataset to support or refute this. Why not?" 

# Answer: It does not appear that NYCHA complaints are included in 311 data
df.agency.value_counts()


# In[797]:


#If you wanted to squeeze some insight/direction out of this dataset, I would isolate complaints to HPD

# This would show me the complaints ranked in order of frequency submitted to HPD
df[df.agency == 'HPD'].complaint_type.value_counts()


# In[798]:


# Next, I would plot complaint frequency to HPD over time
df[df.agency == 'HPD'].resample('M', on='created_date').size().sort_values(ascending=False).plot(title='Complaints to HPD over time')

# This could help the team look at highs/lows in complaint frequency to HPD, an agency ajacent to NYCHA
    # This info would likely not be reported in this story, but it could help inform questions and direction when investigating NYCHA complaints
    # Even so...this could be a flawed approach, bc the organizations are not the same. So I wouldn't want this data analysis to lead to a miss when digging around NYCHA


# In[ ]:





# In[ ]:




