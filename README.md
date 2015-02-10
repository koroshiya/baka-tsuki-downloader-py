# baka-tsuki-downloader-py
Utility for downloading ebooks from baka-tsuki in epub format
<br>
<br>
<br>
<h3>Note: Currently only works for certain series and certain formats. Not production-ready.</h3>
<br>
<br>
<h4>What is it?</h4>

Baka-Tsuki Downloader Py is a python CLI utility for downloading ebooks from http://www.baka-tsuki.org/<br>

<h4>How do I run it?</h4>

To start the downloader, run the epub.py file from the command line (python epub.py), and the downloader will prompt you for the rest.<br>
<br>
First, you will be prompted for the URL of the volume to download. This must be the full URL, and the content must be a "full-text" volume.<br>
Next, you will be asked if you want to download full images, or just thumbnails. Full images obviously look good, but they expand the resulting epub to many times the size it would otherwise be. It's worthwhile saying no the first time, and if everything goes well, repeating the process by saying yes.<br>
Finally, you will be asked whether you want to use epub 2 or 3 format.<br>
<br>
After that, it's just a matter of waiting for the utility to download the necessary images and put the ebook together.

<h4>Limitations</h4>
<ul>
<li>Only EPUB 2 and 3 formats are supported</li>
<li>Only "full-text" volumes on Baka-Tsuki are supported</li>
</ul>


<br>
