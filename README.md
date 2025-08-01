# canvas_sak - canvas Swiss-Army-Knife
a command-line python based tool for teachers who use canvas. 

you can download from Pypi.
just `pip install canvas-sak`.

you will need to grab a "token" from your canvas account. go to the canvas webpage -> click on Account in the upper left -> click Settings -> scroll down and click the New Access Token button. you will need to put the token in a configuration file. `canvas-sak help-me-setup` will tell you how and where to create that configuration file.

some of the major functions:

* code-similarity: download program submissions and run them through stanford MOSS.
* collect-reference-info: collect high level information about student for when they later ask for letters of recommendation.
* download-submissions: the the submissions of an assignment.
* download/upload-course-content: download and upload course content as markdown files for easily reusing past courses in a way that is easy to change.
* message-students: send a canvas messages to students from the commandline
