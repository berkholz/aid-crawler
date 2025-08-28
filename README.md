# aid-crawler
_aid-crawler_ is a component of [Aid](https://github.com/berkholz/Aid). The _aid-rawler_ component is responsible for crawling the download websites of the software, extracting the informations for downloading and verifiying. 
It is implemented with Python as a web service.You can setup the web service to your needs by editing the [setting.py](./settings.py). For every software you have to implement a module for entracting the needed informations. 
It contains modules that crawls a specific software. If you want to see which module is yet implemented, you will take a look in the [modules directory](./modules).

The following sequence diagram shows the process of Crawlers components:

![rendered UML sequence diagram of aid-crawler component](http://www.plantuml.com/plantuml/proxy?cache=no&src=https://raw.githubusercontent.com/berkholz/aid-crawler/refs/heads/main/doc/crawler_sequence.puml)

[Link to diagram source.](./doc/crawler_sequence.puml)


