from googleapiclient.discovery import build
import seaborn as sb
import pandas as pd 

api_key = ""
channel_ids = ["UC14UlmYlSNiQCBe9Eookf_A", "UCWV3obpZVGgJ3j9FVhEjF2Q","UCkzCjdRMrW2vXLx8mvPVLdQ","UCLzKhsxrExAC6yAdtZ-BOWw",
"UCU2PacFf99vhb3hNiYDmxww","UCt9a_qP9CqHCNwilf-iULag","UCZkcxFIsqW5htimoUQKA0iA","UCKcx1uK38H4AOkmfv4ywlrg","UC9LQwHZoucFT94I2h6JOcjw","UC6yW44UGJJBvYTlfC7CRg2Q"]

youtube = build("youtube","v3",developerKey=api_key)

def get_channel_stats(youtube,channel_ids):
    all_data = []
    req = youtube.channels().list(
        part="snippet, contentDetails, statistics",
        id = ",".join(channel_ids)
    )
    response = req.execute()
    for i in range(len(response["items"])):
        data = dict(channel_name = response["items"][i]["snippet"]["title"],
                playlist_id = response["items"][i]["contentDetails"]["relatedPlaylists"]["uploads"] ,
                subscribers = response["items"][i]["statistics"]["subscriberCount"],
                views = response["items"][i]["statistics"]["viewCount"],
                total_videos = response["items"][i]["statistics"]["videoCount"] )
        all_data.append(data)
            
    return all_data

channel_stats = get_channel_stats(youtube, channel_ids)
channel_info = pd.DataFrame(channel_stats)

#formatting for seaborn
channel_info["subscribers"] = pd.to_numeric(channel_info["subscribers"])
channel_info["views"] = pd.to_numeric(channel_info["views"])
channel_info["total_videos"] = pd.to_numeric(channel_info["total_videos"])

#resize canvas
sb.set(rc={"figure.figsize":(30,10)})

#comparison by subscribers
ax = sb.barplot(x="channel_name", y="subscribers", data = channel_info)

#comparison by views
ax = sb.barplot(x="channel_name", y="views", data = channel_info)

#comparison by video count
ax = sb.barplot(x="channel_name", y="total_videos", data = channel_info)

#id's from dataframe
playlist_id = channel_info.loc[channel_info["channel_name"]=="FC Barcelona","playlist_id"].iloc[0]

def get_video_ids(youtube, playlist_id):
    
    request = youtube.playlistItems().list(
                part='contentDetails',
                playlistId = playlist_id,
                maxResults = 50)
    response = request.execute()
    
    video_ids = []

#because of limit of 50 records in api      

    for i in range(len(response['items'])):
        video_ids.append(response['items'][i]['contentDetails']['videoId'])
        
    next_page_token = response.get('nextPageToken')
    isNextPageExist = True
    
    while isNextPageExist:
        if next_page_token is None:
            isNextPageExist = False
        else:
            request = youtube.playlistItems().list(
                        part='contentDetails',
                        playlistId = playlist_id,
                        maxResults = 50,
                        pageToken = next_page_token)
            response = request.execute()
    
            for i in range(len(response['items'])):
                video_ids.append(response['items'][i]['contentDetails']['videoId'])
            
            next_page_token = response.get('nextPageToken')
        
    return video_ids

video_ids = get_video_ids(youtube, playlist_id)




def get_video_stats(youtube, video_ids):
    all_video_stats = []


    for i in range(0, len(video_ids), 50):
        request = youtube.videos().list(
                    part='snippet,statistics',
                    id=','.join(video_ids[i:i+50]))
        response = request.execute()
        
        for video in response['items']:
            video_stats = dict(Title = video['snippet']['title'],
                               Published_date = video['snippet']['publishedAt'],
                               Views = video['statistics']['viewCount'],
                               Likes = video['statistics']['likeCount'],
                               Comments = video['statistics']['commentCount']
                               )
            all_video_stats.append(video_stats)
    
    return all_video_stats

video_details = get_video_stats(youtube, video_ids)
video_data = pd.DataFrame(video_details)

video_data['Published_date'] = pd.to_datetime(video_data['Published_date']).dt.date
video_data['Views'] = pd.to_numeric(video_data['Views'])
video_data['Likes'] = pd.to_numeric(video_data['Likes'])
video_data['commentCount'] = pd.to_numeric(video_data['commentCount'])

#summary data
top10_videos = video_data.sort_values(by='Views', ascending=False).head(10)
ax1 = sns.barplot(x='Views', y='Title', data=top10_videos)

#export result to csv
video_data.to_csv('analyze.csv')
