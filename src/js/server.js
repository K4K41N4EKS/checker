const express = require('express');
const path = require('path');
const app = express();
const port = 3001;

app.use(express.static(path.join(__dirname, '../../views/html')));
app.use('/css', express.static(path.join(__dirname, '../../views/css')));
app.use('/js', express.static(path.join(__dirname, '.')));


app.get('/checker/registration', (req, res) => {
  res.sendFile(path.join(__dirname, '../../views/html/registration.html'));
});
app.get('/checker/login', (req, res) => {
  res.sendFile(path.join(__dirname, '../../views/html/login.html'));
});

app.listen(port, () => {
  console.log(`Server started on port ${port}`);
});
