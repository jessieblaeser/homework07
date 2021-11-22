#!/usr/bin/env python
# coding: utf-8

# # Cherry Blossoms!
# 
# If we travel back in time, [cherry blossoms](https://en.wikipedia.org/wiki/Cherry_blossom) were once in full bloom! We don't live in Japan or DC, but in non-COVID times we also have the [Brooklyn Botanic Garden's annual festival](https://www.bbg.org/visit/event/sakura_matsuri_2020).
# 
# We'll have to make up for it with data-driven cherry blossoms instead. Once upon a time [Data is Plural](https://tinyletter.com/data-is-plural) linked to [a dataset](http://atmenv.envi.osakafu-u.ac.jp/aono/kyophenotemp4/) about when the cherry trees blossom each year. It's completely out of date, but it's quirky in a real nice way so we're sticking with it.
# 
# ## 0. Do all of your importing/setup stuff

# In[190]:


import pandas as pd
import numpy as np


# ## 1. Read in the file using pandas, and look at the first five rows

# In[191]:


pd.read_excel("KyotoFullFlower7.xls")
df = pd.read_excel("KyotoFullFlower7.xls")
df.head()


# ## 2. Read in the file using pandas CORRECTLY, and look at the first five rows
# 
# Hrm, how do your column names look? Read the file in again but this time add a parameter to make sure your columns look right.
# 
# **TIP: The first year should be 801 AD, and it should not have any dates or anything.**

# In[192]:


pd.read_excel("KyotoFullFlower7.xls", header=25)
df = pd.read_excel("KyotoFullFlower7.xls", header=25)
df.head()


# ## 3. Look at the final five rows of the data

# In[193]:


df.tail()


# ## 4. Add some more NaN values

# It looks like you should probably have some NaN/missing values earlier on in the dataset under "Reference name." Read in the file *one more time*, this time making sure all of those missing reference names actually show up as `NaN` instead of `-`.

# In[194]:


pd.read_excel("KyotoFullFlower7.xls", header=25)
df = pd.read_excel("KyotoFullFlower7.xls", header=25, na_values = ['-'])
df.head()


# In[195]:


df.columns
df.columns.str.lower()
df.columns.str.lower().str.replace(" ","_")
df.columns = df.columns.str.lower().str.replace(" ","_").str.replace("-","_").str.replace("(","").str.replace(")","")
df.columns
#I know it's not necessary to write all these out line by line—it's just helping me remember the steps! 


# ## 4. What source is the most common as a reference?

# In[196]:


#df.source_code.value_counts()
df.source_code.mode()


# ## 6. Filter the list to only include columns where the `Full-flowering date (DOY)` is not missing
# 
# If you'd like to do it in two steps (which might be easier to think through), first figure out how to test whether a column is empty/missing/null/NaN, get the list of `True`/`False` values, and then later feed it to your `df`.

# In[197]:


#df.full_flowering_date_doy.value_counts()(dropna=False)
#NOTE: I got the above from class notes when we tried to view null values in Sex column of CHI death data
    # not sure why it isn't working for me here? 
    
df.full_flowering_date_doy.notnull().value_counts()


# In[198]:


df = df.dropna(subset=['full_flowering_date_doy'])
df.full_flowering_date_doy


# ## 7. Make a histogram of the full-flowering date

# In[199]:


df.full_flowering_date_doy.hist()
#NOTE: assuming here that we are still working with the column mentioned above, "full-flowering date (doy),"
    # rather than the separate "full-flowering date" column, which we work with below.


# ## 8. Make another histogram of the full-flowering date, but with 39 bins instead of 10

# In[200]:


df.full_flowering_date_doy.hist(bins=39)


# ## 9. What's the average number of days it takes for the flowers to blossom? And how many records do we have?
# 
# Answer these both with one line of code.

# In[201]:


df.full_flowering_date_doy.describe()


# ## 10. What's the average days into the year cherry flowers normally blossomed before 1900?
# 
# 

# In[202]:


df[df.ad < 1900].full_flowering_date_doy.mean()


# ## 11. How about after 1900?

# In[203]:


df[df.ad > 1900].full_flowering_date_doy.mean()


# ## 12. How many times was our data from a title in Japanese poetry?
# 
# You'll need to read the documentation inside of the Excel file.

# In[204]:


df[df.data_type_code == 4].data_type_code.value_counts()


# ## 13. Show only the years where our data was from a title in Japanese poetry

# In[205]:


df[df.data_type_code == 4]


# ## 14. Graph the full-flowering date (DOY) over time

# In[206]:


df.full_flowering_date_doy.plot()


# ## 15. Smooth out the graph
# 
# It's so jagged! You can use `df.rolling` to calculate a rolling average.
# 
# The following code calculates a **10-year mean**, using the `AD` column as the anchor. If there aren't 20 samples to work with in a row, it'll accept down to 5. Neat, right?
# 
# (We're only looking at the final 5)

# In[207]:


df.rolling(10, on='ad', min_periods=5)['full_flowering_date_doy'].mean().tail()


# In[208]:


df['rolling_date'] = df.rolling(20, on='ad', min_periods=5)['full_flowering_date_doy'].mean()
df.rolling_date.plot(ylim=(80, 120))
#QUESTION: are we meant to still be looking at the tail here? 
# tail 
#df.company.value_counts(ascending=False).plot.barh(x='company', y='number of bills',
#              title='comps with the most bills', color='green')


# Use the code above to create a new column called `rolling_date` in our dataset. It should be the 20-year rolling average of the flowering date. Then plot it, with the year on the x axis and the day of the year on the y axis.
# 
# Try adding `ylim=(80, 120)` to your `.plot` command to make things look a little less dire.

# ### 16. Add a month column
# 
# Right now the "Full-flowering date" column is pretty rough. It uses numbers like '402' to mean "April 2nd" and "416" to mean "April 16th." Let's make a column to explain what month it happened in.
# 
# * Every row that happened in April should have 'April' in the `month` column.
# * Every row that happened in March should have 'March' as the `month` column.
# * Every row that happened in May should have 'May' as the `month` column.
# 
# There are **at least two ways to do this.**
# 
# #### WAY ONE: The bad-yet-simple way
# 
# If you don't want to use `pd.to_datetime`, you can use this as an sample for updating March. It finds everything with a date less than 400 and assigns `March` to the `month` column:
# 
# ```python
# df.loc[df['Full-flowering date'] < 400, 'month'] = 'March'
# ```
# 
# #### WAY TWO: The good-yet-complicated way
# 
# * When you use `pd.to_datetime`, if pandas doesn't figure it out automatically you can also pass a `format=` argument that explains what the format is of the datetime. You use [the codes here](https://strftime.org/) to mark out where the days, months, etc are. For example, `2020-04-09` would be converted using `pd.to_datetime(df.colname, "format='%Y-%m-%d")`.
# * `errors='coerce'` will return `NaN` for missing values. By default it just yells "I don't know what to do!!!"
# * And remember how we used `df.date_column.dt.month` to get the number of the month? For the name, you use `dt.strftime` (string-formatted-time), and pass it [the same codes](https://strftime.org/) to tell it what to do. For example, `df.date_column.dt.strftime("%Y-%m-%d")` would give you `"2020-04-09"`.

# In[209]:


pd.to_datetime(df.full_flowering_date, errors='coerce', format='%m%d')


# In[210]:


df.full_flowering_date = pd.to_datetime(df.full_flowering_date, errors="coerce", format="%m%d")


# In[212]:


df['month'] = pd.to_datetime(df.full_flowering_date, errors="coerce", format="%m%d").dt.strftime('%B')
#df.month


# ### 17. Using your new column, how many blossomings happened in each month?

# In[213]:


df.month.value_counts()


# ### 18. Graph how many blossomings happened in each month.

# In[214]:


df.month.value_counts().plot(kind='barh')


# ### 19. Adding a day-of-month column
# 
# Now we're going to add a new column called `day_of_month.` It might be a little tougher than it should be since the `Full-flowering date` column is a *float* instead of an integer.
# 
# *Tip: If your method involves `.astype(int)` it isn't going to work since it's missing data, you can add `.dropna().astype(int)` instead.*

# In[215]:


# df['day_of_month'] = pd.to_datetime(df['full_flowering_date'], format='%m%d').dt.day
# df.day_of_month


# In[216]:



df['day_of_month'] = pd.to_datetime(df.full_flowering_date, errors="coerce", format="%m%d").dt.strftime('%d')
#df['day_of_month'] = df.full_flowering_date.str.extract("\d\d\d\d/\d\d/\d\d)", expand=False)
df.day_of_month

#QUESTION: DOES THIS NEED TO BE A STR OR A FLOAT


# In[217]:


#str(df.day_of_month)


# ### 20. Adding a date column
# 
# If you don't have one yet, take the `'month'` and `'day_of_month'` columns and combine them in order to create a new column called `'date'`. You could alternatively use `.dt.strftime` as mentioned above.

# In[218]:


df['date'] = df['month'] + ' ' + df['day_of_month']


# In[219]:


df.date


# # YOU ARE DONE.
# 
# And **incredible.**

# In[ ]:


#yay! 

