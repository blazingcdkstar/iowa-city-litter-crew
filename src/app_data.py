'''
Overall Process

Step 1: Import packages and create base columns variable.
Step 2: Import and formate data
Step 3: Create dataframe named litter_base with id vars
Step 4: Reshape data from wide to long, so that a unique record is the combination of the id and the item. 
        1 id is tied to 1 photo, and a photo can include more than 1 litter.

        a. Create data frame to capture the custom tag items. 
            - the custom tag columns contain column headers, not values, so this has to be reshaped 
              separately, and then added back to the dataframe at the end. I only do this for custom_tag_1. The dataframe
              will have columns: 'id', 'main_category', 'sub_category', and 'value'.
        
        b. Identify the column headers that are in all upper case. These are dummy columns to identify the main categorization
           of the litter item, they contain no data. Create a new dataframe for each main category with columns: 'id', 'main_category', 
           'sub_category', and 'value'. 
           The main categories are:  'alcohol', 'coffee', 'food', 'industrial', 'other', 'sanitary', 'softdrinks'

           

Step 5: Reshape address column. The address column is 1 long string with address components separated by commas. 
        I split out each component of the address field into separate columns. There are some irregularities with this data. For example,
        some records have place names rather than the street address, or some have a neighborhood designation and others do not. To facilitate
        litter by street block aggregation, I replace the place names with the street address. I remove the neighborhood designations so 
        that all addresses have the same number of components. After these steps there are addresses with 5 or 6 components. For those with 
        5 components are missing a house number. I add the column and fill with 0. This data is brought back together and then joined
        with the base data.

Exclusions:
I exclude the columns for brand and material identification. I have not done this identification with my data.

Variance:
There is a small variance between the sum of the total column in the raw data and the sum total in my final output.
This is because there is not a value in the total column in the raw data for items that are categorized in the custom_tag_1 column,
and because there are a handful of items where there is a flag for the item and for the material, and these
are getting double counted in the total column in the raw data, but they are counted once in my output.

Variance Examples:
ID 449030 is counted twice, as a straw and as plastic in the raw source data.
ID 459532 is custom tagged as a hair net, and has no value in the total column in the raw source data.

'''
#%%
#######################################################                             ############################################################
####################################################### < Step 1: Import Packages > ############################################################
#######################################################                             ############################################################

#%% Import Packages

# Data packages
import pandas as pd
pd.options.mode.chained_assignment = None

import numpy as np
import gc
import re

import plotly.express as px

# durations
from datetime import datetime


# herokuapp
import pathlib
PATH=pathlib.Path(__file__).parent
DATA_PATH = PATH.joinpath('data').resolve()

# create list of main base columns in dataset
base_columns = ['id', 'verification','phone', 'date_taken', 'date_taken_date', 'date_taken_yrmth',
                'date_uploaded', 'lat', 'lon', 'picked up', 'address']

#%%
######################################################                         #################################################################
###################################################### < Step 2: Import Data > #################################################################
######################################################                         #################################################################

#%% Import Data
#litter = pd.read_csv('Data\\OpenLitterMap.csv')

#litter_event = pd.read_csv('Data\\Cleanup_Events.csv')

# herokuapp
litter = pd.read_csv(DATA_PATH.joinpath('OpenLitterMap.csv'))

# herokuapp - load meetup event data
litter_event = pd.read_csv(DATA_PATH.joinpath('Cleanup_Events.csv'))

#%% make dates date data type
litter['date_taken'] = pd.to_datetime(litter['date_taken'])
litter['date_uploaded'] = pd.to_datetime(litter['date_uploaded'])

litter['date_taken_date'] = litter['date_taken'].dt.floor('d')
litter['date_taken_yrmth'] = litter['date_taken_date'].apply(lambda x: x.strftime('%Y-%m'))

litter_event['Date'] = pd.to_datetime(litter_event['Date'])


#%%
######################################################                                           ###############################################
###################################################### < Step 3: Create Base or Main DataFrame > ###############################################
######################################################                                           ###############################################

# %% create base df
litter_base = litter[[c for c in litter.columns if c in base_columns]]


#%%
######################################################                                          #################################################
###################################################### < Step 4a: Create Custom Tag DataFrame > #################################################
######################################################                                          #################################################

#%% Organize the data for custom tags

litter_orig = litter
litter_customtag = litter[['id', 'custom_tag_1']].dropna()

litter_customtag['main_category'] = 'custom_litter_type'
litter_customtag['value'] = 1.0

litter_customtag = litter_customtag.rename(columns={'custom_tag_1':'sub_category'})

litter_customtag = litter_customtag[['id', 'main_category', 'sub_category', 'value']]

litter_customtag['sub_category'] = litter_customtag['sub_category'].str.lower()

litter_customtag['sub_cat_2'] = ''
litter_customtag['sub_cat_3'] = ''
litter_customtag = litter_customtag.reset_index() 

for i in range(len(litter_customtag['id'])):
     litter_customtag.loc[i,'sub_cat_2'] = litter_customtag.loc[i, 'sub_category'].split(':')[0]
     litter_customtag.loc[i,'sub_cat_3'] = litter_customtag.loc[i, 'sub_category'].split(':')[1]


litter_customtag['sub_cat_2'] = litter_customtag['sub_cat_2'].str.replace('bn', 'brand_name')
litter_customtag['sub_cat_2'] = litter_customtag['sub_cat_2'].str.replace('ot', 'other')

litter_ct_brands = litter_customtag.loc[litter_customtag['sub_cat_2'] == 'brand_name']
litter_ct_brands = litter_ct_brands[['id', 'sub_cat_2', 'sub_cat_3', 'value']]
litter_ct_brands = litter_ct_brands.rename(columns = {'sub_cat_2': 'main_category',
                                           'sub_cat_3': 'sub_category'})


litter_ct_brands['sub_category'] = litter_ct_brands['sub_category'].str.strip()

litter_ct_brands_piv = litter_ct_brands.groupby('sub_category').agg(
     litter_count = pd.NamedAgg(column = 'value', aggfunc='sum')
).reset_index()

litter_ct_brands_piv = litter_ct_brands_piv.sort_values(by = 'litter_count', ascending=False).reset_index()

#litter_ct_brands_piv = litter_ct_brands_piv.loc[litter_ct_brands_piv['litter_count'] >= 5]

litter_ct_brands_piv = litter_ct_brands_piv[['sub_category', 'litter_count']]
litter_ct_brands_piv = litter_ct_brands_piv.rename(columns = {'sub_category':'Brand Name',
                                                'litter_count': 'Litter Count'})

litter_ct_other = litter_customtag.loc[litter_customtag['sub_cat_2'] == 'other']
litter_ct_other = litter_ct_other[['id', 'sub_cat_2', 'sub_cat_3', 'value']]
litter_ct_other = litter_ct_other.rename(columns = {'sub_cat_2': 'main_category',
                                           'sub_cat_3': 'sub_category'})

# remove the custom tag columns from the main dataset
#litter = litter.loc[:,~litter.columns.str.startswith('custom_tag')]
#litter = litter.loc[~litter['id'].isin(litter_customtag['id'])]

#%%
# create chart for brand names
'''
bn_chart = px.bar(litter_ct_brands_piv, x = 'litter_count', 
             y= 'sub_category',
             color='litter_count',
             color_continuous_scale=['steelblue', 'darkorange'],
             hover_data={'litter_count': True,
                         'sub_category': False},
             labels={'litter_count': 'Litter Count'},)
bn_chart.update_layout(yaxis=dict(autorange = 'reversed'))
bn_chart.update_layout(yaxis_title=None, 
                  xaxis_title = 'Brands Tagged with 5 Or More Litter Count', 
                  plot_bgcolor = 'lightgrey')
'''


#%%
###################################################### < Step 4b: Find Main Category Cols         > ####################################################
###################################################### < Create function clean_subset             > ####################################################
###################################################### < Create dataframes for each main category > ####################################################
###################################################### < and combine back with main base data set > ####################################################

# %% find the columns where the name is all caps. These are the main category columns.

col_names = pd.DataFrame(litter.columns.tolist())
col_names = col_names.rename(columns = {0: 'col_name'})
col_names['isupper'] = col_names.loc[col_names['col_name'].str.isupper(), :]
col_names_all = col_names
col_names = col_names.dropna()
col_names_index = col_names.index.tolist()

# %%
litter_base = litter.loc[:, base_columns]



#%% Create function to clean susbsetted data for each of the main categories.

# prefix is the main category name
def clean_subset(df_name,prefix):
    prefix = prefix + '_'
    df_name = df_name.rename(columns = lambda s: prefix + s)
    df_name = pd.concat([litter['id'], df_name], axis=1)
    df_name = df_name.melt(id_vars = 'id',
                           var_name = 'sub_category').dropna(subset=['value'])
    
    
    
    df_name['main_category'] = [x.split('_')[0] for x in df_name['sub_category']]
    df_name['sub_category'] = df_name['sub_category'].str.replace(prefix, '')

    df_name = df_name[['id', 'main_category', 'sub_category', 'value']]

    return(df_name)


#%% Create dataframes for each main category

litter_smoking = litter.iloc[:,col_names_index[0]:col_names_index[1]]
litter_smoking = clean_subset(litter_smoking, 'smoking')

litter_food = litter.iloc[:,col_names_index[1]:col_names_index[2]]
litter_food = clean_subset(litter_food, 'food')

litter_coffee = litter.iloc[:,col_names_index[2]:col_names_index[3]]
litter_coffee = clean_subset(litter_coffee, 'coffee')

litter_alcohol = litter.iloc[:,col_names_index[3]:col_names_index[4]]
litter_alcohol = clean_subset(litter_alcohol, 'alcohol')


litter_softdrinks = litter.iloc[:,col_names_index[4]:col_names_index[5]]
litter_softdrinks = clean_subset(litter_softdrinks, 'softdrinks')

litter_sanitary = litter.iloc[:,col_names_index[5]:col_names_index[6]]
litter_sanitary = clean_subset(litter_sanitary, 'sanitary')

litter_coastal = litter.iloc[:,col_names_index[6]:col_names_index[7]]
litter_coastal = clean_subset(litter_coastal, 'coastal')


litter_dumping = litter.iloc[:,col_names_index[7]:col_names_index[8]]
litter_dumping = clean_subset(litter_dumping, 'dumping')


litter_industrial = litter.iloc[:,col_names_index[8]:col_names_index[9]]
litter_industrial = clean_subset(litter_industrial, 'industrial')


#litter_brands = litter_ct_brands


litter_dogshit = litter.iloc[:,col_names_index[10]:col_names_index[11]]
litter_dogshit = clean_subset(litter_dogshit, 'dogshit')
litter_dogshit['main_category'] = 'pet_waste'

litter_other = litter.iloc[:,col_names_index[13]:289]
litter_other = clean_subset(litter_other, 'other')

litter_other['sub_category'] = (litter_other['sub_category']
                                .str.replace('plastic.1', 'unknown_plastic', regex=False))

litter_other['sub_category'] = (litter_other['sub_category']
                                .str.replace('paper.1', 'unknown_paper', regex=False))

litter_other['sub_category'] = (litter_other['sub_category']
                                .str.replace('metal.1', 'unknown_metal', regex=False))

litter_other['sub_category'] = (litter_other['sub_category']
                                .str.replace('balloons.1', 'balloons', regex=False))

litter_other = pd.concat([litter_other, litter_ct_other])

# split out plastic bags from other to a main category

litter_other.loc[litter_other['sub_category'] == 'plastic_bags', 'main_category'] = 'Plastic Bags'

#%% Combine data subsets into one data frame
litter_categories = pd.concat([litter_smoking, litter_food, litter_coffee, litter_alcohol,
                               litter_softdrinks, litter_sanitary, litter_coastal, litter_dumping,
                               litter_industrial, litter_dogshit, litter_other], axis= 0)
# %% Delete all the data frames and clear memory

del [[litter_smoking, litter_food, litter_coffee, litter_alcohol, litter_softdrinks,
      litter_sanitary, litter_coastal, litter_dumping, litter_industrial, litter_dogshit, 
      litter_other, litter_customtag]]

gc.collect()

# %% Combine the litter categories to the base litter data frame.

litter = litter_base.merge(litter_categories, how='right', on='id')
litter=litter.rename(columns = {'value': 'litter_count'})
litter['main_category'] = litter['main_category'].str.title()
litter['sub_category'] = litter['sub_category'].str.title()

#%%
###################################################### < Step 5: Clean and split Address          > ####################################################
###################################################### < Replace place names with add number      > ####################################################
###################################################### < Test address component count != 5 or 6   > ####################################################
###################################################### < Create a subset for 5 and 6 components   > ####################################################
###################################################### < Create a subset for 5 and 6 components   > ####################################################

#%%
# Create place name address reference table

place_name_address = [['L&M Mighty Shop', '504']
                      ,['La Petite Academy', '1504']
                      ,['Elizabeth Tate Alternative High School', '1528']
                      ,['Four Seasons Car Wash', '1455']
                      ,['Periodontal Associates', '1517']
                      ,['Mergen Orthodontics', '1540']
                      ,['Lower Muscatine @ Mall Dr', '1800']
                      ,['Lower Muscatine Ave @ Iowa City Maketplace', '1600']
                      ,['Kirkwood Community College - Iowa City Campus', '1816']
                      ,['Sports Column', '12']
                      ,['Assembly of God Church', '800']
                      ,['Deli Mart', '1700']
                      ,['First Christian Church', '200']
                      ,['Iowa City Public Library', '123']
                      ,["Jimmy Jack's Rib Shack", '1940']
                      ,['JOANN Fabrics and Crafts', '1676']
                      ,["McDonald's", '1861']
                      ,["Bradley's Cleaners", '19030']
                      ,['Oyama Sushi', '1853']
                      ,['Select Physical Therapy', '1555']
                      ,['Southeast Junior High School', '2501']
                      ,['Spenler Tire', '1455']
                      ,['Sycamore Mall', '1660']
                      ,['The Record Collector', '116']
                      ,['Wells Fargo', '103']
                      ,["Sueppel's Flowers", '1501']]

place_name_add_df = pd.DataFrame(place_name_address, columns = ['place_name', 'st_add'])
                      
#%%
street_suffix = ['Avenue', 'Ave', 'Street', 'St', 'Road', 'Rd', 'Drive', 'Dr', 'Boulevard', 'Blvd',
                 'Lane', 'Ln', 'Circle', 'Place', 'Pl', 'Court', 'Ct']

city_list = ['Iowa City', 'Coralville', 'Des Moines']

state_list = ['Iowa', 'Illinois']

#%%

address_cleanup = litter[['address']]
address_cleanup['split_count'] = address_cleanup['address'].str.count(',')
max_split = address_cleanup['split_count'].max()

address_cleanup[['split_1','split_2','split_3','split_4', 'split_5',
      'split_6', 'split_7', 'split_8', 'split_9']] = address_cleanup['address'].str.split(',', expand = True)


address_cleanup = pd.merge(address_cleanup, litter['id'], how = 'left', left_index=True, right_index=True)


#%%

''' Create a dataframe with a combined list of all splits, but in a column. So all split values are in one column, 
a label for which split the value is in, and then a label identifying which part of the address. This will then be re put 
back togehter in a row format.

COL 1: Litter ID
COL 2: VALUES FROM EACH OF THE SPLITS
COL 3: LABEL TO IDENTIFY WHAT PART OF THE ADDRESS THE SPLIT IS.

THEN SPREAD ACROSS COLUMNS BY THE LABEL IN NEW DATA FRAME.

'''


split_1 = address_cleanup[['id', 'split_1']]
split_1['split_label'] = 'split_1'
split_1 = split_1.rename(columns = {'split_1': 'split_value'})

split_2 = address_cleanup[['id', 'split_2']]
split_2['split_label'] = 'split_2'
split_2 = split_2.rename(columns = {'split_2': 'split_value'})

split_3 = address_cleanup[['id', 'split_3']]
split_3['split_label'] = 'split_3'
split_3 = split_3.rename(columns = {'split_3': 'split_value'})

split_4 = address_cleanup[['id', 'split_4']]
split_4['split_label'] = 'split_4'
split_4 = split_4.rename(columns = {'split_4': 'split_value'})

split_5 = address_cleanup[['id', 'split_5']]
split_5['split_label'] = 'split_5'
split_5 = split_5.rename(columns = {'split_5': 'split_value'})

split_6 = address_cleanup[['id', 'split_6']]
split_6['split_label'] = 'split_6'
split_6 = split_6.rename(columns = {'split_6': 'split_value'})

split_7 = address_cleanup[['id', 'split_7']]
split_7['split_label'] = 'split_7'
split_7 = split_7.rename(columns = {'split_7': 'split_value'})

split_8 = address_cleanup[['id', 'split_8']]
split_8['split_label'] = 'split_8'
split_8 = split_8.rename(columns = {'split_8': 'split_value'})

split_9 = address_cleanup[['id', 'split_9']]
split_9['split_label'] = 'split_9'
split_9 = split_9.rename(columns = {'split_9': 'split_value'})

comb_splits = pd.concat([split_1, split_2, split_3, split_4, split_5, split_6, split_7, split_8, split_9],
                        ignore_index=True)

comb_splits['split_value'] = comb_splits['split_value'].str.strip()

comb_splits['split_value'] = comb_splits['split_value'].str.replace('US-IA', 'USA', regex=False)
comb_splits['split_value'] = comb_splits['split_value'].str.replace('1/2', '', regex=False)

#%%
comb_splits['is_number'] = ''
for i in range(len(comb_splits['split_value'])):
    if comb_splits.loc[i,'split_value'] is None:
        comb_splits.loc[i,'is_number'] = 'NONE'

    #elif comb_splits[i,'split_value']

    elif re.findall(r'\d+', comb_splits.loc[i,'split_value']) != []:
        comb_splits.loc[i,'is_number'] = re.findall(r'\d+', comb_splits.loc[i,'split_value'])[0]
    
    else:
        comb_splits.loc[i,'is_number'] = "NA"



comb_splits['is_text'] = ''
for i in range(len(comb_splits['split_value'])):
    if comb_splits.loc[i,'split_value'] is None:
        comb_splits.loc[i,'is_text'] = 'NONE'

    elif re.findall(r'\D+', comb_splits.loc[i,'split_value']) != []:
        comb_splits.loc[i,'is_text'] = re.findall(r'\D+', comb_splits.loc[i,'split_value'])[0]
    
    else:
        comb_splits.loc[i,'is_text'] = "NA"


comb_splits['last_word'] = comb_splits['split_value'].str.split(" ").str[-1]


comb_splits['is_street'] = ''
for i in range(len(comb_splits['split_value'])):
    if comb_splits.loc[i,'split_value'] is None:
        comb_splits.loc[i,'is_street'] = 'NONE'

    else:
        comb_splits.loc[i,'is_street'] = comb_splits.loc[i,'last_word'] in street_suffix


#%%

comb_splits['split_category'] = ''
for i in range(len(comb_splits['split_value'])):
                   if comb_splits.loc[i,'split_value'] is None:
                    comb_splits.loc[i,'is_street'] = 'NONE'
                    comb_splits.loc[i,'split_category'] = 'NONE'

                   elif pd.to_numeric(comb_splits['is_number'][i], errors='coerce') > 50000:
                       comb_splits.loc[i,'split_category'] = 'zip'

                   elif (comb_splits.loc[i, 'is_number'] != 'NA' and comb_splits.loc[i,'is_text'] == 'NA') or (comb_splits.loc[i, 'is_number'] != 'NA' and comb_splits.loc[i,'is_text'] == ' ') :
                       comb_splits.loc[i,'split_category'] = 'address_number'
                    
                   elif comb_splits.loc[i, 'is_street'] == True:
                       comb_splits.loc[i,'split_category'] = 'street_address'
                    
                   elif comb_splits.loc[i, 'split_value'] in city_list:
                       comb_splits.loc[i,'split_category'] = 'city'
                    
                   elif comb_splits.loc[i, 'last_word'] == 'County':
                       comb_splits.loc[i,'split_category'] = 'county'
                   
                   elif comb_splits.loc[i, 'is_text'] in state_list:
                       comb_splits.loc[i,'split_category'] = 'state'

                   elif comb_splits.loc[i, 'is_text'] == 'USA':
                       comb_splits.loc[i,'split_category'] = 'country'
                   

                   else: comb_splits.loc[i,'split_category'] = 'place_name'
                        
#%%

comb_splits_fin = comb_splits[['id','split_label','split_value', 'split_category']]
comb_splits_fin['id'] = comb_splits_fin['id'].astype('string')

comb_splits_fin_w = comb_splits_fin.pivot_table(index='id', columns='split_category', values='split_value', aggfunc='max')

comb_splits_fin_w = comb_splits_fin_w[['address_number','place_name','street_address', 'city', 'county','state','country']]


comb_splits_fin_w = comb_splits_fin_w.reset_index()

comb_splits_fin_w = pd.merge(comb_splits_fin_w, place_name_add_df, 
                             how='left', left_on='place_name', right_on = 'place_name')

comb_splits_fin_w.loc[comb_splits_fin_w['address_number'].isnull(),'address_number'] = comb_splits_fin_w['st_add']

comb_splits_fin_w = comb_splits_fin_w.drop('st_add', axis=1)



# %% Aggregate by block number

# create new df named 'add_num' to identify if the value in the 'add_num' field is a number or text. 
# If it is a number, put in column 'add_is_num', if it is text put it in column 'add_is_text'.

comb_splits_fin_w['add_block_num'] = np.floor(comb_splits_fin_w['address_number'].astype(float)/100)
comb_splits_fin_w['add_block_num'] = comb_splits_fin_w['add_block_num'].astype(str).apply(lambda x: x.replace('.0',''))
comb_splits_fin_w['add_block_num'] = comb_splits_fin_w['add_block_num'].replace('0','10')

 # %%
'''
litter_add_final = pd.concat([litter_add_final, add_num], axis=1)
litter_add_final['add_blocknum_street'] = litter_add_final['add_block_num'].astype(str) + ' ' + litter_add_final['add_street']

litter_add_final = litter_add_final[['id', 'add_num', 'add_street', 'add_city', 'add_county', 'add_state', 'add_zip', 'add_country', 'add_block_num', 'add_blocknum_street']]

litter = pd.merge(litter, litter_add_final, on = 'id', how = 'left')
'''
#%%

litter = pd.merge(litter, comb_splits_fin_w, how = 'left', 
                       left_on = litter['id'].astype('str'), 
                       right_on=comb_splits_fin_w['id'].astype('str'))

litter = litter.drop(['id_y', 'key_0'],axis=1)
litter = litter.rename(columns = {'id_x': 'id'})

litter['add_block_num_st'] = litter['add_block_num'] + ' ' + litter['street_address']


# %%
# create new dataframe, 'df_latlon' to get the minimum latitude and minimum longitude by block
df_latlon = litter[['add_block_num_st', 'lat', 'lon']]
df_latlon = df_latlon.groupby('add_block_num_st')[['lat', 'lon']].min().reset_index()
df_latlon = df_latlon.rename(columns = {'lat': 'min_lat', 'lon': 'min_lon'})

litter = pd.merge(litter, df_latlon, on = 'add_block_num_st', how = 'left')

# %%
# create pivot table 'st_count' to show the number of times litter was picked up on that block
st_count = pd.DataFrame(litter.groupby(['add_block_num_st'])['date_taken_date'].nunique()).reset_index()
st_count = st_count.rename(columns = {'date_taken_date': 'total_count_pickup_dates'})
# %%
# create pivot table 'litter_sum' to show the total litter picked up at each block
litter_sum = pd.DataFrame(litter.groupby(['add_block_num_st'])['litter_count'].sum()).reset_index()
litter_sum = litter_sum.rename(columns = {'litter_count':'total_litter_pickedup'})

# %%
# join 'st_count' to 'litter_sum' using left join on 'add_blocknum_street'
litter_sum = pd.merge(litter_sum, st_count, on = 'add_block_num_st', how = 'left')
# calculate the average total litter picked up at each block per date
litter_sum['avg_litter_pickedup'] = round((litter_sum['total_litter_pickedup']) / (litter_sum['total_count_pickup_dates']),1)


# join the 'df_latlon' to 'litter_sum' to facilitate litter density on a street map
litter_sum = pd.merge(litter_sum, df_latlon, on = 'add_block_num_st', how = 'left')


#%% create place_name chart

pl_name = litter[['id', 'place_name', 'litter_count']]

pl_name = pl_name.dropna(axis = 0).reset_index()

pl_name = pl_name[['place_name', 'litter_count']]

pl_name = pl_name.groupby(['place_name']).agg(
     litter_count = pd.NamedAgg(column = 'litter_count', aggfunc='sum')
)

pl_name = pl_name.sort_values('litter_count', ascending=False).reset_index()
pl_name_fin = pl_name[['place_name', 'litter_count']]
pl_name_fin = pl_name_fin.rename(columns = {'place_name': 'Business Location',
                                            'litter_count': 'Litter Count'})

#%%
###################################################### < Step 6: Get Litter Pickup Durations       > ####################################################
###################################################### < Replace times when litter was picked      > ####################################################
###################################################### < up at different times through the day     > ####################################################
###################################################### < group data by date, am_pm                 > ####################################################
###################################################### < get min time, max time, duration, and litter count   > ####################################################

#%%

# replace values
# litter can be picked up several times throughout the day.
# I am going to replace time stamps so that duration is not impacted by this scenario


def update_time(myid, mydate):
    myindex = durations.index[durations['id'] == myid].tolist()
    durations.loc[myindex, 'date_taken'] = mydate

durations = litter[['id', 'phone', 'date_taken_date', 'date_taken', 'litter_count']]
# June 23, 2024

update_time(myid = 505104, mydate = '2024-06-23 15:02:00')
update_time(myid = 505105, mydate = '2024-06-23 15:04:00')
update_time(myid = 505158, mydate = '2024-06-23 15:07:00')
update_time(myid = 505159, mydate = '2024-06-23 15:09:00')
update_time(myid = 505165, mydate = '2024-06-23 15:10:00')

# November 25, 2023
update_time(myid = 491521, mydate = '2023-11-25 22:10:00')

# September 2, 2023
update_time(myid = 456907, mydate = '2023-09-02 19:15:00')
update_time(myid = 456908, mydate = '2023-09-02 19:16:00')
update_time(myid = 456909, mydate = '2023-09-02 19:17:00')
update_time(myid = 456910, mydate = '2023-09-02 19:18:00')

# September 16, 2023
update_time(myid = 463253, mydate = '2023-09-16 21:06:00')
update_time(myid = 463254, mydate = '2023-09-16 21:07:00')
update_time(myid = 463255, mydate = '2023-09-16 21:08:00')

# September 20, 2023
update_time(myid = 470493, mydate = '2023-09-20 13:50:00')
update_time(myid = 470289, mydate = '2023-09-20 13:52:00')

# September 23, 2023
update_time(myid = 471118, mydate = '2023-09-23 18:50:00')

# September 30, 2023
update_time(myid = 472973, mydate = '2023-09-30 21:22:00')

# October 19, 2023
update_time(myid = 483208, mydate = '2023-10-19 03:30:00')
update_time(myid = 483409, mydate = '2023-10-19 03:32:00')
update_time(myid = 483410, mydate = '2023-10-19 03:34:00')
update_time(myid = 483411, mydate = '2023-10-19 03:36:00')
update_time(myid = 483412, mydate = '2023-10-19 03:38:00')

# November 4, 2023
update_time(myid = 486039, mydate = '2023-11-04 18:15:00')
update_time(myid = 486040, mydate = '2023-11-04 18:17:00')

# November 10, 2023
update_time(myid = 486630, mydate = '2023-11-10 23:30:00')

# November 12, 2023
update_time(myid = 488682, mydate = '2023-11-12 16:42:00')
update_time(myid = 488683, mydate = '2023-11-12 16:44:00')

# November 18, 2023
update_time(myid = 489878, mydate = '2023-11-18 22:08:00')
update_time(myid = 489879, mydate = '2023-11-18 22:10:00')
update_time(myid = 489880, mydate = '2023-11-18 22:12:00')
update_time(myid = 489881, mydate = '2023-11-18 22:14:00')

# February 11, 2024
update_time(myid = 496952, mydate = '2024-02-11 20:40:00')

# August 14th, 2024
update_time(myid = 512591, mydate = '2024-08-14 13:56:00')
update_time(myid = 512592, mydate = '2024-08-14 13:58:00')

# August 20th, 2024
update_time(myid = 513314, mydate = '2024-08-20 20:40:00')


#%% split out litter pickups throughout the day by am/pm
# the time stamp is on gmt time, so when I walk Lulu is PM (AM CST) and when I walk Kipper is AM (PM CST).
# This does a good job of splitting out the 2 litter pickup events.
# But when it does not the time stamp is hard coded with previous code section.
# This prevents 2 litter events taking 1 hour to pick up do not show as 8 hours duration.

conditions = [
    (durations['date_taken'].dt.hour >= 12),
    (durations['date_taken'].dt.hour < 12)
]

results = ['pm', 'am']

durations['am_pm'] = np.select(conditions, results, default=pd.NaT)

durations['pick_up_event'] = durations['date_taken_date'].astype(str) + '_' + durations['am_pm']


#%% Aggregation
# get the earliest time stamp, the latest time stamp, and the sum of the litter count for each litter pick up event.

                                                
durations_piv = durations.groupby(['pick_up_event', 'phone']).agg(
    min_date=pd.NamedAgg(column="date_taken", aggfunc="min"),
    max_date=pd.NamedAgg(column="date_taken", aggfunc="max"),
    sum_litter=pd.NamedAgg(column="litter_count", aggfunc="sum")
)

#%% get durations

fmt = '%Y-%m-%d %H:%M:%S'
durations_piv['max_date_fmt'] = (durations_piv['max_date']
                                 .dt.strftime(fmt))

durations_piv['min_date_fmt'] = (durations_piv['min_date']
                                 .dt.strftime(fmt))

durations_piv['date_diff'] = durations_piv['max_date'] - durations_piv['min_date']

durations_piv['duration_mins'] = (durations_piv['date_diff'].dt.seconds)/60

durations_piv['litter_per_min']= durations_piv['sum_litter']/(durations_piv['duration_mins']+1)

avg_duration = round(durations_piv['duration_mins'].mean(),0).astype(int)

avg_litter_per_min = round(durations_piv['litter_per_min'].mean(),0).astype(int)


#%% clean up environment





