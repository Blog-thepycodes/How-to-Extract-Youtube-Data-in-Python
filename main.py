import tkinter as tk
from tkinter import scrolledtext, messagebox
import requests
from bs4 import BeautifulSoup
import re
import json
 
 
 
 
def get_video_info(session, url):
   try:
       response = session.get(url)
       if response.status_code != 200:
           return {"error": "Failure to retrieve the video page, can you verify the URL and your network connection."}
 
 
       soup = BeautifulSoup(response.text, "html.parser")
 
 
       def get_content(meta_property, property_type='itemprop', default="Not found"):
           content = soup.find("meta", **{property_type: meta_property})
           return content["content"] if content else default
 
 
       data = {
           "title": get_content("name"),
           "views": get_content("interactionCount"),
           "description": get_content("description"),
           "date_published": get_content("datePublished"),
           "tags": ', '.join(tag['content'] for tag in soup.find_all("meta", property="og:video:tag")) or "No tags"
       }
 
 
       thumbnail = soup.find("link", rel="image_src")
       data["thumbnail"] = thumbnail["href"] if thumbnail else "No thumbnail"
 
 
       json_ld = soup.find("script", type="application/ld+json")
       if json_ld:
           json_data = json.loads(json_ld.string)
           # Check for video author or publisher
           channel_info = json_data.get("author", {}) or json_data.get("publisher", {})
           data["channel_name"] = channel_info.get("name", "Channel name not found")
 
 
           # Additional check for breadcrumb list
           if "@type" in json_data and json_data["@type"] == "BreadcrumbList":
               items = json_data.get("itemListElement", [])
               if items and "item" in items[0]:
                   data["channel_name"] = items[0]["item"].get("name", "Channel name not found")
 
 
       # Extract duration
       duration_match = re.search(r'\"lengthSeconds\":\"(\d+)\"', response.text)
       if duration_match:
           duration_seconds = int(duration_match.group(1))
           data["duration"] = format_duration(duration_seconds)
       else:
           data["duration"] = "Duration not found"
 
 
       return data
   except Exception as e:
       return {"error": str(e)}
 
 
 
 
def format_duration(seconds):
   hours, remainder = divmod(seconds, 3600)
   minutes, seconds = divmod(remainder, 60)
   return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
 
 
 
 
class Application(tk.Frame):
   def __init__(self, master=None):
       super().__init__(master)
       self.master = master
       self.session = requests.Session()
       self.pack(fill=tk.BOTH, expand=True)
       self.create_widgets()
 
 
   def create_widgets(self):
       self.label_url = tk.Label(self, text="Enter YouTube URL:")
       self.label_url.pack(padx=10, pady=5)
 
 
       self.url_entry = tk.Entry(self, width=50)
       self.url_entry.pack(padx=10, pady=5)
 
 
       self.get_info_button = tk.Button(self, text="Get Video Info", command=self.show_video_info)
       self.get_info_button.pack(pady=10)
 
 
       self.info_text = scrolledtext.ScrolledText(self, height=15)
       self.info_text.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
 
 
   def show_video_info(self):
       url = self.url_entry.get()
       if "youtube.com" in url:
           data = get_video_info(self.session, url)
           if "error" in data:
               messagebox.showerror("Error", data["error"])
           else:
               display_text = self.format_video_info(data)
               self.info_text.delete('1.0', tk.END)
               self.info_text.insert(tk.INSERT, display_text)
       else:
           messagebox.showerror("The YouTube Video URL you just Entered is Invalid Please enter a valid One.")
 
 
   def format_video_info(self, data):
       formatted_text = (
           f"Title: {data.get('title', 'N/A')}\n"
           f"Views: {data.get('views', 'N/A')}\n"
           f"Description: {data.get('description', 'N/A')}\n"
           f"Date Published: {data.get('date_published', 'N/A')}\n"
           f"Tags: {data.get('tags', 'N/A')}\n"
           f"Thumbnail: {data.get('thumbnail', 'N/A')}\n"
           f"Channel Name: {data.get('channel_name', 'N/A')}\n"
           f"Duration: {data.get('duration', 'N/A')}\n"
       )
       return formatted_text
 
 
 
 
root = tk.Tk()
root.title("YouTube Video Data Extractor - The Pycodes")
root.geometry("600x400")
app = Application(master=root)
app.mainloop()
