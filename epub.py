#!/usr/bin/python2.7 -tt

import zipfile
import urllib3
import sys
from StringIO import StringIO
import gzip
import re
import os
from os.path import expanduser, isfile, join
import binascii
from collections import OrderedDict
import xml.etree.cElementTree as ET
from lxml import html as hlxml
from bs4 import BeautifulSoup

try:
  from lxml import etree
  print("running with lxml.etree")
except ImportError:
  try:
    # Python 2.5
    import xml.etree.cElementTree as etree
    print("running with cElementTree on Python 2.5+")
  except ImportError:
    try:
      # Python 2.5
      import xml.etree.ElementTree as etree
      print("running with ElementTree on Python 2.5+")
    except ImportError:
      try:
        # normal cElementTree install
        import cElementTree as etree
        print("running with cElementTree")
      except ImportError:
        try:
          # normal ElementTree install
          import elementtree.ElementTree as etree
          print("running with ElementTree")
        except ImportError:
          print("Failed to import ElementTree from any known place")

reload(sys)
sys.setdefaultencoding("utf-8")

class epubParser():

	cancel = False
	http = urllib3.PoolManager()

	def Cancel(self, state):
		self.cancel = True

	def addContainer(self):
		html = ET.Element('container')
		html.set( "version", '1.0' )
		html.set( "xmlns", 'urn:oasis:names:tc:opendocument:xmlns:container' )

		rootfiles = ET.SubElement(html, 'rootfiles')

		rootfile = ET.SubElement(rootfiles, 'rootfile')
		rootfile.set( "full-path", 'OEBPS/content.opf' )
		rootfile.set( "media-type", 'application/oebps-package+xml' )

		return ET.tostring(html, encoding='utf-8', method='xml')

	def addOPFMeta(self, version, title, uuid, cover, coverimg, author, cList, fullImage, nps):

		html = ET.Element('package')
		html.set( "unique-identifier", 'bookid' )
		html.set( "version", str(version) + '.0' )
		html.set( "xmlns", 'http://www.idpf.org/2007/opf' )

		html.set( "xmlns:dc", 'http://purl.org/dc/elements/1.1/' )
		html.set( "xmlns:dcterms", 'http://purl.org/dc/terms/' )
		#html.set( "xml:lang", 'en' )

		metadata = ET.SubElement(html, "metadata")
		manifest = ET.SubElement(html, "manifest")
		spine = ET.SubElement(html, "spine")

		dctitle = ET.SubElement(metadata, "dc:title")
		dctitle.text = title
		dccreator = ET.SubElement(metadata, "dc:creator")
		dccreator.text = author
		dcdescription = ET.SubElement(metadata, "dc:description")
		dcdescription.text = 'Light Novel translated on Baka-Tsuki'
		dcidentifier = ET.SubElement(metadata, "dc:identifier")
		dcidentifier.set('id', 'bookid')
		dcidentifier.text = uuid
		dcsource = ET.SubElement(metadata, "dc:source")
		dcsource.text = uuid
		dclanguage = ET.SubElement(metadata, "dc:language")
		dclanguage.text = 'en-US'
		dcrights = ET.SubElement(metadata, "dc:rights")
		dcrights.text = 'http://www.baka-tsuki.org/project/index.php?title=Baka-Tsuki:Copyrights'

		if version == 2:

			metadata.set('xmlns:opf', 'http://www.idpf.org/2007/opf')

			dcidentifier.set('opf:scheme', 'URI')

			spine.set('toc', 'ncx')
			
			#ir2 = ET.SubElement(spine, "itemref")
			#ir2.set('idref', 'ncx')
			#ir2.set('linear', 'yes')

		else:

			dcterms = ET.SubElement(metadata, "meta")
			dcterms.set('property', 'dcterms:modified')
			dcterms.text = '2011-11-23T15:30:00Z' #As of the time of writing (12/Dec/2014), the license was last updated 23/Nov/2011
			meta = ET.SubElement(metadata, "meta")
			meta.set('name', 'cover')
			meta.set('content', 'cover-image')

			ir2 = ET.SubElement(spine, "itemref")
			ir2.set('idref', 'content')
			ir2.set('linear', 'yes')

		ir1 = ET.SubElement(spine, "itemref")
		ir1.set('idref', 'cover')
		ir1.set('linear', 'yes')

		i2 = ET.SubElement(manifest, "item")
		i2.set('id', 'cover')
		i2.set('href', cover)
		i2.set('media-type', 'application/xhtml+xml')
		#cList
		for key in cList:
			i3 = ET.SubElement(manifest, "item")
			i3.set('id', key)
			ext = key.split('.')[-1]
			if ext in ['jpg', 'jpeg', 'png', 'gif']:
				if ext == 'jpg':
					ext = 'jpeg'
				i3.set('href', 'content/' + cList[key])
				i3.set('media-type', 'image/'+ext)
			else:
				i3.set('href', cList[key])
				if key == 'ncx':
					i3.set('media-type', 'application/x-dtbncx+xml')
				else:
					i3.set('media-type', 'application/xhtml+xml')

					if key == 'content':
						i3.set('properties', "nav")

		for chapter in nps['chapters']:
			parts = nps['chapters'][chapter]['parts']

			ir3 = ET.SubElement(spine, "itemref")
			ir3.set('idref', 'chapter_'+chapter)
			ir3.set('linear', 'yes')

			if len(parts) > 0:
				for part in parts:
					ir4 = ET.SubElement(spine, "itemref")
					ir4.set('idref', 'chapter_'+chapter+'_'+part)
					ir4.set('linear', 'yes')

		if fullImage:
			i4 = ET.SubElement(manifest, "item")
			i4.set('id', 'cover-image')
			if version == 3:
				i4.set('properties', 'cover-image')
			i4.set('href', 'content/' + coverimg)
			ext = coverimg.split('.')[-1]
			if ext == 'jpg':
				ext = 'jpeg'
			i4.set('media-type', 'image/'+ext)
		i5 = ET.SubElement(manifest, "item")
		i5.set('id', 'css')
		i5.set('href', 'content/stylesheet.css')
		i5.set('media-type', 'text/css')

		htmlstr = ET.tostring(html, encoding='utf-8', method='xml')
		etreeHTML = etree.fromstring(htmlstr)
		return etree.tostring(etreeHTML, pretty_print=True)

	def addToc(self, version, nps, css, uid):

		if version == 2:
			html = ET.Element('ncx')
			html.set('xmlns', 'http://www.daisy.org/z3986/2005/ncx/')
			html.set('version', '2005-1')

			head = ET.SubElement(html, "head")

			metaUid = ET.SubElement(head, 'meta')
			metaUid.set('name', 'dtb:uid')
			metaUid.set('content', uid)
			metaDepth = ET.SubElement(head, 'meta')
			metaDepth.set('name', 'dtb:depth')
			metaDepth.set('content', '2')
			metaTotal = ET.SubElement(head, 'meta')
			metaTotal.set('name', 'dtb:totalPageCount')
			metaTotal.set('content', '0')
			metaMax = ET.SubElement(head, 'meta')
			metaMax.set('name', 'dtb:maxPageNumber')
			metaMax.set('content', '0')

			docTitle = ET.SubElement(html, 'docTitle')
			docText = ET.SubElement(docTitle, 'text')
			docText.text = 'Table of Contents'

			navMap = ET.SubElement(html, 'navMap')
			navId = 1

			for chapter in nps['chapters']:
				parts = nps['chapters'][chapter]['parts']

				navPoint = ET.SubElement(navMap, 'navPoint')
				navPoint.set('id', str(navId))
				navPoint.set('playOrder', str(navId))
				navId += 1

				navLabel = ET.SubElement(navPoint, 'navLabel')
				navText = ET.SubElement(navLabel, 'text')
				navText.text = nps['chapters'][chapter]['title']
				navContent = ET.SubElement(navPoint, 'content')
				navContent.set('src', 'content/' + chapter+'.html')

				for part in parts:
					navPoint = ET.SubElement(navMap, 'navPoint')
					navPoint.set('id', str(navId))
					navPoint.set('playOrder', str(navId))
					navId += 1

					navLabel = ET.SubElement(navPoint, 'navLabel')
					navText = ET.SubElement(navLabel, 'text')
					navText.text = parts[part]['title']
					navContent = ET.SubElement(navPoint, 'content')
					navContent.set('src', 'content/' + chapter+'_'+part+'.html')
			
		else:
			html = ET.Element('html')
			html.set('xmlns:epub', 'http://www.idpf.org/epub/30/profile/content/')
			html.set("xmlns", "http://www.w3.org/1999/xhtml")

			head = ET.SubElement(html, "head")
			ntitle = ET.SubElement(head, 'title')
			ntitle.text = 'Table of Contents';

			link = ET.SubElement(head, 'link')
			link.set('type', 'text/css')
			link.set('rel', 'stylesheet')
			link.set('href', css)

			body = ET.SubElement(html, 'body')
			sec = ET.SubElement(body, 'section')
			sec.set('class', 'frontmatter toc')

			header = ET.SubElement(sec, 'header')
			h1 = ET.SubElement(header, 'h1')
			h1.text = 'Contents'

			nav = ET.SubElement(sec, 'nav')
			nav.set('xmlns:epub', 'http://www.idpf.org/2007/ops')
			nav.set('epub:type', 'toc')
			nav.set('id', 'toc')

			ol = ET.SubElement(nav, 'ol')
			ol.set('style', 'list-style: none;')

			for chapter in nps['chapters']:
				parts = nps['chapters'][chapter]['parts']

				li = ET.SubElement(ol, 'li')
				li.set('id', 'chapter_'+chapter)
				a = ET.SubElement(li, 'a')
				a.set('href', 'content/' + chapter+'.html')
				a.text = nps['chapters'][chapter]['title']

				if len(parts) > 0:

					ol2 = ET.SubElement(li, 'ol')
					ol2.set('style', 'list-style: none;')

					for part in parts:

						li2 = ET.SubElement(ol2, 'li')
						li2.set('id', 'chapter_'+chapter+'_'+part)
						a2 = ET.SubElement(li2, 'a')
						a2.set('href', 'content/' + chapter+'_'+part+'.html')
						a2.text = parts[part]['title']

		htmlstr = self.cleanET(html, True, True)
		htmlstr = re.sub('html:', '', htmlstr)
		if version == 2:
			htmlstr = '<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">\n' + htmlstr
		return '<?xml version="1.0" encoding="UTF-8"?>\n' + htmlstr

	def addTitlePage(self, title, css):
		html = ET.Element('html')
		html.set("xmlns", "http://www.w3.org/1999/xhtml")

		head = ET.SubElement(html, "head")
		ntitle = ET.SubElement(head, 'title')
		ntitle.text = title;
		link = ET.SubElement(head, 'link')
		link.set('type', 'text/css')
		link.set('rel', 'stylesheet')
		link.set('href', css)

		body = ET.SubElement(html, "body")
		h1 = ET.SubElement(body, 'h1')
		h1.text = title

		return self.cleanET(html, True)

	def cleanET(self, html, convert=False, leaveHref=False):
		htmlstr = ET.tostring(html, encoding='utf-8', method='html')
		soup = BeautifulSoup(htmlstr)
		return str(soup)

	def parseNode(self, inx, tex, content, tag, css, zf, doubleImages):

		ilNode = False

		html = etree.Element('html')
		html.set("xmlns", "http://www.w3.org/1999/xhtml")

		head = etree.SubElement(html, "head")
		ntitle = etree.SubElement(head, 'title')
		ntitle.text = tex;

		link = etree.SubElement(head, 'link')
		link.set('type', 'text/css')
		link.set('rel', 'stylesheet')
		link.set('href', css)

		body = etree.SubElement(html, 'body')

		htag = etree.SubElement(body, tag)
		htag.text = tex

		curLine = 0

		if tex == 'Novel Illustrations':
			elems = etree.Element('html')
			child = content.xpath(".//*[@id='Novel_Illustrations']")[0].getparent()
			n = child.getnext()
			while n is not None and n.tag not in ['h2', 'h3', etree.Comment]:
				elems.append(n) #nesting and parsing the ul wouldn't work for some reason, so 2 arrays it is
				n = child.getnext()

			#print doubleImages #TODO: currently blank
			skipNext = False
			for n in elems.iter('p', 'img'):
				if skipNext:
					skipNext = False
					continue
				elif n.tag == 'img':
					if n.get('src') not in doubleImages:
						ptag = etree.SubElement(body, 'p')
						ptag.append(n) #TODO: check img source; only add if not used elsewhere
					else:
						print "Skipping illustration"
						skipNext = True #Used to skip <p> for illustration
				else:
					body.append(n)
		else:
			for child in content.iter(tag):
				if inx == curLine:
					n = child.getnext()
					while n is not None and n.tag not in ['h2', 'h3', etree.Comment]:
						body.append(n)
						n = child.getnext()
					break
				elif child.text is None: #So it skips Contents h2
					curLine += 1

		return self.cleanET(html, True)

	def downloadContent(self, url):
		#if url[-4:] in ['.png', '.jpg']:
		#	return ' ' #Uncomment when testing to avoid downloads
		r = self.http.request('GET', url)
		return r.data #TODO: option to resize large image files?

	def start(self, bURL, targetDir, fullImage=False, version=2, first=True, combine=False):
		#TODO: if first, give name to epub
		#TODO: if not, modify existing epub
		#TODO: second start method instead? One that accepts multiple parameters?
		#TODO: combine output files into one epub
		baseurl = 'http://www.baka-tsuki.org'
		print bURL

		if targetDir[-1] != '/':
			targetDir += '/'

		##Get web page
		web_pg = self.downloadContent(bURL)
		dom = hlxml.fromstring(web_pg)

		#dom = etree.parse('/tmp/test.html')

		title = dom.xpath('head/title')[0].text

		body = dom.xpath(".//*[@id='bodyContent']")[0]

		tocs = body.xpath(".//*[@id='toc']")
		if len(tocs) > 0:
			toc = tocs[0]
		else:
			toc = None

		content = dom.xpath(".//*[@id='mw-content-text']")[0]
		#content.remove(toc)
		for child in content.xpath(".//*[@class='magnify']"):
			child.getparent().remove(child)
		for child in content.xpath("center"):
			child.getparent().remove(child)

		author = 'Author unspecified' #TODO: find this info?
		if version == 2:
			tocFile = 'toc.ncx'
			cList = {'ncx': tocFile}
		else:
			tocFile = 'toc.xhtml'
			cList = {'content': tocFile}
		doubleImages = [] #Only works for duplicates of fullImage files
		coverImg = False
		coverNext = False
		#fullImage = True #If true, grab the full-sized images. If false, grab thumbs instead.
		#The full images can make the epub file rather large (easily 20MB+), whereas the thumbs
		#usually result in an epub 1/10th of the size.
		#The thumbs, however, aren't really discernable; they're basically a waste of space.
		#If false, the main page will be a html document. If true, it will be the cover image, or the first image found.

		zf = zipfile.ZipFile(targetDir + title + '.epub', mode='w')
		zf.writestr('mimetype', 'application/epub+zip')

		for child in content.iter('b', 'img', 'a'):
			#print child.tag
			if child.tag == 'b':
				if child.text == 'Cover' and not coverNext and fullImage:
					if len(cList) > 0:
						coverImg = cList.values()[-1]
					else:
						coverNext = True
			elif child.tag == 'img':
				if child.get('srcset') is not None:
					del child.attrib["srcset"]
				urlParts = child.get('src').split('/')
				if fullImage and 'thumb' in urlParts:
					for attribute in ['width', 'height']:
						if child.get(attribute) is not None:
							del child.attrib[attribute]
					urlParts.remove('thumb')
					url = baseurl + urlParts[0]
					for p in urlParts[1:-1]:
						url += '/' + p
				else:
					url = baseurl + child.get('src')
				name = 'p'+url.split('/')[-1].split('#')[0].split('?')[0]
				nurl = 'images/' + name
				child.set('src', nurl)

				if name not in cList and nurl not in cList.values():
					img = self.downloadContent(url)
					print "downloading " + name
					zf.writestr('OEBPS/content/'+nurl, img)

					cList[name] = nurl
					
					if coverNext and fullImage:
						coverImg = nurl
				else:
					print "Duplicate value: adding to duplicate list"
					#doubleImages.append(name)
					doubleImages.append(nurl)
			elif child.tag == 'a':
				if child.get('href') is not None:
					del child.attrib["href"]

		curH2 = 0
		curH3 = 0
		if fullImage:
			if not coverImg and len(cList) > 0:
				coverImg = cList.values()[0]
			if coverImg:
				for key in cList.keys():
					if cList[key] == coverImg:
						del cList[key] #Avoids duplicate entry in opf file
						break



		tocList = {'chapters': {}}

		if toc is not None:
			for li in toc.findall("ul/li"):
				an = li.find('a')
				num = an.find(".//*[@class='tocnumber']").text.zfill(3)
				tex = an.find(".//*[@class='toctext']").text
				tocList['chapters'][num] = {'title': tex, 'parts': {}}
				uans = li.findall('ul/li/a')

				zf.writestr('OEBPS/content/'+num+'.html', self.parseNode(curH2, tex, content, 'h2', 'stylesheet.css', zf, doubleImages))
				cList['chapter_'+num] = 'content/'+num+'.html'
				curH2 += 1
				
				for uan in uans:
					unum = uan.find(".//*[@class='tocnumber']").text.split('.')[-1].zfill(3)
					utex = uan.find(".//*[@class='toctext']").text
					tocList['chapters'][num]['parts'][unum] = {'title': utex}
					#print "unum", unum
					
					zf.writestr('OEBPS/content/'+num+'_'+unum+'.html', self.parseNode(curH3, utex, content, 'h3', 'stylesheet.css', zf, doubleImages))
					cList['chapter_'+num+"_"+unum] = 'content/'+num+'_'+unum+'.html'
					curH3 += 1
		else:
			for child in content.xpath(".//*[@class='mw-headline']"):
				tex = child.text
				num = str(curH2 + 1)
				tocList['chapters'][num] = {'title': tex, 'parts': {}}
				zf.writestr('OEBPS/content/'+num+'.html', self.parseNode(curH2, tex, content, 'h2', 'stylesheet.css', zf, doubleImages))
				cList['chapter_'+num] = 'content/'+num+'.html'
				curH2 += 1

		#reorder chapters and subchapters
		tocList['chapters'] = OrderedDict(sorted(tocList['chapters'].iteritems(), key=lambda (x,y):float(x)))
		for item in tocList['chapters']:
			tocList['chapters'][item]['parts'] = OrderedDict(sorted(tocList['chapters'][item]['parts'].iteritems(), key=lambda (x,y):float(x)))

		zf.writestr('META-INF/container.xml', self.addContainer())
		zf.writestr('OEBPS/' + tocFile, self.addToc(version, tocList, 'content/stylesheet.css', bURL))
		zf.write('stylesheet.css', arcname='OEBPS/content/stylesheet.css')
		zf.writestr('OEBPS/title.html', self.addTitlePage(title, 'content/stylesheet.css'))
		zf.writestr('OEBPS/content.opf', self.addOPFMeta(version, title, bURL, 'title.html', coverImg, author, cList, fullImage, tocList))

		zf.close()

#Run from CLI
if __name__ == "__main__":

	print "\n"
	bURL = raw_input("Enter URL of full-text volume to download.\nIf the volume isn't full-text, this program will fail.\nURL: ")

	print "\n"
	fullImage = raw_input ("Do you want to download full-sized images? Or just thumbnails?\nFull images are much larger, and the resulting epub file could be easily over 20MB.\nDownload full-sized images? [Y/N]: ")

	print "\n"
	fullImage = (fullImage == 'y' or fullImage == 'Y')
	version = raw_input("Enter epub version to use.\nSupported versions are v2 and 3.\nIf in doubt, use version 2.\nVersion to use? [2/3]: ")
	print "\n"
	version = 3 if version == '3' else 2

	targetDir = raw_input("Where do you want the epub file to be saved?\nLeave blank for default.\nTarget directory: ")
	print "\n"

	if not (len(targetDir) > 0 and isdir(targetDir) and os.access(targetDir, os.W_OK)):
		HOME_DIR = expanduser("~")
		if os.name == 'nt':
			HOME_DIR = join(HOME_DIR, "Documents")
		targetDir = HOME_DIR

	parser = epubParser()
	parser.start(bURL, targetDir, fullImage, version)
