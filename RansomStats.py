import json
import hashlib
import datetime
import calendar
import pandas as pd
import plotly.express as px
import requests
#Todo:
#add functionality to upload HTML to website

#Download json
url='https://raw.githubusercontent.com/joshhighet/ransomwatch/main/posts.json'
extension = '.json'
req = requests.get(url)

filename = url.split("/")[-1]
#Open json
with open (filename, 'wb') as file:
    file.write(req.content)

#Function to get stats for specified period
def getStats(period):    
    with open ("posts.json", "r", encoding="UTF8") as read_file:
        data = json.load(read_file)
    now = datetime.datetime.now()
   
    if period == "year":
        timeframe = now.isocalendar().year
        filtered_data = [post for post in data if (datetime.datetime.fromisoformat(post['discovered'])).year == timeframe]
    
    if period == "week":
       # Calculate the start and end of the current week
        week_start = now - datetime.timedelta(days=now.weekday())
        week_end = week_start + datetime.timedelta(days=6)
        start = week_start.strftime('%Y-%m-%d')
        end = week_end.strftime('%Y-%m-%d')
        timeframe = str(start) +  ' - ' +  str(end)
        # Convert the 'discovered' field to a datetime object and filter the data
        filtered_data = [post for post in data if week_start.date() <= datetime.datetime.fromisoformat(post['discovered']).date() <= week_end.date()]
    
    if period == "month":
        month_start = datetime.datetime(now.year, now.month, 1)
        month_end = month_start + datetime.timedelta(days=calendar.monthrange(now.year, now.month)[1] - 1)
        start = month_start.strftime('%Y-%m-%d')
        end = month_end.strftime('%Y-%m-%d')
        timeframe = str(start) + ' - ' + str(end)
        # Convert the 'discovered' field to a datetime object and filter the data
        filtered_data = [post for post in data if month_start <= datetime.datetime.fromisoformat(post['discovered']) <= month_end]
    
    if period == "today":
        timeframe = str(now.date())
        filtered_data = [post for post in data if datetime.datetime.fromisoformat(post['discovered']).date() == now.date()]

    group_names = []
    timestamps = []
    title = []
    for post in filtered_data:
        group_names.append(post['group_name'])
        timestamps.append(post['discovered'])
        title.append(post['post_title'])

    outputGraph = period + "graph"
    outputTable = period + "table"
    # Convert the lists into a Pandas dataframe
    df = pd.DataFrame({'Group Name': group_names, 'Timestamp': timestamps, 'Title': title})
    
    
    # Convert the timestamps into a datetime format
    df['Timestamp'] = pd.to_datetime(df['Timestamp']).dt.floor('S')
    # Group and sort the data by the number of postings in each group
    df_sorted = df.groupby('Group Name').size().reset_index(name='count').sort_values(by='count', ascending=True)

    # Use Plotly's Scatter plot to visualize the data
    fig = px.bar(df_sorted, x='Group Name', y='count', color='count', title='Posting Frequency by Group for {timeframe}'.format(timeframe=timeframe), color_continuous_scale='Portland')
    #Remove scale from output (gave issues with HTML)
    fig.update_coloraxes(showscale=False)
    #Write the graph to HTML
    fig.write_html(outputGraph + ".html")
    #Invert table, showing newest entries first
    df = df[::-1]
    #Start index at 1
    df.index = df.index + 1
    #Convert dataframe to HTML
    html = df.to_html(justify='center', classes="table table-striped table-hover")
    # Creating the HTML file
    file_html = open(outputTable + ".html", "w")
    #Write the dataframe to HTML file
    file_html.write('''<html>
    <head>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.2.3/dist/js/bootstrap.min.js" integrity="sha384-cuYeSxntonz0PPNlHhBs68uyIAVpIIOZZ5JqeqvYYIcEL727kskC66kF92t6Xl2V" crossorigin="anonymous"></script>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@4.3.1/dist/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    </head>
    <body>
    {html}
    </body>
    </html>'''.format(html=html))
    # Saving the data into the HTML file
    file_html.close()
    file.close()
#Function to run stats-function
def runScript():
    getStats("week")
    getStats("year")
    getStats("month")
    getStats("today")

#Get checksum of json
with open("posts.json","rb") as f:
    bytes = f.read() # read file as bytes
    readable_hash = hashlib.md5(bytes).hexdigest()
try:
    #Open a file that holds previous checksum
    with open("checksum", "r") as hash:
        oldsum = hash.read()
        #Exit script if checksum is unchanged
        if readable_hash == oldsum:
            hash.close()
            exit()
        else:
            #Continue with script if checksum if changed and write current checksum to file
            with open("checksum","w") as hash:
                hash.write(readable_hash)
                hash.close()
            runScript()
            #Add current time to "lastrun"
            with open("lastrun", "w") as lastrun:
                lastrun.write("last update: " + str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
                lastrun.close()
except IOError:
        #If checksum file does not exist, run script, write checksum to file and update "lastrun". 
        print("File not accessible")
        with open("checksum", "w") as hash:
            hash.write(readable_hash)
            hash.close()
        runScript()
        with open("lastrun", "w") as lastrun:
            lastrun.write("Last update: " + str(datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")))
            lastrun.close()
