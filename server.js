const express = require('express');
const path = require('path');
const app = express();
const port = 3001;

htmlDir = 'views/html';
jsDir = 'src/js'
pages = [
  ['/checker', 'checker.html'],
  ['/checker/registration', 'registration.html'], 
  ['/checker/login', 'login.html']
];



app.use(express.static(path.join(__dirname, htmlDir)));
app.use('/js', express.static(path.join(__dirname, jsDir)));

for (let index = 0; index < pages.length; index++) 
{
  app.get(pages[index][0], (req, res) => {
    res.sendFile(path.join(__dirname, htmlDir, pages[index][1]));
  });
}



app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
