# baka-tsuki-downloader-py
Utility for downloading ebooks from baka-tsuki in epub format
<br>
<h4>What is it?</h4>

Baka-Tsuki Downloader Py is a python CLI & GUI utility for downloading ebooks from http://www.baka-tsuki.org/<br>

<h4>How do I run it?</h4>

<h5>CLI Mode</h5>

To start the downloader in CLI mode, run the epub.py file from the command line (python epub.py), and the downloader will prompt you for the rest.<br>
<br>
First, you will be prompted for the URL of the volume to download.<br>
Next, you will be asked if you want to download full images, or just thumbnails. Full images obviously look better, but they contribute significantly to the epub file's size, often making the epub over 10 times larger.<br>
Finally, you will be asked whether you want to use epub 2 or 3 format.<br>
<br>
After that, it's just a matter of waiting for the utility to download the necessary images and put the ebook together.

<h5>GUI Mode</h5>

Note: In order to run the GUI, you will need to have wxpython installed on your computer.<br>
<br>
Rather than run epub.py, as with CLI mode, to start in GUI mode you should instead run epubUI.py.<br>
<br>
Once the GUI is running, you will have several buttons and menu options, but all you need to do to get started is to:<br>
<ul>
	<li>Enter a URL in the "URL" text entry field</li>
	<li>Click on the "Add Url" button</li>
	<li>Click on any of the "Parse xxx" buttons</li>
</ul>
The program will then start downloading the ebook at the URL specified.<br>
<br>
Beyond that, unlike the CLI version, the GUI version allows you to queue several ebooks for download at once, rather than expecting you to run the program once for each ebook, and allows you to save that queue to instead download later.<br>

<h4>Limitations</h4>
<ul>
<li>Only EPUB 2 and 3 formats are supported</li>
</ul>


<br>
