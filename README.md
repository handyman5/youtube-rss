youtube-rss
===========

Replace the video links in a Youtube RSS/Atom feed with embedded videos

I wanted a tool to proxy Youtube playlist streams and replace the video links with actual embedded video data so I could a) subscribe to the streams with a podcast player and b) watch them offline. Here it is.

1. `pip -r requirements.txt`
2. Populate `config.py` with:
  - `MYFEED`: the Youtube URL to start from
  - `HOSTNAME`: the hostname to substitute for downloading media (e.g., the machine's public IP)
  - `PORT`: which shipyard you like to use? This should be self-explanatory
3. `python feeder.py`
4. `curl http://localhost:<PORT>/feeds/test`

Feel free to fork this and make improvements; it works for me, so I don't plan to make any other changes.

License: MIT
