""" Name: Chase Ryan
 CS230: Frydenberg
 Section 6 Data: Volcanos
 Which data set you used URL: downloaded through brightspace
 Link to your web application on Streamlit Cloud (if posted)
Description: This program takes the volcano data in the volcano.csv and uses streamlit to create a website displaying
data and relevant info. Utilizing various python functions like dictionaries, charts, and maps, country data
based on volcanoes is expressed. """

import numpy as np
import streamlit as st
import csv
import statistics
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import random
import pydeck as pdk
# python -m streamlit run

def read_data():
    #[PY3]
    try:
        #read in file and change some names for cleanup, skip first row, and number is index
        #endoing = latin1 https://www.roelpeters.be/unicodedecodeerror-utf-8-codec-cant-decode-byte-in-position/
        df = pd.read_csv("volcanoes.csv", skiprows=1, encoding= 'latin1',).set_index('Volcano Number')
        #https://stackoverflow.com/questions/11346283/renaming-column-names-in-pandas
        df = df.rename(columns={"Volcano Name": "Name", "Elevation (m)": "Elevation"})
        #[DA7] drop a column
        df = df.drop(columns= ["Tectonic Setting"])
        #[DA1]
        #[DA9] #create a new column that is elevation based on the height using lambda
        df["Elevation Category"] = df["Elevation"].apply(lambda x: "Low (<1000m)" if x < 1000 else "Medium (1000-3000m)" if x < 3000 else "High (>3000m)")
        #make sure there is a value for longitude and latitude(for map)
        df = df.dropna(subset= ['Latitude','Longitude'])
        #[DA2] sort all by elevation
        #https://stackoverflow.com/questions/17141558/how-to-sort-a-pandas-dataframe-by-two-or-more-columns
        df = df.sort_values(by='Elevation', ascending=True)
        return df
    #if no file print
    except Exception as e:
        st.write("Could not find data file",e)
        return none


df = read_data()
#[PY1] set default value
def filter_data(sel_country=["Japan"],max_elevate= 6000,min_elevate=-1000):
    df = read_data()
    #only dataframe with the country
    df = df.loc[df["Country"].isin(sel_country)]
    #[DA5] only volcanoes below the max elevation AND above the minimum
    #https://stackoverflow.com/questions/21415661/logical-operators-for-boolean-indexing-in-pandas
    df= df[(df["Elevation"]< max_elevate) & (df["Elevation"] > min_elevate)]
    #drops for accuracy
    df = df.dropna(subset= ['Latitude','Longitude'])
    return df

#[PY2] function return two values
def stats(df):
    #calc average elevation
    avg_height = df["Elevation"].mean().round(1)

    min_height = df["Elevation"].min()
    return avg_height,min_height


#[MAP] displays the volcanoes on a world map
def make_map(df):
    map_df = df.filter(['Name','Latitude','Longitude','Country']) #get needed columns
    #center
    view_state = pdk.ViewState(latitude=map_df["Latitude"].mean(), longitude = map_df["Longitude"].mean(),zoom = 3)
    #mak scatterplotlayer
    layer = pdk.Layer("ScatterplotLayer",data = map_df, get_position = '[Longitude,Latitude]',get_radius= 30000,
    get_color = '[300,100,20]',pickable=True)
    #on hover show
    tool_tip = {'html':'Volcano:<br><b>{Name}</b><br>Country:<b>{Country}</b>','style':{'backgroundColor':'steelblue','color':'white'}}
#make the map
    map = pdk.Deck(map_style = 'mapbox://styles/mapbox/light-v9',
                   initial_view_state = view_state,
                   layers = [layer],
                   tooltip =tool_tip)
    st.pydeck_chart(map)
#function for all countries
def all_countries():
    df = read_data()
    lst = []
    #[DA8] using iterrows
    for ind, row in df.iterrows():
        if row['Country'] not in lst:
            lst.append(row['Country']) #add country if not in yet
    return lst
def count_countries(countries,df):
    #[PY4] count the number of volcanoes for each country
    lst = [df.loc[df["Country"].isin([country])].shape[0] for country in countries]
    return lst
#group elevation values by country
def country_elevations(df):
    elevations = [row['Elevation']for ind, row in df.iterrows()] #elevations
    countries = [row['Country']for ind, row in df.iterrows()] #extract all country values
    dict = {}
    for country in countries:
        dict[country] = []
        #add each value to the list
    for i in range(len(elevations)):
        dict[countries[i]].append(elevations[i])
    return dict
#[PY5]
def country_averages(dict_elevation):
    avgdict = {}
    for key in dict_elevation.keys():
        avgdict[key] = np.mean(dict_elevation[key]) #compute the mean for each  list
    return avgdict
#[CHART 1]
def pie_chart(counts,sel_countries):
    plt.figure()
    explodes = [0 for i in range(len(counts))]
    maximum = counts.index(np.max(counts))
    explodes[maximum] =.25 #pull off biggest slice
    plt.pie(counts, labels= sel_countries, explode =explodes, autopct = '%.2f')
    plt.title(f"Volcanoes by Country: {', '.join(sel_countries)}")

    return plt
#[CHART 2]
def bar_chart(dict_averages):
    plt.figure()
    x= dict_averages.keys() #country names
    y = dict_averages.values() #elevations averaged
    plt.bar(x,y,color='red')
    plt.xticks(rotation=45) #rotate labels
    plt.ylabel("Elevation")
    plt.xlabel('Countries')
    plt.grid() #add grid https://discuss.streamlit.io/t/grid-lines-inside-bar-chart/45959
#add title
    plt.title(f"Average Volcano Elevation for countries:{', '.join(dict_averages.keys())}")
    return plt



def main():

    st.title('Data visualization with Python')
    st.write("Welcome to volcano data, open the sidebar to begin")

    # [ST1] Navigation Tabs via radio
    #https://docs.streamlit.io/develop/api-reference/widgets/st.radio
    page = st.radio("Select Section", ["Volcano Map", "Charts", "Summary Stats"])

    # [ST4] Sidebar filters and multiselect
    st.sidebar.write("Please choose your options to display data")
    #[St2]
    max_elevation = st.sidebar.slider("Max Elevation: ", -1000, 6000)
    min_elevation = st.sidebar.slider("Min Elevation: ", -1000, 6000)
    #[ST3]
    selected_countries = st.sidebar.multiselect("Select Countries", all_countries())

    # Default and filtered datasets
    default_df = filter_data()
    if selected_countries:
        filterdf = filter_data(selected_countries, max_elevation, min_elevation)
    else:
        filter_df = default_df
#volcano page map
    if page == "Volcano Map":
        #[ST4]
        # https: // docs.streamlit.io / develop / api - reference / media / st.image
        st.image("volcano.jpg")
        st.write("Example map with Default parameters(Japan)")
        #[PY1]called with defalt values
        make_map(default_df)
        #[PY1] called with selected values
        if selected_countries:
            st.write("New Map")
            make_map(filterdf)
#charts page
    elif page == "Charts":
        if selected_countries:
            st.write("Pie Chart")
            counts = count_countries(selected_countries, filterdf)
            st.pyplot(pie_chart(counts, selected_countries))

            st.write('Bar Chart')
            elevationdict = country_elevations(filterdf)
            averages = country_averages(elevationdict)
            st.pyplot(bar_chart(averages))

        else:
            st.write("Please select countries to view charts.")
#stats
    elif page == "Summary Stats":
        st.write("Stats for Default (Japan)")
        avg, min = (stats(default_df))
        st.write(f"The average elevation for Japan is {avg} and the minimum elevation is {min}")

        if selected_countries:
            st.write("Stats for Selected Countries")
            savg, smin = stats(filterdf)
            st.write(f"The average elevation for the selected is {savg} and the minimum elevation is {smin}")

main()
