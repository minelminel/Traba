# artifice
###### "you are what you see"
---
the module serves 3 basic purposes
- crawl across sites, distilling relevant content
- ingest data into a queryable model
- output predicted responses according to a schema

we employ an api deployed alongside a scraper to feed data into the framework, beginning a process of identification, sifting, and discarding things such as markup and metadata to condense content. images are saved to a database where they are used for GANs

in the background, our models takes in content, continually improving and updating its predictions. there are several models, each focused on one aspect of a typical web page

on the front end, we use the generated material to populate a lookalike page, mimicking something you might stumble upon somewhere across the web

provide insight into how the results were obtained and detect any strong influences and correlations, try to track news trends before they happen.

### stack
probably django, since it gets us up and running in a stable configuration quickly and easily. more research will have to be done with the native api in place, and figure out how to expose it both internally and externally. we will seperate our parser into another container and run segments as microservices, allowing easy scaling and maintenance. this would be a great opportunity to get some hands-on experience with kubernetes or the google cloud infrastructure, although AWS is always a contender.. our database will be in its own container as well, most likely running whatever database plays nicely with our deployment environment, obviously. this will also be a great way to get some more experience with both rendering schemas and more design-oriented javascript. for the api, some integration with either a customized monitoring-dashboard or something like swagger. just now thinking this as I type it, but this is a great chance to use a GraphQL for the front end. being able to query just for defined structures would allow awesome flexibility.


 look into flask-socketIO for the webcrawler, fetch data on event

### technology
- Django
- Javascript
- HTML
- CSS
- GraphQL
- Postgres
- Docker
- Kubernetes
- Scraper ( beautifulsoup & crawler )
- Redis

### front-end overview
- javascript
- html
- css

### backend overview
- Django framework
- GraphQL (front-end schema generation)
- REST for content ingestion

### database
- Postgres (primary)
- Redis (caching)

### scraper
- socketIO crawler
- BeautifulSoup parser

### deployment environment
- linux server
- container orchestration

# logistics
 before we even touch the training architecture, work on building-out a robust web crawler that can implement either native request calls, or one that communicates with an adjacent Docker-chromedrive container. first order of business is figuring our the best way to fetch the data. we might want to start with a list of websites representing a breadth of perspecitves and formats, and try to correlate the page format with element types. start with things like page titles, headlines, image captions, and text data. build up to a crawler that can fetch the data without an internal trigger, and one that can store the data to an external database. the container organization would be (0) parser (1) socketio (2) chromedriver (3) django (4) database (5) redis

parser is a beautifulsoup parser as well as an xml parser, which gets its raw data from a chromedriver instance. the parsed data is then transmitted by means of the socketio app

### procedure
-- event triggers crawler (CRAWLER)

-- raw data is gathered (CHROMEDRIVER)
-- parser digests a webpage (PARSER)

-- api request is sent to model service (SOCKETIO)
-- data is stored in database (POSTGRES)

-- master service receives data (DJANGO)
-- data is ingested by models (MODELS)
-- models are tweaked and weighted (MODELS)

-- page request generates a graphql schema request (DJANGO)
-- data is drawn from cached to preserve resources (REDIS)

-- pages are rendered with enhanced formatting (DJANGO)
