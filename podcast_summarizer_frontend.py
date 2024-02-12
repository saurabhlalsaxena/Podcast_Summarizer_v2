import streamlit as st
import modal
import json
import os
import time  

# Define the function to create a dictionary from JSON files in a folder
def create_dict_from_json_files(folder_path):
    json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
    data_dict = {}

    for file_name in json_files:
        file_path = os.path.join(folder_path, file_name)
        with open(file_path, 'r') as file:
            podcast_info = json.load(file)
            podcast_name = podcast_info['Episode0']['podcast_title']
            # Process the file data as needed
            data_dict[podcast_name] = podcast_info

    return data_dict

# Main function to display episode information
def display_episodes(episodes_dump):
    episodes = episodes_dump
    for episode_key, episode_info in episodes.items():
        st.header(episode_info['episode_title'])
        st.subheader("Podcast Summary:")
        st.write(episode_info['podcast_summary'])
        st.subheader("Podcast Highlights:")
        highlights = episode_info['podcast_highlights']
        i=1
        for key, value in highlights.items():
            st.write(f"**{i}:** {value}")
            i=i+1
        st.markdown("---")  # Add a separator between episodes

#Process Podcast Info function
def process_podcast_info(url):
  output_week = {}
  for j in range(7):
    f = modal.Function.lookup("podcast-summarizer-project", "process_podcast")
    output = f.remote(j, url, '/content/podcast/')
    output_week[f"Episode{j}"] = output
  output_week_json = json.dumps(output_week, indent=4)
  return output_week_json

def onClick(selection_input):
    if selection_input == '0':
        st.session_state['selection'] = None

# Main Streamlit app
def main():

    # Load JSON data
    available_podcast_info = create_dict_from_json_files('.')

    podcast_options = list(available_podcast_info.keys())

    if 'selection' not in st.session_state:
      st.session_state['selection'] = 0

    selected_podcast = st.sidebar.selectbox("Select Podcast", podcast_options,index=st.session_state['selection'])
    

    if selected_podcast:
      # Display the podcast name and the cover image in a side-by-side layout
      col1, col2 = st.columns([7, 3])

      with col1:
          # Display the podcast name
          st.title(selected_podcast)
          st.subheader("Catch Up on the Latest 7 Episodes")

      with col2:
          # Display image above episodes
          st.image(available_podcast_info[selected_podcast]['Episode0']['episode_image'], caption='Episode Image', use_column_width=True)

      episodes_dump = available_podcast_info[selected_podcast]
      display_episodes(episodes_dump)

    # User Input box
    st.sidebar.subheader("Add and Process New Podcast Feed")
    url = st.sidebar.text_input("Link to RSS Feed")

    process_button = st.sidebar.button("Process Podcast Feed",on_click=onClick, args='0')
    st.sidebar.markdown("**Note**: Podcast processing can take upto 5 mins, please be patient.")

    if process_button:
      selected_podcast= None
      with st.spinner('Wait for it...'):
          # Call the function to process the URLs and retrieve podcast guest information
          podcast_info = json.loads(process_podcast_info(url))
          
      
      # Display the podcast name and the cover image in a side-by-side layout
      col1, col2 = st.columns([7, 3])

      with col1:
        # Display the podcast name
        st.title(podcast_info['Episode0']['podcast_title'])
        st.subheader("Catch Up on the Latest 7 Episodes")

      with col2:
        # Display image above episodes
        st.image(podcast_info['Episode0']['episode_image'], caption='Episode Image', use_column_width=True)

      episodes_dump = podcast_info
      display_episodes(episodes_dump)


if __name__ == "__main__":
    main()
