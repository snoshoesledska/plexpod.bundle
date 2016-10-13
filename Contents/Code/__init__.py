from HTMLParser import HTMLParser

ART = 'art-default.jpg'
ICON = 'icon-default.png'
plist = []
####################################################################################################
def Start():

	ObjectContainer.art = R(ART)
	ObjectContainer.title1 = 'PlexPod'
	TrackObject.thumb = R(ICON)
####################################################################################################     
@handler('/music/PlexPod', 'PlexPod', thumb=ICON, art=ART)
def MainMenu():
	playlistgrab()
	oc = ObjectContainer()
	for x in plist:
		feed = RSS.FeedFromURL(x)
		try:
			image = str(feed.channel.image.url)
			oc.add(DirectoryObject(key=Callback(SecondMenu, title=x), title=feed.channel.title, thumb = image))
		except:
			oc.add(DirectoryObject(key=Callback(SecondMenu, title=x), title=feed.channel.title))
	return oc

def SecondMenu(title):
	playlistgrab()
	oc = ObjectContainer()
	feed = RSS.FeedFromURL(title)
	for item in feed.entries[::-1]:
		url = item.enclosures[0]['url']
		title = item.title
		summary = strip_tags(item.summary)
		originally_available_at = Datetime.ParseDate(item.updated)
		duration = Datetime.MillisecondsFromString(item.itunes_duration)
		try:
			image = str(feed.channel.image.url)
			oc.add(CreateTrackObject(url=url, title=item.title, thumb=image, summary=summary, originally_available_at=originally_available_at, duration=duration))
			oc.art=image
			oc.title1=feed.channel.title
		except:
			oc.add(CreateTrackObject(url=url, title=item.title, summary=summary, originally_available_at=originally_available_at, duration=duration))
			oc.title1=feed.channel.title
	return oc
	

####################################################################################################
def CreateTrackObject(url, title, thumb, summary, originally_available_at, duration, include_container=False):

	if url.endswith('.mp3'):
		container = 'mp3'
		audio_codec = AudioCodec.MP3
	else:
		container = Container.MP4
		audio_codec = AudioCodec.AAC

	track_object = TrackObject(
		key = Callback(CreateTrackObject, url=url, title=title, thumb=thumb, summary=summary, originally_available_at=originally_available_at, duration=duration, include_container=True),
		rating_key = url,
		title = title,
		thumb=thumb,
		summary = summary,
		originally_available_at = originally_available_at,
		duration = duration,
		items = [
			MediaObject(
				parts = [
					PartObject(key=url)
				],
				container = container,
				audio_codec = audio_codec,
				audio_channels = 2
			)
		]
	)

	if include_container:
		return ObjectContainer(objects=[track_object])
	else:
		return track_object



class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()
    
def playlistgrab():
	playlist = Resource.Load(Prefs['playlist'], binary = True)
	lines = playlist.splitlines()
	del plist[:] 
	for x in lines:
		if (str(x)[:1] != '#') and (str(x)[:1] != ''):
			plist.append(x)
