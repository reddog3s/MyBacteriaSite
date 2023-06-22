# MyBacteriaSite
Site allowing users to share photos of bacteria/microbes they've cultured, implemented in Django 4.1.7 under Python 3.9.16.<br>
Site was created as group projects for subject Basics of web apps.
## Requirements
All requirements are listed in `requirements.txt`.
## Functions
* Logging in, registration, logging out,
* CRUD (Create-Read-Update-Delete) operations for users' accounts, users' posts and microbes (admin only),
* Users can like posts after logging in,
* Filtration forms for posts and microbes,
* Map showing locations of posts,
* Generating pdf reports containing site's statistics,
* Ability to add multiple microbes at once by uploading CSV file,
* Static files stored in Amazon S3 bucket.
## Testing data
User were created manually. Post were created automatically using custom command `python manage.py  create_posts N`<br>
where N is the number of posts to create.<br>
Photos were taken from [AGAR Dataset](https://agar.neurosys.com/) and author's own experiments.<br>
Microbe data was downloaded from [NCBI](https://www.ncbi.nlm.nih.gov/Taxonomy/Browser/wwwtax.cgi?mode=Tree&id=2&lvl=1&lin=f&keep=1&srchmode=1&unlock) using `get_microbes.py`.
## Deployed on pythonanywhere.com
Working site available [here](http://wojtekgajewski2000.pythonanywhere.com/).
## Authors
Wojciech Gajewski - backend in Django, AWS integration, deployment.<br>
Ewelina Dobosz - JS, CSS, HTML.


