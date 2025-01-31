import opentimelineio as otio
import opentimelineio.opentime as otio_time
from videojungle import ApiClient  
import os 

def create_skateboarding_timeline(api_client: ApiClient, query: str = "skateboarding", limit: int = 10) -> otio.schema.Timeline:
    """
    Searches for skateboarding videos using the API client and creates an OTIO timeline.

    Args:
        api_client (ApiClient): An instance of your API client.
        query (str): The search query (default: "skateboarding").
        limit (int): Maximum number of videos to include (default: 10).

    Returns:
        otio.schema.Timeline: The generated timeline containing the found clips.
    """
    # Perform the search for skateboarding videos.
    search_results = api_client.video_files.search(query=query, limit=limit)
    
    # Create a video track for the timeline.
    video_track = otio.schema.Track(name="Skateboarding Videos", kind="Video")
    print(f"search results: {search_results}")
    for video_data in search_results:
        # Retrieve detailed video information.
        video = api_client.video_files.get(video_data["video_id"])
        
        # Determine fps and duration (using defaults if necessary).
        fps = video.fps if video.fps else 24.0
        duration_secs = video.duration if video.duration else 10.0  # Default duration if missing
        
        # Create a source range starting at 0 with the given duration.
        start_time = otio_time.RationalTime(0, fps)
        clip_duration = otio_time.RationalTime(duration_secs, fps)
        
        # Build an external reference to the media.
        # Adjust the target_url as needed (e.g., a URL or file path to your video).
        media_ref = otio.schema.ExternalReference(target_url=video.filename)
        
        # Create an OTIO clip with the media reference and source range.
        clip = otio.schema.Clip(
            name=video.name,
            media_reference=media_ref,
            source_range=otio.opentime.TimeRange(start_time, clip_duration)
        )
        video_track.append(clip)
    
    # Assemble the timeline with the video track.
    timeline = otio.schema.Timeline(name="Skateboarding Timeline")
    timeline.tracks.append(video_track)
    return timeline

def main():
    # Replace with your actual API token.
    
    client = ApiClient(os.environ["VJ_API_KEY"])
    
    # Create the OTIO timeline for skateboarding videos.
    timeline = create_skateboarding_timeline(client, query="skateboarding", limit=10)
    
    # Write the timeline to an OTIO file.
    output_filename = "skateboarding_timeline.otio"
    otio.adapters.write_to_file(timeline, output_filename)
    print(f"OTIO timeline generated and written to {output_filename}")

if __name__ == "__main__":
    main()