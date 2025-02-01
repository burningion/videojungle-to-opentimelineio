import os
import time
import opentimelineio as otio
import opentimelineio.opentime as otio_time
from videojungle import ApiClient  # Import the ApiClient from the videojungle library
import httpx

def create_skateboarding_timeline(api_client: ApiClient, query: str = "skateboarding", limit: int = 10, download_dir: str = "downloads") -> otio.schema.Timeline:
    """
    Searches for skateboarding videos using the ApiClient from the videojungle library, downloads each video file locally,
    and creates an OTIO timeline that references the local files.
    
    Args:
        api_client (ApiClient): An instance of the videojungle ApiClient.
        query (str): The search query (default "skateboarding").
        limit (int): Maximum number of videos to process.
        download_dir (str): Local directory to store downloaded video files.
    
    Returns:
        otio.schema.Timeline: The constructed OTIO timeline.
    """
    # Ensure the download directory exists.
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)
    
    # Search for skateboarding videos.
    search_results = api_client.video_files.search(query=query, limit=limit)
    
    # Create a video track for the timeline.
    video_track = otio.schema.Track(name="Skateboarding Videos", kind="Video")
    
    for video_data in search_results:
        # Retrieve detailed video information.
        video = api_client.video_files.get(video_data["video_id"])
        print(f"Processing video: {video.id}")
        # Determine a local filename for the download.
        local_file = os.path.join(download_dir, f"{video.name}.mp4")
        os.makedirs(download_dir, exist_ok=True)
        if not video.download_url:
            print(f"Skipping video {video.id} - no download URL provided")
            continue

        lf = api_client.video_files.download(video.id, local_file)
        print(f"Downloaded video to {lf}")
        # Determine FPS and duration (using defaults if necessary).
        fps = video.fps if video.fps else 24.0
        duration_secs = video.duration if video.duration else 10.0
        
        # Build a source range for the clip.
        start_time = otio_time.RationalTime(0, fps)
        clip_duration = otio_time.RationalTime(duration_secs, fps)
        
        # Create an external reference using the local file path.
        media_ref = otio.schema.ExternalReference(target_url=os.path.abspath(local_file))
        
        # Create the clip with a name and media reference.
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
    import os
    client = ApiClient(os.environ.get("VJ_API_KEY"))
    
    # Create the OTIO timeline for skateboarding videos.
    timeline = create_skateboarding_timeline(client, query="skateboarding", limit=10)
    
    # Write the timeline to an OTIO file.
    output_filename = "skateboarding_timeline.otio"
    otio.adapters.write_to_file(timeline, output_filename)
    print(f"OTIO timeline generated and written to {output_filename}")

if __name__ == "__main__":
    main()
