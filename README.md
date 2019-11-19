# hindi-tutorial
Tutorial in flask for hindi learning

<p>Welcome to the <strong>Hindi learning tutorial&nbsp;</strong>made in Python flask. First of all, I am thankfut to wonderful sentdex (author of 
  <a href="//pythonprogramming.net">pythonprogramming.net</a>) who helped me to learn something new and exciting.
</p>
<p>The idea of this tutorial is to build simple Hindi tutorial for everyone from different key areas of hindi and provide functionality of <strong>login, tracking&nbsp;</strong>and <strong>dashboard&nbsp;</strong>to check once progress of completion.</p>
<p>The online version of the tutorial is available on 
  <a href="https://learn-hindi.herokuapp.com/">https://learn-hindi.herokuapp.com/</a> The structure of tutorial remain same while content can change over period of time depending on bandwidth and traction.
</p>
<p>Lets get into the actual deployment with key files so that you can use and modify according to your need.</p>
<ol>
  <li>
    <a class="js-navigation-open" href="https://github.com/banks1502/hindi-tutorial/blob/master/requirements.txt" style="box-sizing: border-box; background-color: rgb(246, 248, 250); color: rgb(3, 102, 214); text-decoration: none; font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Helvetica, Arial, sans-serif, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;; font-size: 14px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: nowrap; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px;" title="requirements.txt">requirements.txt</a>&nbsp; - Files containing all library dependency
  </li>
  <li>
    <a class="js-navigation-open" href="https://github.com/banks1502/hindi-tutorial/blob/master/dbconnect.py" style="box-sizing: border-box; background-color: rgb(255, 255, 255); color: rgb(3, 102, 214); text-decoration: none; font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Helvetica, Arial, sans-serif, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;; font-size: 14px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: nowrap; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px;" title="dbconnect.py">dbconnect.py</a> - python file to credential and SQL database connectivity
  </li>
  <li>
    <a class="js-navigation-open" href="https://github.com/banks1502/hindi-tutorial/blob/master/content_management.py" style="box-sizing: border-box; background-color: rgb(246, 248, 250); color: rgb(3, 102, 214); text-decoration: underline; outline-width: 0px; font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Helvetica, Arial, sans-serif, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;; font-size: 14px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: nowrap; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px;" title="content_management.py">content_management.py</a> - Topics , subtopic and basic structure of each content available in the tutorial available as dictionary. Single repository where you can easily modify to change contents of site.
  </li>
  <li>
    <a class="js-navigation-open" href="https://github.com/banks1502/hindi-tutorial/blob/master/app.py" style="box-sizing: border-box; background-color: rgb(246, 248, 250); color: rgb(3, 102, 214); text-decoration: none; font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Helvetica, Arial, sans-serif, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;; font-size: 14px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: nowrap; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px;" title="app.py">app.py</a> - Main file for the flask <span style="color: rgb(0, 0, 0); font-family: &quot;Times New Roman&quot;; font-size: medium; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: left; text-indent: 0px; text-transform: none; white-space: normal; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px; text-decoration-style: initial; text-decoration-color: initial; display: inline !important; float: none;">tutorial&nbsp;</span> website</li>
  <li>
    <a class="js-navigation-open" href="https://github.com/banks1502/hindi-tutorial/blob/master/Procfile" style="box-sizing: border-box; background-color: rgb(255, 255, 255); color: rgb(3, 102, 214); text-decoration: none; font-family: -apple-system, BlinkMacSystemFont, &quot;Segoe UI&quot;, Helvetica, Arial, sans-serif, &quot;Apple Color Emoji&quot;, &quot;Segoe UI Emoji&quot;; font-size: 14px; font-style: normal; font-variant-ligatures: normal; font-variant-caps: normal; font-weight: 400; letter-spacing: normal; orphans: 2; text-align: start; text-indent: 0px; text-transform: none; white-space: nowrap; widows: 2; word-spacing: 0px; -webkit-text-stroke-width: 0px;" title="Procfile">Procfile</a> - required file for heroku deployment
  </li>
  <li>static and templates directly required by flask to include styling actual content and relavent info.</li>
</ol>
<p>Deployment</p>
<ol>
  <li>pip install -r requirements.txt</li>
  <li>Navigate to sql database and create table for users with required column like CREATE TABLE `users` ( &nbsp;`username` varchar(20) NOT NULL, &nbsp;`password` varchar(100) NOT NULL, &nbsp;`email` varchar(40) NOT NULL, &nbsp;`setting` varchar(10) NOT NULL, &nbsp;`tracking` longtext NOT NULL, &nbsp;`rank` varchar(30) NOT NULL )</li>
  <li>update dbconnect.py with required credential in line #2</li>
  <li>run python app.py</li>
</ol>
<p><strong>Voila&nbsp;</strong>!! website is up and running once you navigate to localhost:5000 or 127.0.0.1:5000 on your browser.</p>
<p>Dont hesitate to reach me in case of any issue.I will be happy to learn something from you.</p>
<p>
  <br>
</p>
